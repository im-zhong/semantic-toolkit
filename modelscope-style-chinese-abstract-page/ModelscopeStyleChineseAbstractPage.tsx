export default function ModelscopeStyleChineseAbstractPage() {
  const exampleInput = `近年来，随着科研文献数量的快速增长，研究人员面临信息过载和知识获取效率低下的问题。现有文献分析方法大多侧重于关键词提取或主题分类，难以准确揭示科技文献中不同句子的语义功能。为解决这一问题，本文提出一种基于本地部署大语言模型和提示词工程的科技文献语步识别方法，用于自动识别摘要中的研究背景、研究目的、研究方法、研究结果和研究结论。该方法首先对输入摘要进行句子切分，然后结合面向学术文本设计的提示模板，引导模型对每个句子的语义角色进行判定，并通过规则约束对输出结果进行结构化整理。实验选取1200篇中英文科技论文摘要作为测试数据，与传统机器学习方法和通用文本分类模型进行对比。结果表明，本文方法在语步识别任务上的整体准确率达到91.3%，Macro-F1达到0.89。研究表明，基于本地大模型的提示词工程方法能够有效提升科技文献语义分析的自动化水平。`;

  const resultData = [
    {
      title: "研究背景",
      key: "background",
      items: [
        "近年来，随着科研文献数量的快速增长，研究人员面临信息过载和知识获取效率低下的问题。",
        "现有文献分析方法大多侧重于关键词提取或主题分类，难以准确揭示科技文献中不同句子的语义功能。",
      ],
    },
    {
      title: "研究目的",
      key: "purpose",
      items: [
        "为解决这一问题，本文提出一种基于本地部署大语言模型和提示词工程的科技文献语步识别方法，用于自动识别摘要中的研究背景、研究目的、研究方法、研究结果和研究结论。",
      ],
    },
    {
      title: "研究方法",
      key: "method",
      items: [
        "该方法首先对输入摘要进行句子切分，然后结合面向学术文本设计的提示模板，引导模型对每个句子的语义角色进行判定，并通过规则约束对输出结果进行结构化整理。",
      ],
    },
    {
      title: "研究结果",
      key: "result",
      items: [
        "实验选取1200篇中英文科技论文摘要作为测试数据，与传统机器学习方法和通用文本分类模型进行对比。结果表明，本文方法在语步识别任务上的整体准确率达到91.3%，Macro-F1达到0.89。",
      ],
    },
    {
      title: "研究结论",
      key: "conclusion",
      items: [
        "研究表明，基于本地大模型的提示词工程方法能够有效提升科技文献语义分析的自动化水平。",
      ],
    },
  ];

  const apiRequest = `POST /api/move-recognition/chinese-abstract`;
  const requestJson = `{
  "text": "这里是一段中文科技论文摘要文本"
}`;
  const responseJson = `{
  "code": 200,
  "message": "success",
  "data": {
    "background": ["..."],
    "purpose": ["..."],
    "method": ["..."],
    "result": ["..."],
    "conclusion": ["..."]
  }
}`;
  const pythonCode = `import requests\n\nurl = "http://localhost:8000/api/move-recognition/chinese-abstract"\nheaders = {\n    "Content-Type": "application/json",\n    "Authorization": "Bearer your_access_token"\n}\npayload = {\n    "text": "这里是一段中文科技论文摘要文本"\n}\nresp = requests.post(url, json=payload, headers=headers)\nprint(resp.json())`;

  return (
    <div className="min-h-screen bg-[#f7f9fc] text-slate-800">
      <header className="sticky top-0 z-40 border-b border-slate-200 bg-white/95 backdrop-blur">
        <div className="mx-auto flex h-16 max-w-[1400px] items-center justify-between px-6">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[linear-gradient(135deg,#5fa8ff_0%,#3b82ff_38%,#1f5fff_100%)] text-sm font-bold text-white shadow-lg shadow-blue-200/50">语</div>
            <div>
              <div className="text-sm font-semibold text-slate-900">语义计算工具库</div>
              <div className="text-xs text-slate-500">面向系统研发人员的语义能力平台</div>
            </div>
          </div>

          <div className="hidden flex-1 px-10 lg:block">
            <div className="mx-auto flex max-w-[560px] items-center rounded-full border border-slate-200 bg-slate-50 px-4 py-2.5">
              <svg viewBox="0 0 24 24" className="mr-2 h-4 w-4 text-slate-400" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="11" cy="11" r="7" />
                <path d="m20 20-3.5-3.5" />
              </svg>
              <input
                className="w-full bg-transparent text-sm outline-none placeholder:text-slate-400"
                placeholder="搜索工具、能力、API、文档"
              />
            </div>
          </div>

          <div className="flex items-center gap-3 text-sm">
            <button className="rounded-lg px-3 py-2 text-slate-600 hover:bg-slate-100">文档中心</button>
            <button className="rounded-lg px-3 py-2 text-slate-600 hover:bg-slate-100">API 管理</button>
            <button className="rounded-lg bg-[linear-gradient(135deg,#5fa8ff_0%,#3b82ff_38%,#1f5fff_100%)] px-4 py-2 font-medium text-white shadow-sm">在线体验</button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-[1400px] space-y-6 px-6 py-6">
        <section className="overflow-hidden rounded-[28px] border border-slate-200 bg-white shadow-sm">
          <div className="grid gap-0 lg:grid-cols-[1.3fr_0.7fr]">
            <div className="relative bg-[radial-gradient(circle_at_top_left,_rgba(255,255,255,0.18),_transparent_30%),linear-gradient(135deg,#5fa8ff_0%,#3b82ff_38%,#1f5fff_100%)] p-8 text-white">
              <div className="mb-4 flex flex-wrap gap-2 text-xs">
                <span className="rounded-full border border-white/25 bg-white/14 px-3 py-1">语步识别</span>
                <span className="rounded-full border border-white/25 bg-white/14 px-3 py-1">中文摘要</span>
                <span className="rounded-full border border-white/25 bg-white/14 px-3 py-1">API 可接入</span>
              </div>
              <h1 className="text-4xl font-bold leading-tight">中文摘要语步识别</h1>
              <p className="mt-4 max-w-3xl text-base leading-7 text-white/90">
                面向系统研发人员与平台接入场景，对中文科技论文摘要进行结构化语步识别，自动抽取研究背景、研究目的、研究方法、研究结果与研究结论，支持在线测试与标准 API 集成。
              </p>
              <div className="mt-8 flex flex-wrap gap-3">
                <button className="rounded-xl bg-white px-5 py-3 text-sm font-semibold text-[#2f73ff] shadow-sm">立即体验</button>
                <button className="rounded-xl border border-white/25 bg-white/14 px-5 py-3 text-sm font-semibold text-white">查看 API 文档</button>
              </div>
              <div className="mt-7 grid max-w-2xl grid-cols-3 gap-3">
                {[
                  ["输入对象", "中文科技论文摘要"],
                  ["输出结构", "五类语步 JSON"],
                  ["接入方式", "RESTful API"],
                ].map(([k, v]) => (
                  <div key={k} className="rounded-2xl border border-white/25 bg-white/14 p-4 backdrop-blur-sm">
                    <div className="text-xs text-white/80">{k}</div>
                    <div className="mt-2 text-sm font-medium text-white">{v}</div>
                  </div>
                ))}
              </div>
            </div>

            <div className="p-6">
              <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                <div className="text-sm font-semibold text-slate-900">能力摘要</div>
                <div className="mt-4 space-y-3 text-sm text-slate-600">
                  <div className="flex items-start gap-3">
                    <span className="mt-1 h-2 w-2 rounded-full bg-[#2f73ff]" />
                    <p>支持单段摘要文本输入，适用于研发联调与平台能力验证。</p>
                  </div>
                  <div className="flex items-start gap-3">
                    <span className="mt-1 h-2 w-2 rounded-full bg-[#2f73ff]" />
                    <p>统一输出五类语步字段，适合被其他项目直接调用和消费。</p>
                  </div>
                  <div className="flex items-start gap-3">
                    <span className="mt-1 h-2 w-2 rounded-full bg-[#2f73ff]" />
                    <p>页面内置在线体验、返回预览、请求示例与 Python 调用代码。</p>
                  </div>
                </div>
              </div>

              <div className="mt-4 rounded-2xl border border-slate-200 bg-white p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm font-semibold text-slate-900">快速接入</div>
                    <div className="mt-1 text-xs text-slate-500">统一对外业务接口</div>
                  </div>
                  <span className="rounded-full bg-blue-50 px-3 py-1 text-xs text-[#2f73ff]">POST</span>
                </div>
                <div className="mt-4 rounded-xl bg-slate-950 px-4 py-3 font-mono text-xs text-slate-100">
                  {apiRequest}
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="grid gap-6 lg:grid-cols-[1.08fr_0.92fr]">
          <div className="rounded-[24px] border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-5 flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-slate-900">在线体验</h2>
                <p className="mt-1 text-sm text-slate-500">输入摘要并查看结构化语步识别结果</p>
              </div>
              <span className="rounded-full bg-emerald-50 px-3 py-1 text-sm text-emerald-700">在线可用</span>
            </div>

            <label className="mb-2 block text-sm font-medium text-slate-700">摘要内容</label>
            <textarea
              defaultValue={exampleInput}
              className="h-[300px] w-full rounded-2xl border border-slate-200 bg-slate-50 px-5 py-4 text-sm leading-7 text-slate-700 outline-none transition placeholder:text-slate-400 focus:border-[#1677ff] focus:bg-white"
              placeholder="请输入中文科技论文摘要文本"
            />
            <div className="mt-8 flex flex-wrap gap-3">
              <button className="rounded-xl bg-[linear-gradient(135deg,#5fa8ff_0%,#3b82ff_38%,#1f5fff_100%)] px-5 py-3 text-sm font-semibold text-white shadow-sm">开始识别</button>
              <button className="rounded-xl border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-slate-700">填入示例</button>
              <button className="rounded-xl border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-slate-700">清空内容</button>
            </div>
          </div>

          <div className="rounded-[24px] border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-5 flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-slate-900">输出预览</h2>
                <p className="mt-1 text-sm text-slate-500">统一 JSON 结构，便于第三方系统消费</p>
              </div>
              <button className="rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-600">复制响应</button>
            </div>

            <div className="space-y-3">
              {resultData.map((block) => (
                <div key={block.key} className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                  <div className="mb-2 flex items-center justify-between">
                    <div className="text-sm font-semibold text-slate-900">{block.title}</div>
                    <span className="rounded-full bg-white px-2.5 py-1 text-xs text-slate-500">{block.key}</span>
                  </div>
                  <div className="space-y-1.5 text-sm leading-6 text-slate-600">
                    {block.items.map((item, idx) => (
                      <div key={idx} className="rounded-xl bg-white px-3 py-2 text-[13px]">{item}</div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="rounded-[24px] border border-slate-200 bg-white p-6 shadow-sm">
          <div className="mb-6 flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-slate-900">API 接入演示</h2>
              <p className="mt-1 text-sm text-slate-500">展示的是语义计算工具库对外业务接口，不暴露底层模型实现</p>
            </div>
            <span className="rounded-full bg-blue-50 px-3 py-1 text-sm text-[#2f73ff]">开发者文档</span>
          </div>

          <div className="grid gap-5 lg:grid-cols-[0.95fr_1.05fr]">
            <div className="space-y-5">
              <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                <div className="mb-3 text-sm font-semibold text-slate-900">请求信息</div>
                <div className="grid gap-3 md:grid-cols-2">
                  {[
                    ["接口名称", "中文摘要语步识别"],
                    ["请求路径", "/api/move-recognition/chinese-abstract"],
                    ["请求方式", "POST"],
                    ["鉴权方式", "Bearer Token"],
                  ].map(([k, v]) => (
                    <div key={k} className="rounded-xl bg-white p-4">
                      <div className="text-xs text-slate-500">{k}</div>
                      <div className="mt-2 break-all text-sm font-medium text-slate-800">{v}</div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="rounded-2xl border border-slate-200 bg-slate-950 p-4 text-xs text-slate-100">
                <div className="mb-3 text-slate-400">请求体 JSON</div>
                <pre className="whitespace-pre-wrap leading-6">{requestJson}</pre>
              </div>

              <div className="rounded-2xl border border-slate-200 bg-slate-950 p-4 text-xs text-slate-100">
                <div className="mb-3 text-slate-400">返回体 JSON</div>
                <pre className="whitespace-pre-wrap leading-6">{responseJson}</pre>
              </div>
            </div>

            <div className="space-y-5">
              <div className="rounded-2xl border border-slate-200 bg-slate-950 p-4 text-xs text-slate-100">
                <div className="mb-3 text-slate-400">Python 调用示例</div>
                <pre className="whitespace-pre-wrap leading-6">{pythonCode}</pre>
              </div>

              <div className="rounded-2xl border border-slate-200 bg-[linear-gradient(180deg,#f8fbff_0%,#f2f7ff_100%)] p-4">
                <div className="text-sm font-semibold text-slate-900">接入建议</div>
                <div className="mt-4 space-y-3 text-sm leading-7 text-slate-600">
                  <p>1. 业务系统仅需调用统一业务接口，无需关注底层模型选型与提示词细节。</p>
                  <p>2. 返回结构固定为 background / purpose / method / result / conclusion，适合前端展示与结构化存储。</p>
                  <p>3. 建议通过服务端完成鉴权与日志记录，便于后续接口治理与能力审计。</p>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
