from __future__ import annotations

import json
import os
import re
import math
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from dotenv import load_dotenv


SCI_TECH_PREFIXES = set("NOPQRSTUVX")
DEFAULT_JSON_PATH = "data/完整版中国图书馆图书分类法.json"

MODE_LABELS = {
    "zh": "中文科技文献分类",
    "chinese": "中文科技文献分类",
    "en": "英文科技文献分类",
    "english": "英文科技文献分类",
    "domain": "专业领域科技文献分类",
}

# 给本地召回补充中英文领域词，解决英文文献直接检索中文类名时召回弱的问题。
# 这些词只用于“候选召回加权”，最终分类仍由智谱模型在候选类目中重排决定。
DOMAIN_KEYWORDS: Dict[str, str] = {
    "N": "自然科学 general science natural science scientific research system science",
    "O": "数学 物理 化学 力学 数理科学 algebra geometry calculus statistics probability physics chemistry quantum mechanics optics thermodynamics polymer catalyst",
    "P": "天文学 地球科学 地理 地质 气象 海洋 遥感 astronomy geology geography meteorology ocean remote sensing GIS earthquake climate",
    "Q": "生物科学 生命科学 细胞 基因 蛋白 微生物 植物 动物 生态 biology life science cell gene protein microbiology plant animal ecology biodiversity",
    "R": "医学 卫生 临床 药物 疾病 诊断 治疗 护理 流行病 medicine medical healthcare clinical disease diagnosis therapy drug nursing epidemiology",
    "S": "农业 林业 畜牧 水产 作物 土壤 植保 农机 agriculture forestry crop soil livestock fishery plant protection rural",
    "T": "工业技术 工程 计算机 自动化 机械 电子 通信 材料 建筑 化工 能源 engineering technology computer automation machinery electronics communication material architecture chemical energy",
    "TP": "计算机 人工智能 机器学习 深度学习 数据挖掘 图像处理 自然语言处理 知识图谱 软件 数据库 网络安全 computer AI artificial intelligence machine learning deep learning data mining image processing NLP software database cybersecurity",
    "TN": "电子 通信 信号 雷达 半导体 集成电路 无线通信 5G 物联网 electronics communication signal radar semiconductor integrated circuit wireless 5G IoT",
    "TM": "电工 电机 电力系统 电网 新能源 储能 electrical power system grid motor renewable energy battery energy storage",
    "TH": "机械 仪器仪表 机器人 传感器 manufacturing machinery instrument robot sensor mechanical design",
    "TG": "金属 材料 冶金 焊接 铸造 metallurgy metal material welding casting",
    "TU": "建筑 城市规划 土木工程 结构工程 BIM construction architecture urban planning civil engineering structural engineering BIM",
    "U": "交通运输 铁路 公路 航运 汽车 traffic transportation railway highway shipping vehicle logistics",
    "V": "航空 航天 飞行器 火箭 卫星 aerospace aviation aircraft rocket satellite spacecraft",
    "X": "环境科学 安全科学 污染治理 碳排放 生态修复 environmental science safety pollution carbon emission ecological restoration",
}

