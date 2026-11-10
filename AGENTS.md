# AGENTS.md — chalkpress-skill

Chalkpress 的 **agent 技能形态**：SKILL.md 编排 + 确定性 Python 管线（转录/关键帧/对齐/PDF）。LLM 工作（字幕校对、图文摘要）由宿主 agent 承担，管线零 LLM、零 API。桌面应用在旧仓库 `luolin1024/chalkpress`，代码已分家，不要从那边同步任何东西回来。

## 架构与不变量

```
SKILL.md            技能契约：宿主 agent 读的工作流（依赖分组 + 4 步流程）
chalkpress/
  pipeline.py       run_transcribe / run_build 两阶段 + manifest.json 交接
  cli.py            argparse 子命令 transcribe / build（唯一入口）
  asr.py            faster-whisper / mlx-whisper 双后端（均为函数内懒加载）
  keyframes.py      ffmpeg 场景检测 + 平均哈希去重
  align.py          SRT 解析、字幕×关键帧中点归窗、md 构建器
  pdf.py            reportlab 横版 A4；CJK 字体链；标签固定中文
  textproc.py       OpenCC 简繁规范（懒加载）
  terms.py          拼音滑窗术语修正（pypinyin 懒加载）+ load_scene_pack
  binaries.py       ffmpeg 解析链：CHALKPRESS_FFMPEG → PATH → imageio-ffmpeg
  scene_packs/      内置场景包数据（ruankao.json），随包分发（package-data）
tests/              pytest（纯 Python，无 ffmpeg/model/LLM 依赖）
```

**两条硬不变量**，改代码前先确认没破：

1. **两阶段契约**：`transcribe` 拥有 ffmpeg 与一切音视频访问；`build` 只消费 `manifest.json` + `keyframes/` + SRT，**绝不依赖 ffmpeg/音视频文件**（保证可在任意环境重跑）。manifest 是两阶段唯一交接物，帧时间戳必须来自 manifest 而非重新探测。
2. **管线零 LLM、零 API**：不引入 requests/网络调用（whisper 模型下载是唯一例外）。校对/摘要永远在 SRT/aligned.md 上由宿主 agent 完成。

## 领域词汇

术语以 [CONTEXT.md](CONTEXT.md) 为准（讲义/转录稿/校对/摘要/术语包等 13 词）。注意「转录 (Transcribe)」= 阶段一，「转录稿 (Transcript)」= SRT 产物，两词刻意区分，别混用。

## 约定

- 每个模块 `from __future__ import annotations`（Python ≥3.9 地板价）。
- 重依赖一律函数内懒加载（faster_whisper/mlx_whisper/opencc/pypinyin/imageio_ffmpeg），缺失时报带安装指引的 `RuntimeError`（指明装哪个 extra）。模块顶层只允许 stdlib + pillow/reportlab。
- 注入式 `log=print`，无 logging 模块；阶段日志 `[1/2]`/`[2/2]` 供宿主 agent 观测进度。
- 跨模块引用下划线私有函数（如 `align._mmss`）是本仓库既有约定，不要"修"。
- 新术语包 = 往 `chalkpress/scene_packs/` 加 JSON（`scene`/`terms`/`direct` 三键），不写代码。
- Options 默认值直接写死在 dataclass，**没有** config.toml 回退链（旧应用的配置系统已删）。

## 修改后的联动检查

- **改 CLI 旗标/工作流** → SKILL.md 是 agent 的唯一操作手册，必须同步；SKILL.md 里的报错示例要与 pipeline 的实际报错文本对上。
- **改 manifest 结构** → `tests/test_pipeline.py` 的 round-trip 用例与 build 的字段读取同改。
- **版本号**：`pyproject.toml` 与 `chalkpress/__init__.py` 两处，改一处必改另一处（当前 0.1.0）。

## 测试与验证

- 无 lint/typecheck 配置。LSP（basedpyright）的 strict 噪声（argparse Any、隐式字符串拼接）与本仓库同款存量风格，不追；但 `error` 级别要清零，可选依赖（faster_whisper/mlx_whisper）未安装导致的 stub 缺失报错除外。
- `pytest tests/ -q`：纯确定性测试（对齐分窗、术语引擎、manifest、build 报错指引）。
- 管线冒烟（改了 pipeline/keyframes/pdf 后必做）：

```bash
# 合成 20s 测试视频 + 手写 SRT，走全链（不需要 whisper）：
ffmpeg -f lavfi -i "testsrc2=size=640x360:rate=15:duration=20" \
       -f lavfi -i "sine=frequency=440:duration=20" -shortest out/clip.mp4
chalkpress transcribe out/clip.mp4 --reuse-srt out/clip.srt
chalkpress build out/clip.mp4
# 检查 clip_讲义/ 下 .srt/.aligned.md/.pdf/keyframes/manifest.json 生成且 pdf 页数正确
```

- 真实转录路径（faster-whisper 首跑下载数百 MB）在 CI 与本地默认验证里都跳过，只验证缺依赖时的报错指引。

## 交付纪律

- 新依赖必须进 pyproject 的对应 extra（base/zh/asr/mac/dev），并同步 SKILL.md 依赖表与 README 表格。
- 本仓库不发布 PyPI：包只随技能目录以 `pip install -e <技能目录>` 方式安装，package-data（scene_packs）必须留在包内。
