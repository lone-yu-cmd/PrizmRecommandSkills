# BugPk Social Parser API Reference

Use these public BugPk endpoints through a `url` parameter.

## Xiaohongshu

Endpoint:

```text
GET https://api.bugpk.com/api/xhsjx?url=<full_xiaohongshu_share_url>
```

Expected fields:

- `code`
- `msg`
- `data.type`
- `data.title`
- `data.desc`
- `data.author.name`
- `data.author.id`
- `data.author.avatar`
- `data.cover`
- `data.url`
- `data.images`
- `data.live_photo`
- `data.video_backup`
- `cache_status`
- `bktip`

Notes:

- `desc` is the正文.
- `video_backup` may be a string or a list.
- Share URLs often include tracking query parameters. Keep the content path, and drop unrelated noise when the parser expects a plain share URL.
- Some fallback parsers are more tolerant of the original share link than of a cleaned canonical URL.
- A direct `520` usually means transport or edge blocking, not a schema problem.

## Douyin

Fallback order:

1. `https://api.bugpk.com/api/douyin`
2. `https://www.devtool.top/api/douyin/parse`
3. `https://api.bugpk.com/api/short_videos`

### Works

Endpoint:

```text
GET/POST https://api.bugpk.com/api/douyin?url=<douyin_share_url>
```

Expected fields:

- `code`
- `msg`
- `data.type`
- `data.title`
- `data.desc`
- `data.author.name`
- `data.author.id`
- `data.author.avatar`
- `data.cover`
- `data.url`
- `data.video_backup`
- `data.images`
- `data.live_photo[].image`
- `data.live_photo[].video`
- `data.music`

Notes:

- `type` can be `video`, `image`, or `live`.
- Live photo records contain image/video pairs.
- Video defaults should not be downloaded unless the user asks.
- The Devtool endpoint is a lighter backup parser. Use it before the aggregated fallback when the main endpoint misses content.
- The aggregated fallback covers many short-video share scenarios and is the final fallback when the other Douyin parsers miss.
- Some links work better with the original share URL than with a cleaned canonical URL.

### Profile

Endpoint:

```text
GET/POST https://api.bugpk.com/api/dyzy?url=<douyin_profile_url>&count=<n>
GET/POST https://api.bugpk.com/api/dyzy?id=<sec_uid>&count=<n>
```

Expected fields:

- `code`
- `msg`
- `data[]`
- `pagination.total`
- `pagination.has_more`
- `data[].index`
- `data[].aweme_id`
- `data[].desc`
- `data[].create_time`
- `data[].share_url`
- `data[].author`
- `data[].author_uid`
- `data[].author_sec_uid`
- `data[].type`
- `data[].cover`
- `data[].url`
- `data[].images`
- `data[].music_title`
- `data[].music_author`
- `data[].music_url`
- `data[].statistics`
- `data[].hashtags`

Notes:

- Use this endpoint for Douyin homepage/profile links.
- Treat the returned array as a list of works, not a single post.

## Bilibili

Fallback order:

1. `https://api.bugpk.com/api/bilibili`
2. `https://uapis.cn/api/v1/social/bilibili/videoinfo`
3. `https://api.bugpk.com/api/short_videos`

Endpoint:

```text
GET https://api.bugpk.com/api/bilibili?url=<bilibili_or_b23_url>
```

Expected fields:

- `code`
- `msg`
- `data.title`
- `data.cover`
- `data.description`
- `data.url`
- `data.user.name`
- `data.user.avatar`
- `data.videos[].title`
- `data.videos[].duration`
- `data.videos[].durationFormat`
- `data.videos[].url`
- `data.totalVideos`

Notes:

- The API is described as supporting Bilibili short videos and collections.
- Direct media URLs may expire; download when long-term archiving matters.
- The uapis endpoint is a backup metadata source and is useful when the primary Bilibili parser fails.
- The aggregated fallback is the final layer for Bilibili share links that still need recovery.