DOMAIN_BOOST_RULES: List[Tuple[str, Sequence[str], float]] = [
    ("TP", ["人工智能", "机器学习", "深度学习", "神经网络", "大模型", "自然语言处理", "图像识别", "知识图谱", "ai", "machine learning", "deep learning", "neural", "nlp", "computer vision", "large language model"], 0.14),
    ("TN", ["通信", "无线", "5g", "6g", "雷达", "信号", "半导体", "集成电路", "芯片", "iot", "wireless", "radar", "semiconductor", "chip"], 0.12),
    ("R", ["医学", "临床", "疾病", "诊断", "治疗", "药物", "医院", "患者", "medical", "clinical", "disease", "diagnosis", "therapy", "drug", "patient"], 0.12),
    ("Q", ["基因", "细胞", "蛋白", "微生物", "生态", "生物", "gene", "cell", "protein", "biology", "microbial", "ecology"], 0.11),
    ("S", ["农业", "作物", "土壤", "农田", "病虫害", "水稻", "小麦", "玉米", "agriculture", "crop", "soil", "rice", "wheat", "maize"], 0.11),
    ("X", ["环境", "污染", "废水", "废气", "碳排放", "生态修复", "安全风险", "environment", "pollution", "wastewater", "carbon emission", "safety"], 0.11),
    ("P", ["遥感", "地理", "地质", "气象", "海洋", "地震", "remote sensing", "geology", "meteorology", "ocean", "earthquake", "gis"], 0.10),
    ("TU", ["建筑", "土木", "结构工程", "城市规划", "bim", "construction", "architecture", "civil engineering"], 0.10),
    ("V", ["航空", "航天", "飞行器", "卫星", "火箭", "aerospace", "aircraft", "satellite", "rocket"], 0.10),
    ("U", ["交通", "运输", "铁路", "公路", "物流", "车辆", "traffic", "transportation", "railway", "vehicle", "logistics"], 0.10),
]

GENERIC_RETRIEVAL_STOP_TOKENS = {
    "研究", "方法", "系统", "基于", "自动", "检测", "自动检测", "模型", "算法", "技术", "应用",
    "设计", "实现", "优化", "分析", "评价", "试验", "实验", "处理", "文献", "一种", "提出",
    "构建", "开发", "分类", "识别方法", "检测方法", "研究方法"
}

QUERY_EXPANSION_RULES: List[Tuple[Sequence[str], str]] = [
    (["医学影像", "影像诊断", "medical imaging", "ct", "mri"], "影像诊断学 临床医学 诊断学 R445 核磁共振成像 电子计算机体层扫描"),
    (["肺结节", "肺癌", "lung nodule", "lung cancer"], "呼吸系统疾病 肺疾病 肿瘤 内科学 R56 R734"),
    (["深度学习", "机器学习", "神经网络", "deep learning", "machine learning", "neural network"], "人工智能 机器学习 模式识别 计算机应用 TP18 TP391"),
    (["自然语言处理", "文本分类", "知识图谱", "nlp", "knowledge graph"], "人工智能 自然语言处理 信息处理 计算机应用 TP391 TP18"),
    (["遥感", "remote sensing", "gis"], "遥感技术 测绘学 地理信息系统 P2 P237 TP7"),
    (["作物", "水稻", "小麦", "玉米", "病虫害", "crop", "rice", "wheat", "maize"], "农作物 作物病虫害 农业科学 植物保护 S4 S43"),
    (["土壤", "施肥", "肥料", "soil", "fertilizer"], "土壤学 肥料学 农业基础科学 S15 S14"),
    (["污水", "废水", "污染", "碳排放", "wastewater", "pollution", "carbon emission"], "环境污染治理 环境工程 环境科学 X5 X7"),
    (["建筑", "混凝土", "结构工程", "bim", "construction", "concrete"], "建筑科学 土木工程 建筑结构 TU"),
    (["通信", "无线", "5g", "6g", "雷达", "semiconductor", "wireless"], "通信技术 无线通信 雷达 电子技术 TN"),
]


def normalize_clc_id(raw_id: Any) -> str:
    """去掉 JSON 中可能存在的 []、{} 等辅助符号，保留可展示的分类号。"""
    text = str(raw_id or "").strip()
    text = re.sub(r"^[\[\{]+", "", text)
    text = re.sub(r"[\]\}]+$", "", text)
    return text.strip()


def top_letter(clc_id: str) -> str:
    match = re.search(r"[A-Z]", normalize_clc_id(clc_id).upper())
    return match.group(0) if match else ""


def clamp(value: Any, low: float = 0.0, high: float = 1.0, default: float = 0.5) -> float:
    try:
        v = float(value)
    except Exception:
        v = default
    return max(low, min(high, v))


