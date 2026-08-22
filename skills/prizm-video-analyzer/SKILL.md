---
name: prizm-video-analyzer
description: "从视频链接提取并总结片内内容（口播 + 画面）。用户贴 B站 / 抖音 / YouTube / 小红书 / TikTok 链接，或说总结视频、分析这个视频、视频讲了什么、提取字幕、看这个链接里的内容时，必须使用本 skill。不要只根据标题或简介猜测。没有平台字幕时下载音频并用 Whisper 转写，同时抽关键帧读板上的字。"
license: MIT
---

# Prizm Video Analyzer

把一条视频 URL 变成「片里实际讲了什么」。先拿现成文字，没有再下音频转写，并抽帧核对画面。

这次从 B 站实操得到的关键事实：风控拦的是网页/下载，不是「不能转写」。弹幕不是字幕。Whisper 必须先有音频。

## Resolve `SKILL_DIR`

本文件所在目录就是 `SKILL_DIR`。脚本在 `SKILL_DIR/scripts/analyze.py`。

```bash
SKILL_DIR="<本 SKILL.md 的绝对目录>"
python3 "$SKILL_DIR/scripts/analyze.py" "<VIDEO_URL>"
```

## 何时使用

- 用户给出 `bilibili.com`、`b23.tv`、`BV*`、`douyin.com`、`v.douyin.com`、`youtube.com`、`youtu.be`、`xiaohongshu.com`、`xhslink.com`、`tiktok.com` 链接，并要求总结 / 分析 / 提取内容
- 用户说「这个视频讲了什么」「提取字幕」「分析这个链接」
- 本地 `.mp4` / `.mov` / `.webm` 也可以走同一脚本（把路径当 source）

做 Remotion 成片、剪映草稿、只下视频不当分析时，不要用本 skill。

## 依赖

需要本机已有：

- `yt-dlp`
- `ffmpeg` / `ffprobe`
- Python 3.10+
- 没有平台字幕时：`pip install faster-whisper`（本地转写，免费）

缺 `yt-dlp` 时：`brew install yt-dlp`。缺 `ffmpeg` 时：`brew install ffmpeg`。

## 工作流程

### 1. 跑提取脚本

把用户给的 URL 原样传入（跟踪参数可留着，脚本会去掉 `spm_id_from` / `vd_source`）。

```bash
python3 "$SKILL_DIR/scripts/analyze.py" "<URL>"
```

常用参数：

- `--max-frames N` 默认 12。讲解动画 / PPT 够用；用户问某一秒可再跑 `--start` / `--end`（若脚本支持）或提高帧数
- `--no-frames` 只要口播
- `--no-whisper` 禁止转写（只适合确认已有字幕时）
- `--cookies-from-browser chrome` 强制带浏览器登录态（B 站 412 时脚本会自己重试，失败再手动加）
- `--whisper-model small` 中文专有名词比 `base` 准，更慢

脚本往 stdout 打一份 JSON，日志在 stderr。读 JSON，不要把 stderr 里的进度条当成结果。

JSON 字段：

- `title` `author` `duration` `platform` `url`
- `text_source`：`captions`（平台字幕）或 `whisper`（音频转写）或 `none`
- `transcript`：口播文字；可能有 ASR 错字
- `frames`：`[{path, timestamp}]`，`path` 为绝对路径
- `error`：失败原因；有则按下一节处理，不要编造片内内容

### 2. 失败时怎么补

| 现象 | 原因 | 下一步 |
|------|------|--------|
| HTTP 412 / Unable to download webpage | B 站等站点拦无登录态请求 | 脚本已会试 Chrome cookie。仍失败则用本机已登录 Chrome（playwright-pro 的 CDP，不要 `chromium.launch()`），或让用户导出 `cookies.txt` 后 `--cookies <file>` |
| `text_source: none` 且提示 danmaku | 只有弹幕，没有口播字幕 | 不要把弹幕当口播。确保没加 `--no-whisper`，安装 `faster-whisper` 后重跑 |
| `faster-whisper not installed` | 没字幕必须转写 | `pip install faster-whisper` 后重跑 |
| Safari cookie `Operation not permitted` | 沙箱读不了 Safari cookie | 改用 Chrome / 用户导出的 `cookies.txt` |
| 地区锁 / 会员视频 | 当前登录态也没有权 | 如实告诉用户，不要反复盲试 |

不要用无头空白浏览器去打开 B 站——没有登录态，412 会再来一次。

### 3. 读画面

`frames` 里每一张都用 Read 打开（同一轮并行）。时间戳用来对齐口播。

讲解视频里，策略名、公式、对比图经常只出现在画面上。口播和板书都要进总结。

### 4. 写总结

用视频的主要语言写（中文片用中文）。

结构：

1. 一条标题行：`[{title}]({url})` + 作者 + 时长
2. 视频在解决什么问题（一两句）
3. 按主题分段列出片内要点；保留片中的例子和类比
4. 若 `text_source` 是 `whisper`，在文末注明口播来自语音识别，专有名词已尽量用画面校正
5. 不要把全文 transcript 贴进对话，除非用户明确要逐字稿

校正规则：Whisper 常把 RAG 听成 Rank、Embedding 听成别的词。**以画面上的英文术语为准**，口播只负责论证和衔接。

用户若问具体时间点，引用 `t=MM:SS`。

### 5. 清理

脚本工作目录印在 JSON 的 `work_dir`。用户还要追问就留下；否则 `rm -rf` 掉它。不要删除 skill 目录本身。

## 为什么是这条链路

平台字幕、AI 看点、简介都不是片内口播。没有字幕轨时，唯一能得到「嘴里说的话」的办法是拿到音频再 ASR。下载音频仍然可能要登录态——那是过风控，不是另一种分析方法。

抽帧不是可选装饰：这条链路上 B 站那条 RAG 片，10 种策略的名字主要写在板上。

更细的站点坑见 `references/platforms.md`。
