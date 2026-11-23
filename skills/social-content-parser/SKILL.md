---
name: social-content-parser
description: "Parse and archive public social-media and short-video share URLs from 20+ platforms (Douyin posts/profiles, Xiaohongshu, Bilibili, X/Twitter, Kuaishou, YouTube, TikTok, Instagram, Zhihu, etc.) into structured local content packages with normalized metadata, media downloads, and optional transcription. Use whenever the user wants to extract, scrape, download, or archive a social share link, strip tracking parameters, fetch a Douyin creator profile, or save structured notes and media—even if they just say 「解析这个链接」「把这条笔记/推文/主页存下来」. Do not use when the user wants a deep comprehension summary of what a video explains on screen and in speech (use prizm-video-analyzer)."
---

# Social Content Parser

Use this skill to turn a public short-video or social share URL into a local content package. Xiaohongshu, Douyin, Bilibili, and X/Twitter still use their dedicated APIs first. Any other http(s) host goes to the aggregated `short_videos` fallback. If that response has no video, the script reads the page directly for Quanmin K歌 and Meipai, then calls `yt-dlp`. YouTube needs `yt-dlp`, Node, and Chrome cookies (`--remote-components ejs:github` solves the player challenge). Instagram and Ixigua also try Chrome cookies. Video files are still saved only with `--download-video`. A video page that yields no video exits non-zero.

Supported platforms:

- Xiaohongshu via `https://api.bugpk.com/api/xhsjx`
- Douyin works via `https://api.bugpk.com/api/douyin`
- Douyin profiles via `https://api.bugpk.com/api/dyzy`
- Bilibili via `https://api.bugpk.com/api/bilibili`
- X/Twitter via `https://api.fxtwitter.com/:screen_name/status/:id`
- Aggregated fallback via `https://api.bugpk.com/api/short_videos` for 20+ platforms

Fallback order:

1. Platform-specific parser.
2. Platform-specific backup parser when available.
3. Aggregated short-video fallback.

## Workflow

1. Use `scripts/parse_social.mjs` as the primary entrypoint.
2. Pass a public share URL with `--url`.
3. Let the script auto-detect the platform from the URL.
4. For Douyin, let the script choose profile or work parsing:
   - `/user/...` links or `--kind profile` use the profile API and return `items`.
   - video, image, and live-photo share links use the work API and return `type=video|image|live`.
5. Strip tracking query parameters from share URLs before parsing.
6. If the primary parser fails or returns an empty payload, try the platform backup parser when available.
7. If both platform parsers fail, fall back to the aggregated short-video parser.
8. Preserve the raw API response in `raw.json`.
9. Normalize shared fields into `normalized.json`.
10. Write a human-readable `report.md`.
11. Download avatar, cover, images, live-photo media, and optional videos into `media/` unless disabled.
12. Only when `--transcribe` is explicitly supplied, select the first normalized video and invoke `video-to-text`; write the result beside the other content files.

## Runtime

Run this once on a machine before the first parse. YouTube, Instagram, Zhihu, Pear Video, and Huya call `yt-dlp`. Copying the skill directory does not bring that program along until this step downloads it into the skill.

```bash
node scripts/ensure_runtime.mjs
```

The script checks that `node` is on `PATH`, then installs the official standalone `yt-dlp` at `scripts/vendor/yt-dlp` (`yt-dlp.exe` on Windows). Later parses use that file before `YT_DLP` or `~/.local/bin/yt-dlp`. Run it again safely when the binary already executes.

Read `references/platform-runtime.md` when preparing a parse, or when a platform fails because `yt-dlp`, Node, or a Chrome cookie is missing. That table says which platform needs which local tool. Chrome login cookies stay on the machine; the skill cannot pack them.

## Output Contract

Default output root:

- `./social-notes/`

Each parsed item creates one subfolder:

- `<platform>-<title>-<YYYY-MM-DD>-<id>/`

Files:

- `report.md`
- `normalized.json`
- `raw.json`
- `media/`
- `transcript.txt|json|srt|md` when transcription is requested and succeeds

Normalized fields:

- `platform`
- `kind`
- `canonicalUrl`
- `fallbackUsed`
- `sourceUrl`
- `code`
- `msg`
- `type`
- `title`
- `desc`
- `author.name`
- `author.id`
- `author.avatar`
- `cover`
- `primaryVideo`
- `videoBackups`
- `images`
- `livePhoto`
- `music`
- `statistics`
- `parts`
- `items`
- `pagination`
- `transcription.enabled`
- `transcription.status`
- `transcription.requestedMode`
- `transcription.usedMode`
- `transcription.format`
- `transcription.output`

