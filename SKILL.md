---
name: chalkpress
description: 把备考/课程视频转成可打印、可检索的讲义 PDF：关键帧成页 + 字幕随页 + agent 撰写学习笔记。适合考研、研究生课程、软考法考等专业考试场景。Turn exam-prep/lecture videos into printable, searchable handout PDFs (keyframe pages, aligned subtitles, agent-written study notes). 触发词：讲义、视频转PDF、网课笔记、考研、备考、课程视频、handout、video to pdf。
---

# Chalkpress：讲座视频 → 讲义 PDF

确定性 Python 管线负责转录、关键帧、对齐、排版；**你（宿主 agent）负责两件 LLM 工作：校对字幕、写图文摘要**。管线零 API 调用，不需要任何 API key。

## 依赖安装（按需）

先确定本次转换需要哪些能力，再装对应依赖组（在技能目录内执行）：

| 场景 | 安装 |
|---|---|
| 任何转换（必装 base） | `uv pip install -e <技能目录>` |
| 视频无现成 SRT，需要转录 | `…install -e '<技能目录>[asr]'`（Apple 芯片可换 `[mac]` 加速） |
| 中文视频（繁简规范/术语修正） | `…install -e '<技能目录>[zh]'` |
| 用户已有 SRT | 无需 asr/mac 组，`--reuse-srt` 跳过转录 |

无 pip/uv 时用 `python3 -m pip`。whisper 模型（数百 MB）在首次真实转录时自动下载，huggingface.co 不可达会自动切国内镜像；已有 SRT 时完全零下载。缺依赖时管线报错信息里写明该装哪组。

## 工作流

### 1. 转录（管线）

```bash
chalkpress transcribe 视频.mp4            # 已有 SRT：加 --reuse-srt 字幕.srt
# 中文课程可加 --language zh --term-fix（软考类课程强烈建议 --term-fix）
```

产出讲义目录 `<视频名>_讲义/`：草稿 `<视频名>.srt`、`keyframes/`（讲义页图）、`manifest.json`。

### 2. 校对字幕（你来做）

读草稿 SRT，修正同音字/误听/标点（如「二叉数」→「二叉树」）。**只改文本，绝不动时间轴**。`--term-fix` 已做拼音级确定性修正，你处理语义级错误。编辑后原位保存为同名 `.srt`。

### 3. 构建（管线）

```bash
chalkpress build 视频.mp4
```

产出 `<视频名>.aligned.md`（字幕×关键帧对照，图片相对链接可读）与 `<视频名>.pdf`。此阶段不需要 ffmpeg，随时可重跑。

### 4. 写摘要（你来做）

读 `aligned.md` 与 `keyframes/*.jpg`（图片可直接看），写 `<视频名>.summary.md`：概述 → 分节要点（引用对应关键帧图片 `keyframes/xx.jpg`）→ 图表解读。用户语言与视频语言一致。

### 5.（可选）摘要嵌入 PDF 首页

```bash
chalkpress build 视频.mp4 --summary <视频名>.summary.md
```

## 约定与边界

- **一次一个视频**：没有批量模式，多视频逐个走完整流程，单个失败不影响后续。
- 输出语言/风格由你在摘要与校对时决定；PDF 框架标签固定为中文。
- 全程本地处理，不上传任何数据。
- 完整流程示例：`transcribe`（几分钟，取决于时长与后端）→ 你校对 → `build`（秒级）→ 你写摘要。
- 报错含义：`未找到 manifest.json`＝跳过了第 1 步；`未安装 faster-whisper`＝缺 `[asr]` 依赖组；`检测到中文字幕但未安装 opencc`＝缺 `[zh]` 依赖组。
