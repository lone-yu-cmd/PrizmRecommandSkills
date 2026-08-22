#!/usr/bin/env python3
"""Extract transcript and keyframes from a video URL or local file.

Stdout: one JSON object. Progress and warnings go to stderr.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

TRACKING_KEYS = {
    "spm_id_from",
    "vd_source",
    "from",
    "seid",
    "share_from",
    "share_medium",
    "share_plat",
    "share_session_id",
    "share_source",
    "share_tag",
    "timestamp",
    "unique_k",
}

DANMAKU_HINTS = ("danmaku", "弹幕")
CAPTION_FAIL_HINTS = (
    "HTTP Error 412",
    "Precondition Failed",
    "Unable to download webpage",
    "Sign in to confirm",
    "This video is private",
    "Confirm your age",
)
BROWSER_ORDER = ("chrome", "brave", "edge", "chromium")


def log(msg: str) -> None:
    print(f"[prizm-video-analyzer] {msg}", file=sys.stderr)


def which_or_die(name: str, install: str) -> str:
    path = shutil.which(name)
    if not path:
        raise SystemExit(f"{name} not found. Install with: {install}")
    return path


def run(cmd: list[str], timeout: int = 300) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
    )


def normalize_url(url: str) -> str:
    parts = urlsplit(url)
    if not parts.scheme:
        return url
    query = [
        (k, v)
        for k, v in parse_qsl(parts.query, keep_blank_values=True)
        if k not in TRACKING_KEYS
    ]
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), ""))


def detect_platform(source: str) -> str:
    s = source.lower()
    if source.startswith("/") or Path(source).exists():
        return "local"
    if "bilibili.com" in s or "b23.tv" in s or re.search(r"\bbv[a-z0-9]+", s, re.I):
        return "bilibili"
    if "youtube.com" in s or "youtu.be" in s:
        return "youtube"
    if "douyin.com" in s:
        return "douyin"
    if "xiaohongshu.com" in s or "xhslink.com" in s:
        return "xiaohongshu"
    if "tiktok.com" in s:
        return "tiktok"
    return "generic"


def caption_entries(info: dict) -> list[dict]:
    entries = []
    for bucket in ("subtitles", "automatic_captions"):
        raw = info.get(bucket) or {}
        for lang, items in raw.items():
            lang_l = str(lang).lower()
            if any(h in lang_l for h in DANMAKU_HINTS):
                continue
            if not items:
                continue
            entries.append({"lang": lang, "kind": bucket, "items": items})
    return entries


def ytdlp_cmd(
    ytdlp: str,
    *args: str,
    cookies_browser: str | None = None,
    cookies_file: str | None = None,
) -> list[str]:
    cmd = [ytdlp, "--no-playlist", "--no-warnings"]
    if cookies_file:
        cmd += ["--cookies", cookies_file]
    elif cookies_browser:
        cmd += ["--cookies-from-browser", cookies_browser]
    cmd += list(args)
    return cmd


def probe(
    ytdlp: str,
    source: str,
    cookies_browser: str | None,
    cookies_file: str | None,
) -> tuple[dict | None, str]:
    cmd = ytdlp_cmd(
        ytdlp,
        "--dump-json",
        "--skip-download",
        "--",
        source,
        cookies_browser=cookies_browser,
        cookies_file=cookies_file,
    )
    proc = run(cmd, timeout=90)
    err = (proc.stderr or "") + (proc.stdout or "")
    if proc.returncode != 0:
        return None, err
    line = (proc.stdout or "").strip().splitlines()
    if not line:
        return None, err or "empty yt-dlp json"
    try:
        return json.loads(line[0]), err
    except json.JSONDecodeError:
        return None, err or "invalid yt-dlp json"


def needs_cookies(err: str) -> bool:
    return any(h in err for h in CAPTION_FAIL_HINTS)


def download_captions(
    ytdlp: str,
    source: str,
    out_dir: Path,
    cookies_browser: str | None,
    cookies_file: str | None,
    langs: list[str],
) -> Path | None:
    lang_arg = ",".join(langs)
    cmd = ytdlp_cmd(
        ytdlp,
        "--skip-download",
        "--write-subs",
        "--write-auto-subs",
        "--sub-langs",
        lang_arg,
        "--sub-format",
        "vtt/srt/best",
        "--convert-subs",
        "vtt",
        "-o",
        str(out_dir / "media.%(ext)s"),
        "--",
        source,
        cookies_browser=cookies_browser,
        cookies_file=cookies_file,
    )
    run(cmd, timeout=120)
    vtcs = sorted(out_dir.glob("media*.vtt"))
    return vtcs[0] if vtcs else None


def vtt_to_text(path: Path) -> str:
    lines = []
    seen = set()
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        s = raw.strip()
        if not s or s.startswith("WEBVTT") or s.startswith("NOTE") or s.startswith("Kind:") or s.startswith("Language:"):
            continue
        if re.match(r"^\d+$", s):
            continue
        if "-->" in s:
            continue
        s = re.sub(r"<[^>]+>", "", s).strip()
        if s and s not in seen:
            seen.add(s)
            lines.append(s)
    return "\n".join(lines)


def download_media(
    ytdlp: str,
    source: str,
    out_dir: Path,
    cookies_browser: str | None,
    cookies_file: str | None,
    audio_only: bool,
) -> Path | None:
    if audio_only:
        fmt = "bestaudio/best"
        extra = ["-x", "--audio-format", "m4a"]
        dest = out_dir / "audio.%(ext)s"
    else:
        fmt = "bv*[height<=720]+ba/b[height<=720]/bv+ba/b"
        extra = ["--merge-output-format", "mp4"]
        dest = out_dir / "video.%(ext)s"
    cmd = ytdlp_cmd(
        ytdlp,
        "-f",
        fmt,
        *extra,
        "-o",
        str(dest),
        "--",
        source,
        cookies_browser=cookies_browser,
        cookies_file=cookies_file,
    )
    proc = run(cmd, timeout=420)
    if audio_only:
        found = list(out_dir.glob("audio.*"))
    else:
        found = [p for p in out_dir.glob("video.*") if p.suffix.lower() in {".mp4", ".mkv", ".webm", ".mov"}]
    if found:
        return found[0]
    log((proc.stderr or proc.stdout or "download produced no file")[-2000:])
    return None


def transcribe(audio_path: Path, model_size: str, language: str | None) -> str | None:
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        raise SystemExit(
            "faster-whisper not installed. Run: pip install faster-whisper"
        )
    log(f"transcribing with Whisper model '{model_size}'")
    model = WhisperModel(model_size, device="auto", compute_type="auto")
    kwargs = {}
    if language:
        kwargs["language"] = language
    segments, _info = model.transcribe(str(audio_path), **kwargs)
    lines = [seg.text.strip() for seg in segments if seg.text and seg.text.strip()]
    return "\n".join(lines) if lines else None


def media_duration(ffprobe: str, path: Path) -> float:
    proc = run(
        [
            ffprobe,
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        timeout=30,
    )
    try:
        return float((proc.stdout or "0").strip() or 0)
    except ValueError:
        return 0.0


def extract_frames(
    ffmpeg: str,
    video_path: Path,
    frames_dir: Path,
    max_frames: int,
    duration: float,
) -> list[dict]:
    frames_dir.mkdir(parents=True, exist_ok=True)
    pattern = str(frames_dir / "frame_%04d.jpg")
    vf = "select='eq(pict_type\\,I)',scale=512:-2"
    proc = run(
        [
            ffmpeg,
            "-y",
            "-i",
            str(video_path),
            "-vf",
            vf,
            "-fps_mode",
            "vfr",
            "-q:v",
            "3",
            pattern,
        ],
        timeout=180,
    )
    files = sorted(frames_dir.glob("frame_*.jpg"))
    if len(files) < 4:
        shutil.rmtree(frames_dir, ignore_errors=True)
        frames_dir.mkdir(parents=True, exist_ok=True)
        fps = max(0.05, (max_frames + 1) / max(duration, 1.0))
        run(
            [
                ffmpeg,
                "-y",
                "-i",
                str(video_path),
                "-vf",
                f"fps={fps:.4f},scale=512:-2",
                "-q:v",
                "3",
                pattern,
            ],
            timeout=180,
        )
        files = sorted(frames_dir.glob("frame_*.jpg"))
        if not files:
            log((proc.stderr or "ffmpeg extracted no frames")[-1500:])
            return []

    if len(files) > max_frames and max_frames > 0:
        if max_frames == 1:
            chosen = [files[len(files) // 2]]
        else:
            chosen = [
                files[round(i * (len(files) - 1) / (max_frames - 1))]
                for i in range(max_frames)
            ]
            # preserve order, drop accidental dupes from rounding
            seen = set()
            uniq = []
            for p in chosen:
                if p not in seen:
                    seen.add(p)
                    uniq.append(p)
            chosen = uniq
        keep = set(chosen)
        for p in files:
            if p not in keep:
                p.unlink(missing_ok=True)
        files = chosen

    n = max(len(files), 1)
    frames = []
    for i, path in enumerate(files):
        ts = duration * i / max(n - 1, 1) if n > 1 else 0.0
        m, s = divmod(int(round(ts)), 60)
        h, m = divmod(m, 60)
        stamp = f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"
        frames.append({"path": str(path.resolve()), "timestamp": stamp})
    return frames


def format_duration(seconds: float | None) -> str:
    if not seconds:
        return "00:00"
    total = int(round(float(seconds)))
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Extract transcript + keyframes from a video URL")
    p.add_argument("source", help="Video URL or local file path")
    p.add_argument("--out-dir", help="Working directory (default: temp dir)")
    p.add_argument("--max-frames", type=int, default=12)
    p.add_argument("--no-frames", action="store_true")
    p.add_argument("--no-whisper", action="store_true")
    p.add_argument("--cookies-from-browser", dest="cookies_browser")
    p.add_argument("--cookies", dest="cookies_file")
    p.add_argument("--whisper-model", default="base")
    p.add_argument("--language", default="", help="Whisper language hint, e.g. zh or en")
    return p.parse_args()


def result_payload(**kwargs):
    return {k: v for k, v in kwargs.items()}


def main() -> int:
    args = parse_args()
    source = args.source
    if not Path(source).exists():
        source = normalize_url(source)
    platform = detect_platform(source)

    ytdlp = which_or_die("yt-dlp", "brew install yt-dlp")
    ffmpeg = which_or_die("ffmpeg", "brew install ffmpeg")
    ffprobe = which_or_die("ffprobe", "brew install ffmpeg")

    work = Path(args.out_dir) if args.out_dir else Path(tempfile.mkdtemp(prefix="prizm-video-analyzer-"))
    work.mkdir(parents=True, exist_ok=True)
    log(f"work dir: {work}")

    cookies_browser = args.cookies_browser
    cookies_file = args.cookies_file
    info = None
    last_err = ""

    if platform == "local":
        media = Path(source).expanduser().resolve()
        if not media.exists():
            print(json.dumps({"error": f"file not found: {media}", "work_dir": str(work)}))
            return 1
        duration = media_duration(ffprobe, media)
        transcript = None
        text_source = "none"
        if not args.no_whisper:
            transcript = transcribe(
                media,
                args.whisper_model,
                args.language or None,
            )
            text_source = "whisper" if transcript else "none"
        frames = []
        if not args.no_frames and args.max_frames > 0:
            frames = extract_frames(ffmpeg, media, work / "frames", args.max_frames, duration)
        print(
            json.dumps(
                result_payload(
                    title=media.name,
                    author="",
                    duration=format_duration(duration),
                    platform="local",
                    url=str(media),
                    text_source=text_source,
                    transcript=transcript or "",
                    frames=frames,
                    work_dir=str(work),
                ),
                ensure_ascii=False,
            )
        )
        return 0

    attempts: list[str | None] = [cookies_browser] if cookies_browser else [None]
    if not cookies_file:
        for b in BROWSER_ORDER:
            if b not in attempts:
                attempts.append(b)

    info = None
    used_browser = cookies_browser
    for browser in attempts:
        used_browser = browser
        label = browser or "no-cookies"
        log(f"probing via yt-dlp ({label})")
        info, last_err = probe(ytdlp, source, browser, cookies_file)
        if info:
            break
        if browser is None and not needs_cookies(last_err):
            break
        if browser is None:
            log("probe without cookies failed; retrying with browser cookies")

    if not info:
        print(
            json.dumps(
                {
                    "error": "yt-dlp could not read this URL. If this is Bilibili/Douyin, export cookies or connect an already-logged-in Chrome.",
                    "detail": last_err[-2000:],
                    "platform": platform,
                    "url": source,
                    "work_dir": str(work),
                },
                ensure_ascii=False,
            )
        )
        return 1

    title = info.get("title") or ""
    author = info.get("uploader") or info.get("channel") or info.get("creator") or ""
    duration_s = info.get("duration") or 0
    captions = caption_entries(info)
    langs = [c["lang"] for c in captions]
    preferred = [lang for lang in langs if str(lang).lower().startswith(("zh", "en"))]
    sub_langs = preferred or langs or ["zh.*", "zh", "en.*", "en"]

    transcript = ""
    text_source = "none"
    if captions:
        log(f"found caption tracks: {', '.join(langs)}")
        vtt = download_captions(
            ytdlp, source, work, used_browser, cookies_file, sub_langs
        )
        if vtt:
            transcript = vtt_to_text(vtt)
            text_source = "captions"
    else:
        log("no caption tracks (danmaku-only counts as none)")

    if not transcript and not args.no_whisper:
        audio = download_media(
            ytdlp, source, work, used_browser, cookies_file, audio_only=True
        )
        if not audio:
            print(
                json.dumps(
                    {
                        "title": title,
                        "author": author,
                        "duration": format_duration(duration_s),
                        "platform": platform,
                        "url": source,
                        "error": "No captions, and audio download failed. Browser cookies may be required.",
                        "work_dir": str(work),
                    },
                    ensure_ascii=False,
                )
            )
            return 1
        lang = args.language or ("zh" if platform in {"bilibili", "douyin", "xiaohongshu"} else None)
        transcript = transcribe(audio, args.whisper_model, lang) or ""
        text_source = "whisper" if transcript else "none"

    frames: list[dict] = []
    if not args.no_frames and args.max_frames > 0:
        video = download_media(
            ytdlp, source, work, used_browser, cookies_file, audio_only=False
        )
        if video:
            dur = duration_s or media_duration(ffprobe, video)
            frames = extract_frames(ffmpeg, video, work / "frames", args.max_frames, float(dur or 0))
        else:
            log("video download failed; continuing without frames")

    print(
        json.dumps(
            result_payload(
                title=title,
                author=author,
                duration=format_duration(duration_s),
                platform=platform,
                url=info.get("webpage_url") or source,
                text_source=text_source,
                transcript=transcript,
                frames=frames,
                cookies=used_browser or ("file" if cookies_file else None),
                work_dir=str(work),
            ),
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
    except subprocess.TimeoutExpired:
        print(json.dumps({"error": "timed out running yt-dlp or ffmpeg"}))
        raise SystemExit(1)