def truncate_text(text: str, max_chars: int = 6000) -> str:
    text = (text or "").strip()
    if len(text) <= max_chars:
        return text
    head = text[: int(max_chars * 0.7)]
    tail = text[-int(max_chars * 0.3) :]
    return head + "\n\n……【中间内容已截断】……\n\n" + tail


@dataclass(frozen=True)
class Category:
    id: str
    original_id: str
    name: str
    path_ids: Tuple[str, ...]
    path_names: Tuple[str, ...]
    top: str
    depth: int
    is_leaf: bool

    @property
    def path(self) -> str:
        return " > ".join(f"{cid} {name}" for cid, name in zip(self.path_ids, self.path_names))

    def retrieval_text(self) -> str:
        path_text = " ".join(self.path_names)
        id_text = " ".join(self.path_ids)
        extra = best_domain_keywords(self.id)
        return f"{self.id} {self.name} {path_text} {id_text} {extra}"


@dataclass
class Candidate:
    category: Category
    score: float

    def to_prompt_dict(self) -> Dict[str, Any]:
        return {
            "id": self.category.id,
            "name": self.category.name,
            "path": self.category.path,
            "local_score": round(float(self.score), 4),
        }

    def to_result_dict(self) -> Dict[str, Any]:
        return {
            "id": self.category.id,
            "name": self.category.name,
            "path": self.category.path,
            "local_score": round(float(self.score), 4),
        }


def best_domain_keywords(clc_id: str) -> str:
    cid = normalize_clc_id(clc_id).upper()
    matched = ""
    for prefix, words in DOMAIN_KEYWORDS.items():
        if cid.startswith(prefix.upper()) and len(prefix) > len(matched):
            matched = prefix
    if matched:
        return DOMAIN_KEYWORDS[matched]
    top = top_letter(cid)
    return DOMAIN_KEYWORDS.get(top, "")


class CategoryStore:
    """加载、展开、过滤中图分类法类目。"""

    def __init__(
        self,
        json_path: str | Path = DEFAULT_JSON_PATH,
        scitech_only: bool = True,
        min_scitech_categories: int = 2105,
    ) -> None:
        self.json_path = Path(json_path)
        self.scitech_only = scitech_only
        self.min_scitech_categories = min_scitech_categories
        self.categories = self._load_categories()

        if self.scitech_only and len(self.categories) < self.min_scitech_categories:
            raise ValueError(
                f"科学技术类目只加载到 {len(self.categories)} 个，少于要求的 "
                f"{self.min_scitech_categories} 个。请确认 JSON 路径是否为完整版：{self.json_path}"
            )

        self.by_id: Dict[str, Category] = {}
        for item in self.categories:
            # 若有重复分类号，保留第一次出现的完整路径。
            self.by_id.setdefault(item.id, item)

    def _load_json(self) -> Any:
        if not self.json_path.exists():
            raise FileNotFoundError(
                f"未找到分类法 JSON：{self.json_path}\n"
                f"请把你上传的“完整版中国图书馆图书分类法.json”放到 data/ 目录。"
            )
        with self.json_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _load_categories(self) -> List[Category]:
        data = self._load_json()
        if not isinstance(data, list):
            raise ValueError("分类法 JSON 顶层应为 list，每个节点包含 id、desc、children。")

        all_categories: List[Category] = []

        def walk(nodes: Iterable[Dict[str, Any]], parent_ids: Tuple[str, ...], parent_names: Tuple[str, ...]) -> None:
            for node in nodes:
                raw_id = str(node.get("id", "")).strip()
                cid = normalize_clc_id(raw_id)
                name = str(node.get("desc", "")).strip()
                if not cid or not name:
                    continue

                children = node.get("children") or []
                path_ids = parent_ids + (cid,)
                path_names = parent_names + (name,)
                cat = Category(
                    id=cid,
                    original_id=raw_id,
                    name=name,
                    path_ids=path_ids,
                    path_names=path_names,
                    top=top_letter(cid),
                    depth=len(path_ids),
                    is_leaf=not bool(children),
                )

                if (not self.scitech_only) or (cat.top in SCI_TECH_PREFIXES):
                    all_categories.append(cat)

                if isinstance(children, list):
                    walk(children, path_ids, path_names)

        walk(data, tuple(), tuple())
        return all_categories

    def get(self, category_id: str) -> Optional[Category]:
        return self.by_id.get(normalize_clc_id(category_id))

    def count(self) -> int:
        return len(self.categories)



