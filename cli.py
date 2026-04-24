import argparse
import json
from pathlib import Path

from clc_classifier import CLCAutoClassifier, DEFAULT_JSON_PATH


def read_text(args) -> str:
    if args.text:
        return args.text
    if args.file:
        path = Path(args.file)
        if not path.exists():
            raise FileNotFoundError(f"文件不存在：{path}")
        return path.read_text(encoding=args.encoding, errors="ignore")
    raise ValueError("请使用 --text 输入文本，或使用 --file 指定文献文件。")


def main() -> None:
    parser = argparse.ArgumentParser(description="中图分类法科技文献自动分类工具 CLI")
    parser.add_argument("--mode", choices=["zh", "en", "domain"], required=True, help="分类模式：zh 中文、en 英文、domain 专业领域")
    parser.add_argument("--text", default="", help="待分类文本")
    parser.add_argument("--file", default="", help="待分类文件路径，建议 txt/md/json")
    parser.add_argument("--encoding", default="utf-8", help="读取文件编码，默认 utf-8")
    parser.add_argument("--domain-hint", default="", help="专业领域提示，仅 domain 模式必填或建议填写")
    parser.add_argument("--json-path", default=DEFAULT_JSON_PATH, help="完整版中图分类法 JSON 路径")
    parser.add_argument("--model", default=None, help="智谱模型名称，默认读取 ZHIPU_MODEL 或 glm-4-flash")
    parser.add_argument("--top-k", type=int, default=80, help="本地候选召回数量")
    args = parser.parse_args()

    text = read_text(args)
    classifier = CLCAutoClassifier(json_path=args.json_path, model=args.model, top_k=args.top_k)

    if args.mode == "zh":
        result = classifier.classify_chinese(text)
    elif args.mode == "en":
        result = classifier.classify_english(text)
    else:
        result = classifier.classify_domain(text, domain_hint=args.domain_hint)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
