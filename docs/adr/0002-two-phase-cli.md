# 两段子命令：transcribe / build

旧管线单命令按 ASR → 校对 → 简繁 → 关键帧 → 对齐 → LLM 总结 → PDF 顺序一跑到底。LLM 移交宿主 agent 后（ADR-0001），管线无法自己校对，而校对必须落在排版**之前**——单命令跑到底意味着 PDF 永远包含未校对文本。因此拆成两段：`chalkpress transcribe`（视频 → 草稿 SRT + keyframes/ + manifest.json，唯一持有 ffmpeg 的阶段）与 `chalkpress build`（SRT × 关键帧 → aligned.md + PDF，纯 Python，可在任何装了 pillow/reportlab 的环境重跑）。SRT 是两阶段唯一交接格式，agent 只改文本不动时间轴；`--summary` 可把 agent 写好的摘要嵌入 PDF 首页。备选方案——单命令加旗标两态（`--no-pdf`/`--reuse-srt` 组合语义绕，第一遍仍会浪费排版）、一次跑完事后校对（PDF 质量受损）——均否决。

## Consequences

- manifest.json 成为两阶段唯一结构化交接物：帧时间戳、时长、检测语言、简繁脚本都由 transcribe 落盘，build 不重新探测场景。
- build 阶段缺失 manifest / SRT 时必须报出指向 transcribe 的明确错误（有测试钉住）。
- 多视频没有批量模式：批量 = 宿主 agent 逐个循环，单个失败不影响后续。
