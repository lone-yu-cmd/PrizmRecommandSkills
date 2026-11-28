#!/usr/bin/env python3
"""Unit tests for skills/prizm-video-analyzer/scripts/analyze.py."""

import json
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import analyze


class TestPureHelpers(unittest.TestCase):
    """Tests for pure URL, platform, caption, VTT, and formatting helpers."""

    def test_normalize_url_strips_tracking_keys_and_fragment(self):
        raw = (
            "https://www.bilibili.com/video/BV1xx411c7mD/"
            "?p=2&spm_id_from=333.999&vd_source=abc&empty=&unique_k=123#reply"
        )
        normalized = analyze.normalize_url(raw)
        self.assertEqual(
            normalized,
            "https://www.bilibili.com/video/BV1xx411c7mD/?p=2&empty=",
        )
        # All TRACKING_KEYS stripped
        all_tracking = "https://example.com/v?" + "&".join(f"{k}=val" for k in sorted(analyze.TRACKING_KEYS))
        self.assertEqual(analyze.normalize_url(all_tracking), "https://example.com/v")
        # Local or scheme-less path returned unchanged
        self.assertEqual(analyze.normalize_url("videos/demo.mp4"), "videos/demo.mp4")

    def test_detect_platform(self):
        with tempfile.TemporaryDirectory() as tmp:
            local_file = Path(tmp) / "clip.mp4"
            local_file.write_bytes(b"0")
            self.assertEqual(analyze.detect_platform(str(local_file)), "local")

        self.assertEqual(analyze.detect_platform("/nonexistent/local.mp4"), "local")
        self.assertEqual(analyze.detect_platform("https://www.bilibili.com/video/BV1xx411c7mD"), "bilibili")
        self.assertEqual(analyze.detect_platform("https://b23.tv/abc123"), "bilibili")
        self.assertEqual(analyze.detect_platform("BV1xx411c7mD"), "bilibili")
        self.assertEqual(analyze.detect_platform("https://www.youtube.com/watch?v=dQw4w9WgXcQ"), "youtube")
        self.assertEqual(analyze.detect_platform("https://youtu.be/dQw4w9WgXcQ"), "youtube")
        self.assertEqual(analyze.detect_platform("https://www.douyin.com/video/123"), "douyin")
        self.assertEqual(analyze.detect_platform("https://www.xiaohongshu.com/explore/abc"), "xiaohongshu")
        self.assertEqual(analyze.detect_platform("http://xhslink.com/o/xyz"), "xiaohongshu")
        self.assertEqual(analyze.detect_platform("https://www.tiktok.com/@user/video/1"), "tiktok")
        self.assertEqual(analyze.detect_platform("https://vimeo.com/123456"), "generic")

    def test_caption_entries_skips_danmaku_and_empty_buckets(self):
        info = {
            "subtitles": {
                "danmaku": [{"ext": "xml"}],
                "zh-弹幕": [{"ext": "ass"}],
                "zh-CN": [{"ext": "vtt"}],
                "empty-lang": [],
            },
            "automatic_captions": {
                "DANMAKU-live": [{"ext": "xml"}],
                "en": [{"ext": "vtt"}],
            },
        }
        self.assertEqual(
            analyze.caption_entries(info),
            [
                {"lang": "zh-CN", "kind": "subtitles", "items": [{"ext": "vtt"}]},
                {"lang": "en", "kind": "automatic_captions", "items": [{"ext": "vtt"}]},
            ],
        )
        self.assertEqual(analyze.caption_entries({}), [])

    def test_ytdlp_cmd_cookie_flags_and_precedence(self):
        self.assertEqual(
            analyze.ytdlp_cmd("yt-dlp", "--skip-download", "url"),
            ["yt-dlp", "--no-playlist", "--no-warnings", "--skip-download", "url"],
        )
        self.assertEqual(
            analyze.ytdlp_cmd("yt-dlp", "url", cookies_browser="chrome"),
            ["yt-dlp", "--no-playlist", "--no-warnings", "--cookies-from-browser", "chrome", "url"],
        )
        self.assertEqual(
            analyze.ytdlp_cmd("yt-dlp", "url", cookies_browser="chrome", cookies_file="/tmp/c.txt"),
            ["yt-dlp", "--no-playlist", "--no-warnings", "--cookies", "/tmp/c.txt", "url"],
        )

    def test_needs_cookies(self):
        for hint in analyze.CAPTION_FAIL_HINTS:
            with self.subTest(hint=hint):
                self.assertTrue(analyze.needs_cookies(f"ERROR: {hint} happened"))
        self.assertFalse(analyze.needs_cookies("ERROR: Unsupported URL"))
        self.assertFalse(analyze.needs_cookies(""))

    def test_vtt_to_text_parses_and_deduplicates(self):
        vtt_content = "\n".join([
            "WEBVTT",
            "Kind: captions",
            "Language: zh",
            "",
            "NOTE This is a comment",
            "",
            "1",
            "00:00:00.000 --> 00:00:02.000",
            "<c>Hello</c> <b>world</b>",
            "",
            "2",
            "00:00:02.000 --> 00:00:04.000",
            "Hello world",
            "Second line",
        ])
        with tempfile.TemporaryDirectory() as tmp:
            vtt_path = Path(tmp) / "sub.vtt"
            vtt_path.write_text(vtt_content, encoding="utf-8")
            self.assertEqual(analyze.vtt_to_text(vtt_path), "Hello world\nSecond line")

            empty_vtt = Path(tmp) / "empty.vtt"
            empty_vtt.write_text("WEBVTT\n\n", encoding="utf-8")
            self.assertEqual(analyze.vtt_to_text(empty_vtt), "")

    def test_format_duration(self):
        self.assertEqual(analyze.format_duration(None), "00:00")
        self.assertEqual(analyze.format_duration(0), "00:00")
        self.assertEqual(analyze.format_duration(5), "00:05")
        self.assertEqual(analyze.format_duration(65.4), "01:05")
        self.assertEqual(analyze.format_duration(65.6), "01:06")
        self.assertEqual(analyze.format_duration(3600), "1:00:00")
        self.assertEqual(analyze.format_duration(3661), "1:01:01")

    def test_result_payload(self):
        self.assertEqual(
            analyze.result_payload(title="Demo", frames=[]),
            {"title": "Demo", "frames": []},
        )


