# Platform runtime

Load this when preparing a parse, or when a platform fails because `yt-dlp`, Node, or a Chrome cookie is missing.

Run `node scripts/ensure_runtime.mjs` before the first parse on a machine. It puts the official standalone `yt-dlp` in `scripts/vendor/`. Node must already be on `PATH`; the script does not install Node. Chrome cookies are read from the local Chrome profile at parse time and are not stored in the skill.

## What each platform needs

| Platform | How the video is obtained | Local tools |
|---|---|---|
| Xiaohongshu, Douyin, Bilibili, X/Twitter | Dedicated HTTP API, then `short_videos` if that API misses | Node |
| Kuaishou, TikTok, Haokan, Weishi, AcFun, Oasis, WeChat Channels, Doubao, Quanmin K歌 | `short_videos`, or the share page for Quanmin | Node |
| Jimeng | `short_videos` on a `jimeng.jianying.com/s/...` short link | Node |
| Ixigua | Same numeric id sent to the Douyin `short_videos` route | Node |
| Meipai | Decode `data-video` from the hot or square listing, then follow the Meitu CDN signer | Node |
| Zhihu, Pear Video, Huya | `yt-dlp` | Node, skill-local `yt-dlp` |
| Instagram | `yt-dlp` with Chrome cookies | Node, skill-local `yt-dlp`, Chrome logged into Instagram |
| YouTube | `yt-dlp` with Chrome cookies and the Node EJS challenge solver (`--remote-components ejs:github`) | Node, skill-local `yt-dlp`, Chrome logged into YouTube |

## When a dependency is missing

- `yt-dlp` is missing or will not run: run `node scripts/ensure_runtime.mjs` again. Do not switch to a random downloader.
- Node is missing: stop and ask for Node on `PATH`. YouTube's player challenge is solved by Node, so a standalone `yt-dlp` binary is not enough there.
- YouTube or Instagram returns a cookie or bot-check error: the Chrome profile on this machine has no usable login. The skill cannot copy cookies from another computer.
- Meipai `/media/<id>` has no video token: the PC detail page hides it. Use a hot or square listing URL, or a `/media/<id>` that is still present on those listings.
- A video page exits non-zero: do not write a success report. The parser already treats an empty video result as failure.
