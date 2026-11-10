"""命令行入口：transcribe（转录 + 关键帧）与 build（对齐 + PDF）两段式。

字幕校对与图文摘要由宿主 agent 完成，工作流见 SKILL.md；管线本身零 LLM、零 API。
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .pipeline import BuildOptions, TranscribeOptions, run_build, run_transcribe


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="chalkpress",
        description="讲座视频 → 讲义：transcribe 产出草稿字幕与关键帧，校对后 build 成对齐稿与 PDF。"
                    "字幕校对与图文摘要由宿主 agent 完成（SKILL.md）")
    p.add_argument("--version", action="version", version=f"chalkpress {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    t = sub.add_parser("transcribe", help="阶段一：语音转写 + 关键帧抽取 → 草稿 SRT + manifest.json")
    t.add_argument("video", type=Path, help="输入视频文件（单个）")
    t.add_argument("-o", "--outdir", type=Path, default=None,
                   help="讲义目录（默认 <视频名>_讲义/）")
    t.add_argument("--reuse-srt", type=Path, default=None,
                   help="复用已有 SRT，跳过转写（关键帧照常抽取；无需安装转写依赖）")
    t.add_argument("--language", default="auto",
                   help="语音语言：auto/zh/en/…（whisper 支持 90+ 语种，默认 auto）")
    t.add_argument("--asr-backend", choices=["auto", "faster-whisper", "mlx-whisper"],
                   default="auto", help="转写后端（默认 auto：Apple 芯片优先 mlx-whisper）")
    t.add_argument("--asr-model", default="small",
                   help="whisper 模型 tiny/base/small/medium 或 HF repo（默认 small）")
    t.add_argument("--speed", choices=["standard", "fast", "turbo"], default="standard",
                   help="faster-whisper 转写线程档位：standard=4 / fast=8 / turbo=全部核心")
    t.add_argument("--zh-script", choices=["auto", "simplified", "traditional"], default="auto",
                   help="中文字幕简繁规范：auto=按系统 locale（需 zh 依赖组）")
    t.add_argument("--term-fix", action="store_true",
                   help="软考术语拼音修正（确定性，零 LLM；需 zh 依赖组）")
    t.add_argument("--scene-threshold", type=float, default=0.08,
                   help="场景切换阈值，越小越敏感（默认 0.08）")
    t.add_argument("--min-gap", type=float, default=2.0, help="关键帧最小间隔秒（默认 2.0）")
    t.add_argument("--keep-wav", action="store_true", help="保留中间 wav 文件")

    b = sub.add_parser("build", help="阶段二：校对后的 SRT × 关键帧 → 对齐稿 + PDF")
    b.add_argument("video", type=Path, help="原视频文件（用于定位讲义目录与 PDF 标题）")
    b.add_argument("-o", "--outdir", type=Path, default=None,
                   help="讲义目录（默认 <视频名>_讲义/）")
    b.add_argument("--srt", type=Path, default=None,
                   help="字幕文件（默认讲义目录内 <视频名>.srt，即校对后的草稿）")
    b.add_argument("--summary", type=Path, default=None,
                   help="摘要 md（宿主 agent 产出），嵌入 PDF 首页")
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "transcribe":
            r = run_transcribe(TranscribeOptions(
                video=args.video, outdir=args.outdir, language=args.language,
                asr_backend=None if args.asr_backend == "auto" else args.asr_backend,
                asr_model=args.asr_model, speed=args.speed, zh_script=args.zh_script,
                term_fix=args.term_fix, reuse_srt=args.reuse_srt,
                scene_threshold=args.scene_threshold, min_gap=args.min_gap,
                keep_wav=args.keep_wav))
            print(f"字幕  : {r.srt}")
            print(f"关键帧: {r.frames} 张 → {r.outdir / 'keyframes'}")
        else:
            r = run_build(BuildOptions(video=args.video, outdir=args.outdir,
                                       srt=args.srt, summary=args.summary))
            print(f"对照  : {r.aligned_path}")
            print(f"PDF   : {r.pdf_path}")
        return 0
    except KeyboardInterrupt:
        print("已中断", file=sys.stderr)
        return 130
    except Exception as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