class TestMockedSystemAndSubprocessFunctions(unittest.TestCase):
    """Tests for functions delegating to shutil, subprocess, sys.argv, and faster_whisper."""

    def test_which_or_die(self):
        with mock.patch("analyze.shutil.which", return_value="/usr/local/bin/ffmpeg"):
            self.assertEqual(analyze.which_or_die("ffmpeg", "brew install ffmpeg"), "/usr/local/bin/ffmpeg")

        with mock.patch("analyze.shutil.which", return_value=None):
            with self.assertRaises(SystemExit) as ctx:
                analyze.which_or_die("yt-dlp", "brew install yt-dlp")
            self.assertIn("brew install yt-dlp", str(ctx.exception))

    def test_probe_branches(self):
        fail_proc = subprocess.CompletedProcess([], 1, stdout="", stderr="HTTP Error 412")
        with mock.patch("analyze.run", return_value=fail_proc):
            info, err = analyze.probe("yt-dlp", "https://example.com", None, None)
        self.assertIsNone(info)
        self.assertIn("412", err)

        empty_proc = subprocess.CompletedProcess([], 0, stdout="   \n", stderr="")
        with mock.patch("analyze.run", return_value=empty_proc):
            info, err = analyze.probe("yt-dlp", "https://example.com", None, None)
        self.assertIsNone(info)
        self.assertEqual(err, "empty yt-dlp json")

        bad_json_proc = subprocess.CompletedProcess([], 0, stdout="{bad json", stderr="")
        with mock.patch("analyze.run", return_value=bad_json_proc):
            info, err = analyze.probe("yt-dlp", "https://example.com", None, None)
        self.assertIsNone(info)
        self.assertEqual(err, "invalid yt-dlp json")

        ok_proc = subprocess.CompletedProcess([], 0, stdout='{"title":"Video"}\n', stderr="")
        with mock.patch("analyze.run", return_value=ok_proc):
            info, _ = analyze.probe("yt-dlp", "https://example.com", "chrome", None)
        self.assertEqual(info, {"title": "Video"})

    def test_media_duration(self):
        with mock.patch("analyze.run", return_value=subprocess.CompletedProcess([], 0, stdout="123.45\n", stderr="")):
            self.assertEqual(analyze.media_duration("ffprobe", Path("a.mp4")), 123.45)

        with mock.patch("analyze.run", return_value=subprocess.CompletedProcess([], 0, stdout="", stderr="")):
            self.assertEqual(analyze.media_duration("ffprobe", Path("a.mp4")), 0.0)

        with mock.patch("analyze.run", return_value=subprocess.CompletedProcess([], 0, stdout="N/A\n", stderr="")):
            self.assertEqual(analyze.media_duration("ffprobe", Path("a.mp4")), 0.0)

    def test_download_captions(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp)

            def fake_run_writes_vtt(cmd, timeout=120):
                (out_dir / "media.zh.vtt").write_text("WEBVTT\n", encoding="utf-8")
                return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

            with mock.patch("analyze.run", side_effect=fake_run_writes_vtt):
                vtt = analyze.download_captions("yt-dlp", "https://example.com", out_dir, None, None, ["zh", "en"])
            self.assertEqual(vtt, out_dir / "media.zh.vtt")

        with tempfile.TemporaryDirectory() as empty_tmp:
            with mock.patch("analyze.run", return_value=subprocess.CompletedProcess([], 1, stdout="", stderr="err")):
                self.assertIsNone(
                    analyze.download_captions("yt-dlp", "https://example.com", Path(empty_tmp), None, None, ["en"])
                )

    def test_download_media_audio_and_video(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp)

            def fake_audio(cmd, timeout=420):
                (out_dir / "audio.m4a").write_bytes(b"audio")
                return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

            with mock.patch("analyze.run", side_effect=fake_audio):
                self.assertEqual(
                    analyze.download_media("yt-dlp", "u", out_dir, None, None, audio_only=True),
                    out_dir / "audio.m4a",
                )

        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp)

            def fake_video_with_part(cmd, timeout=420):
                (out_dir / "video.part").write_bytes(b"partial")
                (out_dir / "video.mp4").write_bytes(b"mp4")
                return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

            with mock.patch("analyze.run", side_effect=fake_video_with_part):
                self.assertEqual(
                    analyze.download_media("yt-dlp", "u", out_dir, None, None, audio_only=False),
                    out_dir / "video.mp4",
                )

        with tempfile.TemporaryDirectory() as empty_tmp:
            with mock.patch("analyze.run", return_value=subprocess.CompletedProcess([], 1, stdout="", stderr="failed")):
                self.assertIsNone(
                    analyze.download_media("yt-dlp", "u", Path(empty_tmp), None, None, audio_only=False)
                )

    def test_extract_frames_primary_fallback_and_downsample(self):
        # 1. >= 4 I-frames without fallback, including >=1h timestamp formatting and downsampling
        with tempfile.TemporaryDirectory() as tmp:
            frames_dir = Path(tmp) / "frames"

            def fake_many_frames(cmd, timeout=180):
                for i in range(1, 7):
                    (frames_dir / f"frame_{i:04d}.jpg").write_bytes(b"jpg")
                return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

            with mock.patch("analyze.run", side_effect=fake_many_frames) as run_mock:
                frames = analyze.extract_frames("ffmpeg", Path("v.mp4"), frames_dir, max_frames=3, duration=3600.0)

            self.assertEqual(run_mock.call_count, 1)
            self.assertEqual([f["timestamp"] for f in frames], ["00:00", "30:00", "01:00:00"])
            self.assertEqual(len(list(frames_dir.glob("frame_*.jpg"))), 3)

        # 2. < 4 I-frames triggers fps fallback and respects max_frames=1 (picks middle)
        with tempfile.TemporaryDirectory() as tmp:
            frames_dir = Path(tmp) / "frames"
            calls = {"n": 0}

            def fake_sparse_then_fallback(cmd, timeout=180):
                calls["n"] += 1
                if calls["n"] == 1:
                    (frames_dir / "frame_0001.jpg").write_bytes(b"a")
                else:
                    for i in range(1, 5):
                        (frames_dir / f"frame_{i:04d}.jpg").write_bytes(b"b")
                return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

            with mock.patch("analyze.run", side_effect=fake_sparse_then_fallback) as run_mock:
                frames = analyze.extract_frames("ffmpeg", Path("v.mp4"), frames_dir, max_frames=1, duration=120.0)

            self.assertEqual(run_mock.call_count, 2)
            self.assertEqual(len(frames), 1)
            self.assertEqual(Path(frames[0]["path"]).name, "frame_0003.jpg")
            self.assertEqual(frames[0]["timestamp"], "00:00")

        # 3. Fallback produces nothing -> []
        with tempfile.TemporaryDirectory() as tmp:
            frames_dir = Path(tmp) / "frames"
            with mock.patch("analyze.run", return_value=subprocess.CompletedProcess([], 1, stdout="", stderr="no frames")):
                self.assertEqual(analyze.extract_frames("ffmpeg", Path("v.mp4"), frames_dir, 4, 10.0), [])

    def test_transcribe_with_mocked_and_missing_faster_whisper(self):
        recorded = {}

        class FakeSeg:
            def __init__(self, text):
                self.text = text

        class FakeWhisperModel:
            def __init__(self, model_size, device, compute_type):
                recorded["init"] = (model_size, device, compute_type)

            def transcribe(self, path, **kwargs):
                recorded["call"] = (path, kwargs)
                return ([FakeSeg("  first line  "), FakeSeg("   "), FakeSeg("second")], None)

        fake_mod = types.ModuleType("faster_whisper")
        fake_mod.WhisperModel = FakeWhisperModel
        with mock.patch.dict(sys.modules, {"faster_whisper": fake_mod}):
            text = analyze.transcribe(Path("/tmp/audio.m4a"), "small", "zh")
        self.assertEqual(text, "first line\nsecond")
        self.assertEqual(recorded["init"], ("small", "auto", "auto"))
        self.assertEqual(recorded["call"], ("/tmp/audio.m4a", {"language": "zh"}))

        # Blank segments yield None
        class EmptyWhisperModel(FakeWhisperModel):
            def transcribe(self, path, **kwargs):
                return ([FakeSeg(""), FakeSeg("  ")], None)

        fake_mod.WhisperModel = EmptyWhisperModel
        with mock.patch.dict(sys.modules, {"faster_whisper": fake_mod}):
            self.assertIsNone(analyze.transcribe(Path("/tmp/audio.m4a"), "base", None))

        # Missing package raises SystemExit
        with mock.patch.dict(sys.modules, {"faster_whisper": None}):
            with self.assertRaises(SystemExit) as ctx:
                analyze.transcribe(Path("/tmp/audio.m4a"), "base", None)
            self.assertIn("faster-whisper not installed", str(ctx.exception))

    def test_parse_args(self):
        with mock.patch.object(sys, "argv", ["analyze.py", "https://example.com/v"]):
            args = analyze.parse_args()
        self.assertEqual(args.source, "https://example.com/v")
        self.assertEqual(args.max_frames, 12)
        self.assertFalse(args.no_frames)
        self.assertFalse(args.no_whisper)
        self.assertEqual(args.whisper_model, "base")

        with mock.patch.object(
            sys,
            "argv",
            [
                "analyze.py",
                "video.mp4",
                "--out-dir",
                "/tmp/work",
                "--max-frames",
                "6",
                "--no-frames",
                "--no-whisper",
                "--cookies-from-browser",
                "chrome",
                "--whisper-model",
                "medium",
                "--language",
                "zh",
            ],
        ):
            custom = analyze.parse_args()
        self.assertEqual(custom.out_dir, "/tmp/work")
        self.assertEqual(custom.max_frames, 6)
        self.assertTrue(custom.no_frames)
        self.assertTrue(custom.no_whisper)
        self.assertEqual(custom.cookies_browser, "chrome")
        self.assertEqual(custom.whisper_model, "medium")
        self.assertEqual(custom.language, "zh")


if __name__ == "__main__":
    unittest.main(verbosity=2)
