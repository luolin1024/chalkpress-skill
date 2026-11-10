# Chalkpress（技能版）

讲座视频 → 可打印、可检索的讲义 PDF：场景检测关键帧成页、字幕随页对齐、宿主 agent 校对与图文摘要。全程本地处理，零 API key。

本仓库是 **agent 技能**（SKILL.md + 确定性 Python 管线），不是应用程序。桌面应用形态在旧仓库 [luolin1024/chalkpress](https://github.com/luolin1024/chalkpress)，两者互不依赖。

## 职责分工

```mermaid
graph LR
    A[视频] --> T[transcribe<br>转录 + 关键帧]
    T --> D[草稿 SRT]
    D --> P[宿主 agent<br>校对字幕]
    P --> B[build<br>对齐 + PDF]
    B --> H[讲义目录<br>PDF · aligned.md · SRT · keyframes]
    H --> S[宿主 agent<br>图文摘要 summary.md]
```

管线（`chalkpress/`）零 LLM、零网络调用（whisper 模型首次下载除外）；`requests` 依赖已归零。

## 安装与使用

技能拖入 agent 技能目录（如 `~/.agents/skills/chalkpress-skill`），由 agent 按 SKILL.md 指引按需安装依赖；人类也可直接用 CLI：

```bash
pip install -e ".[zh,asr]"     # 中文视频 + 本地转录（macOS Apple 芯片 asr→mac）
chalkpress transcribe clip.mp4 --language zh --term-fix
#   → clip_讲义/clip.srt（草稿）+ keyframes/ + manifest.json
#   （此时校对 clip.srt：只改文本，不动时间轴）
chalkpress build clip.mp4
#   → clip.aligned.md + clip.pdf
#   （写 clip.summary.md 后可嵌入 PDF 首页：）
chalkpress build clip.mp4 --summary clip_讲义/clip.summary.md
```

## 依赖分组（按需下载）

| 依赖组 | 内容 | 何时需要 |
|---|---|---|
| base（默认） | pillow, reportlab, imageio-ffmpeg | 任何转换 |
| `zh` | opencc, pypinyin | 中文视频：繁简规范、软考术语修正 |
| `asr` | faster-whisper | 无现成 SRT 时本地转录（模型另自动下载） |
| `mac` | mlx-whisper | Apple 芯片转录加速（替代 asr） |
| `dev` | pytest | 开发 |

已有 SRT 时用 `--reuse-srt`，完全不装转录依赖、零模型下载。

## 开发

```bash
uv venv .venv && uv pip install -e ".[dev,zh]" --python .venv/bin/python
.venv/bin/python -m pytest tests/ -q
```

领域词汇表见 [CONTEXT.md](CONTEXT.md)；架构决策见 [docs/adr/](docs/adr/)；仓库约定见 [AGENTS.md](AGENTS.md)。

## License

[Apache-2.0](LICENSE)