def tokenize_for_retrieval(text: str) -> List[str]:
    """轻量级中英文分词，不依赖 sklearn/jieba，便于 Windows 直接运行。"""
    text = (text or "").lower()
    # 先从查询/类目文本中移除过于泛化的科研表达，降低“自动检测/方法/系统”等词误导分类的概率。
    for stop in sorted(GENERIC_RETRIEVAL_STOP_TOKENS, key=len, reverse=True):
        text = text.replace(stop, " ")
    tokens: List[str] = []

    # 英文、数字、分类号等
    tokens.extend(re.findall(r"[a-z0-9][a-z0-9_\-+.#/]*", text))

    # 中文连续片段做 2~4 字符 gram，适合类目短文本匹配
    for seq in re.findall(r"[\u4e00-\u9fff]+", text):
        if len(seq) <= 6:
            tokens.append(seq)
        for n in (2, 3, 4):
            if len(seq) >= n:
                tokens.extend(seq[i : i + n] for i in range(len(seq) - n + 1))

    # 分类号单独标准化
    for cid in re.findall(r"[a-z]\d+(?:[./]\d+)?", text, flags=re.I):
        tokens.append(normalize_clc_id(cid).lower())

    return [t for t in tokens if len(t.strip()) >= 2 and t not in GENERIC_RETRIEVAL_STOP_TOKENS]


class TfidfCandidateRetriever:
    """本地粗召回：BM25 候选召回，不依赖重型向量库。"""

    def __init__(self, store: CategoryStore) -> None:
        self.store = store
        self.corpus = [cat.retrieval_text() for cat in self.store.categories]
        self.postings: Dict[str, List[Tuple[int, int]]] = defaultdict(list)
        self.doc_len: List[int] = []
        self.doc_freq: Dict[str, int] = {}
        self.avg_doc_len = 1.0
        self._build_index()

    def _build_index(self) -> None:
        doc_freq_counter: Counter[str] = Counter()
        total_len = 0

        for idx, doc in enumerate(self.corpus):
            counts = Counter(tokenize_for_retrieval(doc))
            length = sum(counts.values()) or 1
            self.doc_len.append(length)
            total_len += length

            for token, tf in counts.items():
                self.postings[token].append((idx, int(tf)))
                doc_freq_counter[token] += 1

        self.doc_freq = dict(doc_freq_counter)
        self.avg_doc_len = total_len / max(len(self.doc_len), 1)

    def search(self, query: str, top_k: int = 80) -> List[Candidate]:
        query = (query or "").strip()
        if not query:
            raise ValueError("待分类文本不能为空。")

        query_counts = Counter(tokenize_for_retrieval(query))
        if not query_counts:
            raise ValueError("待分类文本没有可用于检索的关键词。")

        scores: Dict[int, float] = defaultdict(float)
        n_docs = len(self.store.categories)
        k1 = 1.5
        b = 0.75

        for token, qtf in query_counts.items():
            posting = self.postings.get(token)
            if not posting:
                continue

            df = self.doc_freq.get(token, 0)
            idf = math.log(1 + (n_docs - df + 0.5) / (df + 0.5))

            for idx, tf in posting:
                dl = self.doc_len[idx]
                denom = tf + k1 * (1 - b + b * dl / self.avg_doc_len)
                bm25 = idf * (tf * (k1 + 1) / denom)
                scores[idx] += bm25 * (1.0 + min(qtf, 5) * 0.05)

        # 如果没有命中，退化为按大类关键词召回，避免空结果。
        if not scores:
            for idx, cat in enumerate(self.store.categories):
                scores[idx] = self._domain_boost(query, cat)

        boosted: List[Tuple[int, float]] = []
        for idx, score in scores.items():
            cat = self.store.categories[int(idx)]
            final_score = float(score)
            final_score += self._domain_boost(query, cat)
            final_score += self._leaf_boost(cat)
            boosted.append((int(idx), final_score))

        boosted.sort(key=lambda x: x[1], reverse=True)

        result: List[Candidate] = []
        seen = set()
        for idx, score in boosted:
            cat = self.store.categories[idx]
            if cat.id in seen:
                continue
            seen.add(cat.id)
            # 分数做一个温和归一化，便于展示，不影响排序
            display_score = score / (score + 10.0) if score > 0 else 0.0
            result.append(Candidate(category=cat, score=display_score))
            if len(result) >= top_k:
                break

        return result

    @staticmethod
    def _leaf_boost(cat: Category) -> float:
        # 细分类优先一点，避免总是落到 N/O/T 这种大类。
        if cat.is_leaf:
            return 0.30
        if cat.depth >= 4:
            return 0.15
        return 0.0

    @staticmethod
    def _domain_boost(query: str, cat: Category) -> float:
        q = query.lower()
        cid = cat.id.upper()
        boost = 0.0
        for prefix, keywords, weight in DOMAIN_BOOST_RULES:
            if cid.startswith(prefix.upper()):
                matches = sum(1 for k in keywords if k.lower() in q)
                if matches:
                    boost += weight * 45 * min(matches, 4)
        return boost


