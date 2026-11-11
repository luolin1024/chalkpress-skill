<div align="center">

<img src="docs/imgs/logo.png" alt="Chalkpress" width="128"/>

# Chalkpress

**一句话，让 AI Agent 把课程视频变成讲义 PDF**

考研网课、研究生课程、软考法考等专业考试视频：30 分钟的课 → 5 分钟读完，全程本地，零 API Key。

[![CI](https://github.com/luolin1024/chalkpress-skill/actions/workflows/ci.yml/badge.svg)](https://github.com/luolin1024/chalkpress-skill/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/luolin1024/chalkpress-skill)](https://github.com/luolin1024/chalkpress-skill/releases)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](pyproject.toml)
[![Stars](https://img.shields.io/github/stars/luolin1024/chalkpress-skill?style=social)](https://github.com/luolin1024/chalkpress-skill/stargazers)

[快速开始](#-快速开始) · [工作原理](#-工作原理) · [效果](#-效果) · [隐私](#-隐私) · [常见问题](#-常见问题) · [English](./README.en.md)

</div>

---

## 为什么

备考最痛的不是「看课」，是**回头找**：强化班几十讲，错题对应的知识点在哪一讲全靠记忆，进度条拖到怀疑人生。Chalkpress 把一门课**压缩成一册讲义**——阅读从此可以跳读、搜读、打印读：

| 场景 | 看视频 | 读讲义 |
|------|--------|--------|
| 第一轮抓框架 | 30 分钟线性播放，重点在哪只能等 | **约 5 分钟**：翻关键帧页扫读，先抓框架再补细节 |
| 错题回源 | 拖进度条靠记忆，来回试 | 关键词全文检索，**秒级定位到页** |
| 冲刺只补薄弱章节 | 几乎只能重看整讲 | 只翻对应几页；需要听语气，按页内时间戳回看那 1~2 分钟 |
| 打印背诵 | 不可能 | 一页一个知识画面，直接打印随身背 |

> 讲义不是替代看课，而是把「看完」和「找到 / 背住」解耦：通读交给阅读，回看交给时间戳。

## 🚀 快速开始

把这句话发给你的 AI Agent（workbuddy / ChatGPT / Claude Code 等，能执行命令即可）：

> **用这个技能把我的网课视频转成讲义：https://github.com/luolin1024/chalkpress-skill**

Agent 会按 [SKILL.md](SKILL.md) 自己完成剩下的一切：下载技能 → 按需装依赖 → 转录 → **校对字幕** → 生成 PDF → **写学习笔记**。你只需要告诉它视频文件在哪。校对和写笔记这两步由 agent 用自己的智能完成——**不需要任何 API Key，没有任何额外配置**。

## 🧠 工作原理

确定性 Python 管线负责一切机械工作，LLM 判断力由你的 agent 提供——职责单向、边界干净：

```mermaid
graph LR
    A[🎬 视频] --> T[transcribe<br>转录 + 关键帧]
    T --> D[草稿 SRT]
    D --> P[🤖 你的 agent<br>校对字幕]
    P --> B[build<br>对齐 + PDF]
    B --> H[📄 讲义目录]
    H --> S[🤖 你的 agent<br>学习笔记 summary.md]
```

一次转换的交付物：

| 你得到 | 说明 |
|--------|------|
| `<视频名>.pdf` | 每页一个关键帧画面 + 该时间窗的字幕（可选笔记首页），**文字层可检索可复制** |
| `<视频名>.srt` | 全片字幕（校对后），可独立导入播放器 |
| `<视频名>.aligned.md` | 字幕 × 关键帧对照表（内嵌画面，直接阅读） |
| `<视频名>.summary.md` | agent 撰写的结构化学习笔记（可选） |
| `keyframes/` | 讲义页原图，随时复用 |
| `manifest.json` | 帧时间戳与时长——build 不依赖 ffmpeg，**可在任何环境重跑** |

## 🖼️ 效果

**AI 学习笔记** —— agent 自动提炼出带星级权重的考点结构（作为 PDF 可选首页）：

![AI 学习笔记：考情分析](docs/imgs/summary-page.png)

## ✨ 特性

| | 特性 | 说明 |
|---|------|------|
| 🎯 | **关键帧成页** | 场景检测驱动抽帧：内容变化才截页，不是机械等间隔 |
| 📝 | **字幕随页** | Whisper 本地转写，字幕对齐到所在画面的时间窗 |
| 🤖 | **Agent 原生** | 校对与笔记交给你的 agent 完成——零 API Key、零外呼 |
| 🧩 | **术语包即数据** | 专业考试同音字误听确定性修正（坚偶校验 → 奇偶校验、生存数 → 生成树）；内置软考包 241 条，新领域只需加一个 JSON |
| 🔒 | **全程本地** | 转写、抽帧、排版全在你机器上，管线零网络调用 |
| 🖨️ | **可检索 PDF** | 横版 A4，画面为图、字幕为真实文字层；中文不缺字 |

## 🆚 与常见工具的区别

| | Chalkpress | 剪映 / 飞书妙记 | 通用转写工具 |
|---|-----------|---------------|-------------|
| 产出形态 | **讲义 PDF**（画面+字幕同页） | 转文字稿 | 纯文字 |
| 可打印可检索 | ✅ 文字层 PDF | ❌ | ❌ |
| 结构化学习笔记 | ✅ agent 撰写 | ❌ | ❌ |
| 复习方式 | 搜关键词定位到页 | 在长文字稿里翻找 | 翻找 |
| 视频上传 | **永不上传** | 需上传云端 | 视本地实现 |
| API Key | **不需要** | 平台账号 | 多数需要 |

## 🔒 隐私

视频**始终不上传**——转写、抽帧、排版全程在你机器上完成，管线自身零网络调用（whisper 模型首次下载除外）。字幕与关键帧只出现在你自己的 agent 会话里。涉密的内部培训视频同样可用。

## ❓ 常见问题

<details>
<summary><b>为什么不需要 API Key？校对和笔记谁做的？</b></summary>

你的 AI Agent 本身就是 LLM——它按 SKILL.md 的指引读取草稿字幕自行校对、阅读画面和字幕撰写笔记。管线只做机械工作。这也是本项目与「套壳调 API」工具的本质区别。
</details>

<details>
<summary><b>不用 agent，想手动跑命令？</b></summary>

```bash
pip install -e ".[zh,asr]"        # macOS Apple 芯片把 asr 换成 mac
chalkpress transcribe 课程.mp4 --language zh --term-fix
chalkpress build 课程.mp4
```

已有字幕用 `--reuse-srt` 跳过转写；详见 [SKILL.md](SKILL.md) 与 `chalkpress --help`。
</details>

<details>
<summary><b>「30 分钟 → 5 分钟」夸张吗？</b></summary>

以**课件型网课**（PPT 录播、概念讲解）为典型场景：讲义页数 ≈ 课件页数，翻页扫读确实能把通览一节课压到 5 分钟上下。推导密集的内容压缩比会低一些——但讲义依然先给你地图。
</details>

<details>
<summary><b>支持英文视频吗？</b></summary>

支持。Whisper 支持 90+ 语种自动识别；笔记语言由 agent 与你约定。
</details>

## 🗺️ 路线图

- [x] 两段子命令 + manifest 交接（build 无 ffmpeg 依赖）
- [x] 内置软考术语包（241 条）
- [x] 双语 README
- [ ] 更多领域术语包（法考 / 考研政治英语 / 医考…—— 欢迎 PR，只需加 JSON）
- [ ] CUDA / GPU 转写后端
- [ ] 发布到主流 agent 技能市场

## 🤝 参与贡献

欢迎 PR！特别是**术语包**：往 [`chalkpress/scene_packs/`](chalkpress/scene_packs/) 加一个 `{scene, terms, direct}` JSON，就是对新考试领域的完整支持——引擎零改动。管线改进请先跑 `pytest tests/ -q`，并遵守 [AGENTS.md](AGENTS.md) 的两条不变量。

## 📄 许可

[Apache-2.0](LICENSE)。

---

<div align="center">

**觉得有用？给个 ⭐ 让更多备考人看到**

[SKILL.md](SKILL.md) · [问题反馈](https://github.com/luolin1024/chalkpress-skill/issues)

</div>
