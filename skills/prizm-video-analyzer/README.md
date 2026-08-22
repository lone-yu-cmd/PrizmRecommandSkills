# Prizm Video Analyzer

从 B 站 / 抖音 / YouTube / 小红书 / TikTok 链接提取口播和关键帧，总结视频里实际讲了什么。没有平台字幕时下载音频并用 Whisper 转写。

## Install

随对外仓一起装：

```bash
npx skills add lone-yu-cmd/PrizmRecommandSkills --skill prizm-video-analyzer
```

全局：

```bash
npx skills add lone-yu-cmd/PrizmRecommandSkills --skill prizm-video-analyzer -g
```

skills.sh：https://skills.sh/lone-yu-cmd/PrizmRecommandSkills/prizm-video-analyzer

## Requirements

- `yt-dlp`
- `ffmpeg` / `ffprobe`
- Python 3.10+
- No captions: `pip install faster-whisper`

## Usage

Paste a video URL and ask to summarize or extract what the video says. The agent runs `scripts/analyze.py`, reads keyframes, and writes a grounded summary.

## License

MIT
