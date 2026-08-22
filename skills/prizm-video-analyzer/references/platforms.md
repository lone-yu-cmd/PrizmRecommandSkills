# 平台差异

## Bilibili

- 无 cookie 拉网页经常 **HTTP 412 Precondition Failed**。`yt-dlp` 和页面抓取都会中招。
- `https://api.bilibili.com/x/web-interface/view?bvid=BV...` 有时仍能返回标题、UP 主、时长。这只是元数据，不是口播。
- `--list-subs` 若只有 `danmaku xml`，当作没有字幕。弹幕不是口播稿。
- 播放器字幕列表和「AI 看点」经常是空的。空了就下音频 + Whisper。
- Cookie 要对 **所有** 后续 `yt-dlp` 调用生效（探测、下字幕、下音频、下视频），不要只给抖音开 cookie。
- Chrome `--cookies-from-browser chrome` 通常可用；Safari 在部分环境会 `Operation not permitted`。

## Douyin / 小红书 / TikTok

- 短链（`v.douyin.com`、`xhslink.com`）先让 `yt-dlp` 解析跳转。
- 多数没有字幕轨，默认走音频 + Whisper。
- 风控比 B 站更常见，优先浏览器 cookie。登录不是为了「看见私密内容」，是为了公开分享链接能解析播放地址。

## YouTube

- 经常有人工或自动字幕。先拉 `zh.*` / `en.*`，有字幕就不要下整段视频。
- 自动字幕比 Whisper 快，专有名词仍可能错，有画面就对照校正。

## 通用

- `yt-dlp --sub-langs en.*` 会丢掉中文字幕。本 skill 的脚本默认包含 `zh.*`。
- 不要用无登录态的新浏览器实例去「代替」cookie；412 会原样重现。
- Playwright / CDP 仅在 `--cookies-from-browser` 失败时作为升级路径，且必须连用户已登录的 Chrome。
