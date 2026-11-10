"""确定性讲义管线：transcribe（视频 → 草稿字幕 + 关键帧）与 build（对齐 + PDF）。

管线零 LLM、零 API 调用（whisper 模型首次下载除外）：字幕校对与图文摘要由宿主
agent 按 SKILL.md 指引完成，SRT 是两阶段之间的交接格式。

build 阶段不碰 ffmpeg / 音视频：只消费 transcribe 落盘的 manifest.json + keyframes/，
因此可以在任何装了 pillow/reportlab 的环境里重跑。
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path

from . import __version__, align, asr, keyframes, pdf, terms, textproc

VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".webm", ".avi", ".m4v", ".flv", ".ts"}

MANIFEST_NAME = "manifest.json"


@dataclass
class TranscribeOptions:
    video: Path
    outdir: Path | None = None            # None → <视频名>_讲义/
    language: str = "auto"                # whisper 语言码或 auto
    asr_backend: str | None = None        # None → 自动（Apple 芯片优先 mlx-whisper）
    asr_model: str = "small"
    speed: str = "standard"               # faster-whisper 线程档位 standard/fast/turbo
    zh_script: str = "auto"               # auto → 按系统 locale 判定简繁
    term_fix: bool = False                # 内置软考术语包拼音修正（需 zh 依赖组）
    reuse_srt: Path | None = None         # 复用已有 SRT 跳过转写（关键帧照常抽取）
    scene_threshold: float = 0.08
    min_gap: float = 2.0
    keep_wav: bool = False


@dataclass
class BuildOptions:
    video: Path                           # 仅用于定位默认讲义目录与 PDF 标题
    outdir: Path | None = None
    srt: Path | None = None               # None → 讲义目录/<stem>.srt（草稿或校对后）
    summary: Path | None = None           # 宿主 agent 产出的摘要 md，嵌入 PDF 首页


@dataclass
class TranscribeResult:
    outdir: Path
    srt: Path
    frames: int
    detected_lang: str | None
    duration: float
    seconds: float


@dataclass
class BuildResult:
    outdir: Path
    aligned_path: Path
    pdf_path: Path
    seconds: float


def _resolve_outdir(video: Path, outdir: Path | None) -> Path:
    return (outdir or video.with_name(video.stem + "_讲义")).expanduser().resolve()


def _has_hanzi(segments) -> bool:
    return any("\u4e00" <= c <= "\u9fff" for s in segments for c in s["text"])


def _convert_segments(segments, zh_script: str, log) -> str | None:
    """简繁规范（whisper 繁体输出会干扰校对）；非中文内容原样通过，返回 script 或 None。"""
    if not segments or not _has_hanzi(segments):
        return None
    script = textproc.resolve_zh_script(zh_script)
    try:
        for s in segments:
            s["text"] = textproc.convert(s["text"], script)
    except ImportError as exc:
        raise RuntimeError(
            "检测到中文字幕但未安装 opencc：请安装中文依赖 pip install 'chalkpress[zh]'"
        ) from exc
    log(f"      简繁规范 → {script}")
    return script


def _fix_terms(segments, log) -> None:
    """软考术语包拼音滑窗修正（确定性，零 LLM）。"""
    try:
        pack = terms.load_scene_pack("ruankao")
        fixed = 0
        for s in segments:
            s["text"], n = terms.fix_custom(s["text"], pack["terms"], pack.get("direct"))
            fixed += n
    except ImportError as exc:
        raise RuntimeError(
            "术语修正需要 pypinyin：请安装中文依赖 pip install 'chalkpress[zh]'"
        ) from exc
    log(f"      术语修正（软考包 {len(pack['terms'])} 条）：替换 {fixed} 处")


def _write_manifest(path: Path, *, stem: str, video: str, duration: float,
                    detected_lang: str | None, zh_script: str | None, frames) -> None:
    data = {
        "chalkpress": __version__,
        "video": video,
        "stem": stem,
        "duration": round(duration, 3),
        "detected_lang": detected_lang,
        "zh_script": zh_script,
        "frames": [{"ts": round(f.ts, 3), "file": f.path.name} for f in frames],
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")


def _read_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def run_transcribe(opt: TranscribeOptions, log=print) -> TranscribeResult:
    t0 = time.time()
    video = opt.video.expanduser().resolve()
    if not video.is_file():
        raise FileNotFoundError(f"视频不存在：{video}")
    if video.suffix.lower() not in VIDEO_EXTS:
        raise ValueError(
            f"不支持的视频格式 {video.suffix}（支持：{' '.join(sorted(VIDEO_EXTS))}）")
    outdir = _resolve_outdir(video, opt.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    srt_path = outdir / f"{video.stem}.srt"
    wav = outdir / "audio.wav"

    log(f"[1/2] 语音转写：{video.name}")
    if opt.reuse_srt:
        segments = align.parse_srt(opt.reuse_srt)
        detected = None
        log(f"      复用字幕 {opt.reuse_srt}（{len(segments)} 条），跳过转写")
    else:
        backend = opt.asr_backend or asr.best_backend()
        threads = asr.resolve_threads(opt.speed)
        log(f"      抽取音轨 → 本地转写（{backend}/{opt.asr_model}，{threads} 线程）…")
        asr.extract_audio(video, wav)
        lang = None if opt.language in ("auto", "") else opt.language
        segments, detected = asr.transcribe(wav, opt.asr_model, backend, lang,
                                            threads=threads)
        log(f"      {len(segments)} 条原始字幕（检测语言：{detected or '?'}）")

    script = _convert_segments(segments, opt.zh_script, log)
    if opt.term_fix and segments:
        _fix_terms(segments, log)
    asr.write_srt(segments, srt_path)
    log(f"      草稿字幕（{len(segments)} 条）→ {srt_path.name}")

    duration = asr.wav_duration(wav) if wav.exists() else keyframes.parse_duration_ffmpeg(video)
    log(f"[2/2] 场景检测（阈值 {opt.scene_threshold}）→ 抽帧 → 去重 …")
    times = keyframes.plan_frame_times(video, duration, opt.scene_threshold, opt.min_gap)
    frames = keyframes.extract_frames(video, times, outdir / "keyframes")
    log(f"      {len(times)} 个候选 → {len(frames)} 个关键帧")

    if wav.exists() and not opt.keep_wav:
        wav.unlink()
    _write_manifest(outdir / MANIFEST_NAME, stem=video.stem, video=video.name,
                    duration=duration, detected_lang=detected, zh_script=script,
                    frames=frames)

    dt = time.time() - t0
    log(f"完成：{outdir}（{dt:.1f}s）— 下一步：校对 {srt_path.name}，再运行 chalkpress build")
    return TranscribeResult(outdir=outdir, srt=srt_path, frames=len(frames),
                            detected_lang=detected, duration=duration, seconds=dt)


def run_build(opt: BuildOptions, log=print) -> BuildResult:
    t0 = time.time()
    video = opt.video.expanduser().resolve()
    outdir = _resolve_outdir(video, opt.outdir)
    manifest_path = outdir / MANIFEST_NAME
    if not manifest_path.is_file():
        raise FileNotFoundError(
            f"未找到 {manifest_path}：请先运行 chalkpress transcribe 生成关键帧")
    man = _read_manifest(manifest_path)
    stem = man["stem"]

    srt_path = opt.srt.expanduser().resolve() if opt.srt else outdir / f"{stem}.srt"
    if not srt_path.is_file():
        raise FileNotFoundError(
            f"未找到字幕 {srt_path}：transcribe 会产出草稿 SRT，校对（可由宿主 agent 完成）后再 build")
    segments = align.parse_srt(srt_path)

    frames = [keyframes.KeyFrame(ts=f["ts"], path=outdir / "keyframes" / f["file"])
              for f in man["frames"]]
    missing = [f.path.name for f in frames if not f.path.is_file()]
    if missing:
        raise FileNotFoundError(
            f"关键帧缺失 {len(missing)} 张（如 {missing[0]}）：请重新运行 chalkpress transcribe")

    log(f"[1/2] 字幕 × 关键帧 对齐（{len(segments)} 条字幕 × {len(frames)} 帧）…")
    aligned = align.align(segments, [f.ts for f in frames])
    aligned_path = outdir / f"{stem}.aligned.md"
    aligned_path.write_text(
        align.window_markdown(aligned, frames, img_rel="keyframes"), encoding="utf-8")

    summary_md = None
    if opt.summary is not None:
        p = opt.summary.expanduser().resolve()
        if not p.is_file():
            raise FileNotFoundError(f"摘要文件不存在：{p}")
        summary_md = p.read_text(encoding="utf-8")

    log("[2/2] 生成 PDF …")
    pdf_path = outdir / f"{stem}.pdf"
    pdf.build_pdf(pdf_path, stem, frames, aligned, summary_md)

    dt = time.time() - t0
    log(f"完成：{outdir}（{dt:.1f}s）")
    return BuildResult(outdir=outdir, aligned_path=aligned_path,
                       pdf_path=pdf_path, seconds=dt)