class ZhipuClient:
    """智谱 GLM 调用封装。API Key 只从环境变量读取，不写入代码。"""

    def __init__(self, model: Optional[str] = None) -> None:
        load_dotenv()
        api_key = os.getenv("ZHIPUAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "未检测到环境变量 ZHIPUAI_API_KEY。\n"
                "请在 .env 文件或系统环境变量中配置：ZHIPUAI_API_KEY=你的智谱APIKey"
            )

        from zhipuai import ZhipuAI

        self.model = model or os.getenv("ZHIPU_MODEL", "glm-4-flash")
        self.client = ZhipuAI(api_key=api_key)

    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.05) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
        )
        return response.choices[0].message.content

    def chat_json(self, messages: List[Dict[str, str]], temperature: float = 0.05) -> Dict[str, Any]:
        text = self.chat(messages=messages, temperature=temperature)
        return parse_json_from_llm(text)


def parse_json_from_llm(text: str) -> Dict[str, Any]:
    """兼容模型返回 ```json ... ``` 或前后带解释文字的情况。"""
    raw = (text or "").strip()

    block = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.S | re.I)
    if block:
        raw = block.group(1)
    else:
        start = raw.find("{")
        end = raw.rfind("}")
        if start >= 0 and end > start:
            raw = raw[start : end + 1]

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"智谱模型未返回合法 JSON：{e}\n原始返回：\n{text}") from e



def expand_query_by_rules(text: str) -> str:
    lower = (text or "").lower()
    additions: List[str] = []
    for triggers, expansion in QUERY_EXPANSION_RULES:
        if any(str(t).lower() in lower for t in triggers):
            additions.append(expansion)
    if additions:
        return text + "\n" + "\n".join(additions)
    return text

