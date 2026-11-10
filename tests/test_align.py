# tests/test_align.py
"""md 构建器：关键帧图片以相对链接内嵌（讲义目录平铺布局，keyframes/ 为默认前缀）。"""
from pathlib import Path

from chalkpress.align import window_markdown
from chalkpress.keyframes import KeyFrame


def _fixture():
    frames = [KeyFrame(ts=0.0, path=Path("keyframes/00m00s.jpg")),
              KeyFrame(ts=42.0, path=Path("keyframes/00m42s.jpg"))]
    aligned = [{"start": 0.0, "end": 42.0,
                "subs": [{"start": 1.0, "end": 2.0, "text": "开场"}]},
               {"start": 42.0, "end": 60.0, "subs": []}]
    return aligned, frames


def test_window_markdown_embeds_images_default_prefix():
    md = window_markdown(*_fixture())
    assert "![00:00](keyframes/00m00s.jpg)" in md
    assert "![00:42](keyframes/00m42s.jpg)" in md
    assert "## 关键字幕 × 关键帧对照" in md


def test_align_bins_by_midpoint():
    """字幕按中点落入所在关键帧时间窗，窗不重叠且不遗漏。"""
    from chalkpress.align import align as align_fn

    segs = [{"start": 1.0, "end": 5.0, "text": "a"},    # 中点 3.0 → 首窗
            {"start": 5.0, "end": 60.0, "text": "b"}]   # 中点 32.5 → 次窗
    windows = align_fn(segs, [10.0, 60.0])
    assert [w["subs"][0]["text"] for w in windows] == ["a", "b"]
    assert (windows[0]["start"], windows[0]["end"]) == (0.0, 10.0)
    assert (windows[1]["start"], windows[1]["end"]) == (10.0, 60.0)
