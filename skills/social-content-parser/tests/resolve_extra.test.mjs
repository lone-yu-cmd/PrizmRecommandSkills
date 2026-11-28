import assert from 'node:assert/strict';
import test from 'node:test';

import { labelPlatform } from '../scripts/resolve_extra.mjs';

test('labelPlatform recognizes all supported extra platforms and strips www.', () => {
  const cases = [
    ['https://www.youtube.com/watch?v=abc', 'youtube'],
    ['https://youtu.be/abc', 'youtube'],
    ['https://music.youtube.com/watch?v=abc', 'youtube'],
    ['https://m.youtube.com/watch?v=abc', 'youtube'],
    ['https://www.instagram.com/reel/xyz/', 'instagram'],
    ['https://instagr.am/p/xyz/', 'instagram'],
    ['https://www.ixigua.com/123456', 'ixigua'],
    ['https://www.zhihu.com/zvideo/123', 'zhihu'],
    ['https://www.pearvideo.com/video_123', 'pearvideo'],
    ['https://www.meipai.com/media/123', 'meipai'],
    ['https://www.huya.com/video/play/123.html', 'huya'],
    ['https://jimeng.jianying.com/ai-tool/home', 'jimeng'],
    ['https://dreamina.jianying.com/ai-tool/home', 'jimeng'],
    ['https://www.doubao.com/share/123', 'doubao'],
    ['https://kg.qq.com/node/play?s=123', 'quanmin'],
    ['https://node.kg.qq.com/play?s=123', 'quanmin'],
    ['https://www.kuaishou.com/short-video/abc', 'kuaishou'],
    ['https://v.kuaishouapp.com/s/abc', 'kuaishou'],
    ['https://www.tiktok.com/@user/video/1', 'tiktok'],
    ['https://haokan.baidu.com/v?vid=1', 'haokan'],
    ['https://isee.weishi.qq.com/ws/share/1', 'weishi'],
    ['https://www.acfun.cn/v/ac123', 'acfun'],
    ['https://oasis.weibo.cn/v/123', 'oasis'],
    ['https://channels.weixin.qq.com/web/123', 'channels']
  ];

  for (const [url, expected] of cases) {
    assert.equal(labelPlatform(url), expected, `expected ${url} -> ${expected}`);
  }
});

test('labelPlatform rejects lookalike domains and falls back on unknown or invalid URLs', () => {
  assert.equal(labelPlatform('https://notyoutube.com/watch?v=1'), 'generic');
  assert.equal(labelPlatform('https://example.com/video', 'custom-fallback'), 'custom-fallback');
  assert.equal(labelPlatform('not-a-valid-url'), 'generic');
  assert.equal(labelPlatform('', 'fallback'), 'fallback');
});
