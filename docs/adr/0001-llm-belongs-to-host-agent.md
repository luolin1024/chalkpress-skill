# LLM 职责归宿主 agent，管线零 LLM

从桌面应用转向 agent 技能时，原管线内嵌的 OpenAI 兼容 API 调用（字幕校对 `correct.py`、图文总结 `analyze.py`、场景术语 `scenes.py`）被整体移除：技能的使用者本身就是 LLM，校对与摘要由宿主 agent 按 SKILL.md 指引完成，chalkpress 管线只保留确定性转换（ffmpeg / whisper / 对齐 / reportlab），`requests` 依赖归零。备选方案——管线保留外部 API 配置（改动小但技能用户必须自配 API key，与"去掉多余内容"的转向目标冲突）、双模式（两条代码路径都要维护）——均否决。后果：校对必须发生在转录与 build 之间（SRT 为交接物，见 ADR-0002），管线可在离线环境完整运行。

## Considered Options

- **管线保留外部 API**：兼容旧用法，但技能形态下多出 API key 配置负担与一条 LLM 代码路径。
- **双模式**（有 API 配置走管线、否则归 agent）：看似兼顾，实际两套校对质量与测试面，维护成本最高。
- **归宿主 agent**（采纳）：零配置、零网络、职责与宿主能力天然对齐。
