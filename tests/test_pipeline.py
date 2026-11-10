# tests/test_pipeline.py
"""管线契约：manifest 交接格式、build 对 transcribe 产物的依赖与报错指引。"""
from pathlib import Path

import pytest

from chalkpress.keyframes import KeyFrame
from chalkpress.pipeline import (
    MANIFEST_NAME,
    BuildOptions,
    _read_manifest,
    _write_manifest,
    run_build,
)


def test_manifest_roundtrip(tmp_path):
    frames = [KeyFrame(ts=0.0, path=Path("keyframes/00m00s.jpg")),
              KeyFrame(ts=61.5, path=Path("keyframes/01m01s.jpg"))]
    path = tmp_path / MANIFEST_NAME
    _write_manifest(path, stem="demo", video="demo.mp4", duration=120.25,
                    detected_lang="zh", zh_script="simplified", frames=frames)
    man = _read_manifest(path)
    assert man["stem"] == "demo"
    assert man["detected_lang"] == "zh"
    assert man["duration"] == 120.25
    assert man["frames"] == [{"ts": 0.0, "file": "00m00s.jpg"},
                             {"ts": 61.5, "file": "01m01s.jpg"}]


def test_manifest_survives_none_fields(tmp_path):
    """复用外部 SRT 时 detected_lang/zh_script 为 None，manifest 必须可写可读。"""
    path = tmp_path / MANIFEST_NAME
    _write_manifest(path, stem="x", video="x.mkv", duration=3.0,
                    detected_lang=None, zh_script=None, frames=[])
    man = _read_manifest(path)
    assert man["detected_lang"] is None and man["zh_script"] is None


def test_build_requires_transcribe_manifest(tmp_path, capsys):
    """没有 manifest 时报错并指向 transcribe 阶段，而不是含糊失败。"""
    video = tmp_path / "v.mp4"
    video.write_bytes(b"")
    with pytest.raises(FileNotFoundError, match="transcribe"):
        run_build(BuildOptions(video=video, outdir=tmp_path / "v_讲义"))


def test_build_requires_srt(tmp_path):
    """有 manifest 没字幕：报错说明草稿 SRT 在哪、该先校对。"""
    video = tmp_path / "v.mp4"
    video.write_bytes(b"")
    outdir = tmp_path / "v_讲义"
    outdir.mkdir()
    (outdir / MANIFEST_NAME).write_text(
        '{"stem": "v", "duration": 1.0, "detected_lang": null, '
        '"zh_script": null, "frames": []}', encoding="utf-8")
    with pytest.raises(FileNotFoundError, match="SRT"):
        run_build(BuildOptions(video=video, outdir=outdir))