## Commands

```bash
node scripts/parse_social.mjs --url "https://v.douyin.com/..."
node scripts/parse_social.mjs --url "https://www.douyin.com/user/..." --count 10
node scripts/parse_social.mjs --url "https://b23.tv/..."
node scripts/parse_social.mjs --url "https://www.xiaohongshu.com/explore/..."
node scripts/parse_social.mjs --url "https://v.douyin.com/..." --transcribe
node scripts/parse_social.mjs --url "https://www.xiaohongshu.com/explore/..." --transcribe --transcript-format srt
```

Useful options:

```bash
node scripts/parse_social.mjs --url "<share-url>" --out-dir ./social-notes
node scripts/parse_social.mjs --url "<share-url>" --no-download
node scripts/parse_social.mjs --url "<share-url>" --download-video
node scripts/parse_social.mjs --platform douyin --kind profile --id "<sec_uid>" --count 10
node scripts/parse_social.mjs --from-file raw.json --platform douyin
```

Transcription options:

```bash
node scripts/parse_social.mjs --url "<share-url>" --transcribe
node scripts/parse_social.mjs --url "<share-url>" --no-download --transcribe
node scripts/parse_social.mjs --url "<share-url>" --transcribe --transcription-mode direct
node scripts/parse_social.mjs --url "<share-url>" --transcribe --transcription-mode local --speaker-diarization
node scripts/parse_social.mjs --url "<share-url>" --transcribe --transcript-format srt --sentence-max-length 20
```

- Transcription is off by default because Tencent ASR is a paid external operation.
- Install the companion `video-to-text` skill as a sibling before using `--transcribe`.
- `direct` is the default. It sends the normalized media URL straight to Tencent without downloading or transcoding it locally.
- `local` downloads the media first and never falls back to the remote URL. Use it when CDN URLs require request headers or expire quickly.
- `auto` is an explicit recovery mode: it tries a temporary local download first and falls back to direct URL only when local preparation fails before ASR task submission.
- Add `--no-download` when only the transcript is needed. Direct transcription does not need a local video copy.
- The workflow discovers `video-to-text` as a sibling skill first, then project/user `.agents/skills` and `.skills` installs, or accepts `--video-to-text-script` / `VIDEO_TO_TEXT_SCRIPT`.
- Douyin profile results contain multiple works and are not implicitly transcribed. Supply a single work URL instead.
- There is no COS upload bridge yet. If a protected CDN URL cannot be fetched by Tencent and the locally transcoded audio still exceeds Tencent's 5 MB inline limit, upload the media to COS or another public object store and run `video-to-text --url` on that URL.

## Platform Notes

- Xiaohongshu: `desc` is the正文. `video_backup` may be a string or list.
- Douyin profile: `/user/...` homepage links use `dyzy`; normalized output has `kind=profile`, `type=profile`, and an `items` list.
- Douyin work: video, image, and live-photo share links use `douyin`; normalized output has `kind=post` and `type=video|image|live`. `live_photo` includes paired image/video values.
- X/Twitter: the parser uses FXTwitter first, keeps tweet text, author info, media, metrics, and long-form article content when available, then falls back to the aggregated parser if needed.
- Share links often contain tracking parameters; the parser keeps the content path and drops those extras before calling the API.
- Do not assume every fallback wants the same cleaned URL; some fallback parsers prefer the original share link.
- When the primary parser misses content, the skill can fall back to the aggregated short-video parser to recover a usable result.
- Bilibili: supports short videos and collections. Use `videos` as parts when present. Direct video URLs may expire.
- Fallback parser: `short_videos` covers 20+ short-video platforms and is useful when the platform-specific parser misses a share link.

## Rules

- Do not use the official `key=value` sample as a real parameter.
- Do not invent engagement metrics. Keep unsupported fields empty or absent.
- Do not assume every platform returns the same schema.
- Do not download videos unless the user asks or `--download-video` is provided.
- Do not transcribe unless the user asks or `--transcribe` is provided.
- Treat `--transcribe` as authorization for one Tencent ASR task. Do not retry a submitted ASR task through another mode; automatic fallback is allowed only before task submission.
- Preserve `raw.json` exactly for debugging and future schema changes.
