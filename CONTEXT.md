# Chalkpress（技能形态）

Chalkpress 把讲座视频变成可打印、可检索的讲义。本仓库是它的 agent 技能形态：SKILL.md 编排 + 确定性 Python 管线，LLM 工作由宿主 agent 承担。桌面应用形态留在旧仓库 luolin1024/chalkpress，两者互不依赖。

## Language

**讲义 (Handout)**:
一次转换的全部产物：PDF、字幕、随帧对齐的 Markdown、关键帧图、学习摘要。
_Avoid_: 输出、结果文件夹

**技能 (Skill)**:
本仓库的交付形态：一份 SKILL.md 指引加随仓库携带的 Python 管线，由宿主 agent 读取并执行。
_Avoid_: 应用、App、桌面版（属于旧仓库）

**管线 (Pipeline)**:
从视频到讲义骨架的确定性转换：转录、关键帧检测、字幕对齐、PDF 生成。不含任何 LLM 调用。
_Avoid_: 流程、程序

**转录稿 (Transcript)**:
带时间戳的字幕文件（SRT）。来自转录阶段的草稿，经校对后供构建使用。
_Avoid_: ASR 输出、识别结果

**转录 (Transcribe)**:
管线第一阶段：从视频产出草稿转录稿与关键帧。
_Avoid_: 抽取、识别

**构建 (Build)**:
管线第二阶段：将校对后的转录稿与关键帧对齐，产出对齐稿与 PDF。
_Avoid_: 排版、渲染

**转换 (Conversion)**:
一个视频到一份讲义的全过程。本技能没有批量概念，多视频由宿主 agent 逐个转换。
_Avoid_: 批处理

**校对 (Proofread)**:
修正转录稿中的错字与同音字错误。由宿主 agent 用自身模型完成，管线不做。
_Avoid_: 纠错

**摘要 (Summary)**:
面向学习者的图文学习笔记。由宿主 agent 阅读对齐稿与关键帧后写成，存为讲义目录中的 Markdown。
_Avoid_: AI 总结、study notes

**关键帧 (Keyframe)**:
按画面变化（而非固定间隔）检测出的代表页图片，充当讲义的"页"。
_Avoid_: 截图

**宿主 Agent (Host agent)**:
运行技能的 LLM agent（如 Claude Code）。承担校对与摘要，并按需安装软件依赖。
_Avoid_: 用户、客户端

**术语包 (Term pack)**:
特定领域（如软考）的术语与固定替换表 JSON，用于确定性同音字修正。
_Avoid_: 场景包、词库