class CLCAutoClassifier:
    """自动分类工具主服务：中文、英文、专业领域三个入口相互独立。"""

    def __init__(
        self,
        json_path: str | Path = DEFAULT_JSON_PATH,
        model: Optional[str] = None,
        top_k: int = 80,
        prompt_candidate_k: int = 35,
    ) -> None:
        self.store = CategoryStore(json_path=json_path, scitech_only=True, min_scitech_categories=2105)
        self.retriever = TfidfCandidateRetriever(self.store)
        self.llm = ZhipuClient(model=model)
        self.top_k = top_k
        self.prompt_candidate_k = prompt_candidate_k

    def classify_chinese(self, text: str) -> Dict[str, Any]:
        return self.classify(text=text, mode="zh")

    def classify_english(self, text: str) -> Dict[str, Any]:
        return self.classify(text=text, mode="en")

    def classify_domain(self, text: str, domain_hint: str = "") -> Dict[str, Any]:
        return self.classify(text=text, mode="domain", domain_hint=domain_hint)

    def classify(self, text: str, mode: str = "zh", domain_hint: str = "") -> Dict[str, Any]:
        mode = mode.lower().strip()
        if mode not in MODE_LABELS:
            raise ValueError(f"mode 只能是 {list(MODE_LABELS.keys())}，当前为：{mode}")

        original_text = truncate_text(text, max_chars=6000)
        if not original_text:
            raise ValueError("待分类文本不能为空。")

        retrieval_query = self._build_retrieval_query(original_text, mode=mode, domain_hint=domain_hint)
        candidates = self.retriever.search(retrieval_query, top_k=self.top_k)
        prompt_candidates = candidates[: self.prompt_candidate_k]

        result = self._llm_rerank(
            text=original_text,
            mode=mode,
            domain_hint=domain_hint,
            candidates=prompt_candidates,
        )
        result = self._sanitize_result(result, prompt_candidates)

        return {
            "tool": "自动分类工具",
            "mode": MODE_LABELS[mode],
            "model": self.llm.model,
            "category_source": str(self.store.json_path),
            "loaded_scitech_categories": self.store.count(),
            "candidate_count": len(candidates),
            "result": result,
            "local_top_candidates": [c.to_result_dict() for c in candidates[:10]],
        }

    def _build_retrieval_query(self, text: str, mode: str, domain_hint: str) -> str:
        """为英文/专业领域文本生成中文关键词，增强候选召回。"""
        query = text
        if domain_hint:
            query = f"专业领域：{domain_hint}\n{query}"

        query = expand_query_by_rules(query)

        # 中文模式通常不需要额外调用；英文和专业领域先让模型转成中文关键词，提升召回准确率。
        if mode not in {"en", "english", "domain"}:
            return query

        try:
            messages = [
                {
                    "role": "system",
                    "content": (
                        "你是科技文献关键词抽取助手。请把输入文献摘要提炼为中文检索词，"
                        "用于匹配《中国图书馆分类法》科学技术类目。只返回 JSON。"
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "请输出 JSON：\n"
                        "{"
                        '"translated_summary":"一句中文摘要",'
                        '"keywords_cn":["中文关键词1","中文关键词2"],'
                        '"discipline_terms":["学科方向1","学科方向2"]'
                        "}\n\n"
                        f"领域提示：{domain_hint or '无'}\n"
                        f"文献文本：\n{text}"
                    ),
                },
            ]
            data = self.llm.chat_json(messages, temperature=0.02)
            parts = [
                query,
                str(data.get("translated_summary", "")),
                " ".join(map(str, data.get("keywords_cn", []) or [])),
                " ".join(map(str, data.get("discipline_terms", []) or [])),
            ]
            return "\n".join(p for p in parts if p.strip())
        except Exception:
            # 关键词扩展失败时不中断，仍用原文 + 领域提示召回。
            return query

    def _llm_rerank(
        self,
        text: str,
        mode: str,
        domain_hint: str,
        candidates: List[Candidate],
    ) -> Dict[str, Any]:
        candidate_json = json.dumps(
            [c.to_prompt_dict() for c in candidates],
            ensure_ascii=False,
            indent=2,
        )
        system_prompt = (
            "你是严格的《中国图书馆分类法》中科技文献自动分类专家。"
            "你的任务是根据文献片段，从候选类目中选择最合适的分类号。"
            "注意：只能使用候选类目列表中出现的 id，不能编造分类号。"
            "若文献明显跨学科，需要给出多个备选分类号。"
            "输出必须是合法 JSON，不要输出 Markdown。"
        )
        user_prompt = f"""
分类模式：{MODE_LABELS[mode]}
专业领域提示：{domain_hint or "无"}

待分类科技文献文本：
{text}

候选中图分类法科技类目：
{candidate_json}

请严格返回如下 JSON 结构：
{{
  "language_detected": "zh/en/mixed",
  "is_interdisciplinary": true,
  "primary": {{
    "id": "候选类目中的分类号",
    "name": "类目名称",
    "path": "完整路径",
    "confidence": 0.0,
    "reason": "为什么这是主分类，控制在80字以内"
  }},
  "alternatives": [
    {{
      "id": "候选类目中的分类号",
      "name": "类目名称",
      "path": "完整路径",
      "confidence": 0.0,
      "reason": "作为备选的原因，控制在60字以内"
    }}
  ],
  "keywords": ["关键词1", "关键词2", "关键词3"],
  "user_selection_note": "给用户的选择建议，说明何时选主类、何时选备选类"
}}

置信度规则：
- 0.85~1.00：主题非常明确，分类号高度匹配。
- 0.70~0.84：主题明确，但存在相邻类目可能。
- 0.50~0.69：交叉学科或文本信息不足，建议人工确认。
- 低于0.50：不确定，只能作为候选建议。
""".strip()

        return self.llm.chat_json(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.03,
        )

    def _sanitize_result(self, result: Dict[str, Any], candidates: List[Candidate]) -> Dict[str, Any]:
        allowed = {c.category.id: c.category for c in candidates}
        fallback = candidates[0].category

        primary = result.get("primary") or {}
        primary_id = normalize_clc_id(primary.get("id"))
        if primary_id not in allowed:
            primary_id = fallback.id

        primary_cat = allowed[primary_id]
        clean_primary = {
            "id": primary_cat.id,
            "name": primary_cat.name,
            "path": primary_cat.path,
            "confidence": clamp(primary.get("confidence"), default=0.62),
            "reason": str(primary.get("reason") or "模型返回的主分类号不在候选集中，已回退为本地召回最高类目。")[:120],
        }

        alternatives = []
        seen = {primary_id}
        raw_alts = result.get("alternatives") or []
        if not isinstance(raw_alts, list):
            raw_alts = []

        for alt in raw_alts:
            aid = normalize_clc_id((alt or {}).get("id"))
            if aid in allowed and aid not in seen:
                cat = allowed[aid]
                alternatives.append(
                    {
                        "id": cat.id,
                        "name": cat.name,
                        "path": cat.path,
                        "confidence": clamp((alt or {}).get("confidence"), default=0.55),
                        "reason": str((alt or {}).get("reason") or "可作为交叉学科备选。")[:100],
                    }
                )
                seen.add(aid)

        # 至少补足 3 个备选，方便用户自行选择。
        for c in candidates:
            if len(alternatives) >= 5:
                break
            if c.category.id not in seen:
                alternatives.append(
                    {
                        "id": c.category.id,
                        "name": c.category.name,
                        "path": c.category.path,
                        "confidence": round(clamp(c.score, default=0.5), 4),
                        "reason": "本地候选召回结果，可供人工复核。",
                    }
                )
                seen.add(c.category.id)

        keywords = result.get("keywords") or []
        if not isinstance(keywords, list):
            keywords = [str(keywords)]

        return {
            "language_detected": result.get("language_detected", "unknown"),
            "is_interdisciplinary": bool(result.get("is_interdisciplinary", len(alternatives) > 1)),
            "primary": clean_primary,
            "alternatives": alternatives,
            "keywords": [str(k) for k in keywords[:10]],
            "user_selection_note": str(
                result.get("user_selection_note")
                or "主分类用于默认归档；若文献同时强调方法、对象和应用场景，可从备选分类号中人工选择。"
            )[:200],
        }
