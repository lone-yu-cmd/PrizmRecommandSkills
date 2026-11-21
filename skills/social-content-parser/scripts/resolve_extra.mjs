import { spawn } from 'node:child_process';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36';

const HOST_RULES = [
  ['youtube', ['youtube.com', 'youtu.be', 'music.youtube.com']],
  ['instagram', ['instagram.com', 'instagr.am']],
  ['ixigua', ['ixigua.com']],
  ['zhihu', ['zhihu.com']],
  ['pearvideo', ['pearvideo.com']],
  ['meipai', ['meipai.com']],
  ['huya', ['huya.com']],
  ['jimeng', ['jimeng.jianying.com', 'jimeng.cn', 'dreamina.jianying.com']],
  ['doubao', ['doubao.com']],
  ['quanmin', ['kg.qq.com', 'kg2.qq.com', 'kg3.qq.com', 'node.kg.qq.com']],
  ['kuaishou', ['kuaishou.com', 'chenzhongtech.com', 'gifshow.com', 'kuaishouapp.com']],
  ['tiktok', ['tiktok.com']],
  ['haokan', ['haokan.baidu.com', 'haokan.com']],
  ['weishi', ['weishi.qq.com']],
  ['acfun', ['acfun.cn', 'acfun.tv']],
  ['oasis', ['oasis.weibo.cn']],
  ['channels', ['weixin.qq.com', 'channels.weixin.qq.com']]
];

const COOKIE_FIRST = new Set(['youtube', 'instagram', 'ixigua']);

export function labelPlatform(sourceUrl, fallback = 'generic') {
  let host = '';
  try {
    host = new URL(sourceUrl).hostname.replace(/^www\./, '');
  } catch {
    return fallback;
  }
  for (const [name, hosts] of HOST_RULES) {
    if (hosts.some((known) => host === known || host.endsWith(`.${known}`))) return name;
  }
  return fallback;
}

function run(command, args, timeoutMs) {
  return new Promise((resolve) => {
    const child = spawn(command, args);
    let stdout = '';
    let stderr = '';
    const timer = setTimeout(() => {
      child.kill('SIGKILL');
      stderr += '\nTIMEOUT';
    }, timeoutMs);
    child.stdout.on('data', (chunk) => { stdout += chunk; });
    child.stderr.on('data', (chunk) => { stderr += chunk; });
    child.on('error', (err) => {
      clearTimeout(timer);
      resolve({ code: 127, stdout, stderr: `${stderr}\n${err.message}` });
    });
    child.on('close', (code) => {
      clearTimeout(timer);
      resolve({ code, stdout, stderr });
    });
  });
}

function vendorYtDlp() {
  const name = process.platform === 'win32' ? 'yt-dlp.exe' : 'yt-dlp';
  return path.join(path.dirname(fileURLToPath(import.meta.url)), 'vendor', name);
}

async function ytdlpBin() {
  const candidates = [vendorYtDlp()];
  if (process.env.YT_DLP) candidates.push(process.env.YT_DLP);
  candidates.push(path.join(os.homedir(), '.local/bin/yt-dlp'));
  for (const candidate of candidates) {
    try {
      await fs.access(candidate);
      return candidate;
    } catch {
      // try the next location
    }
  }
  return 'yt-dlp';
}

function pickVideoUrl(info) {
  const formats = Array.isArray(info?.formats) ? info.formats : [];
  const withUrl = formats.filter((item) => item?.url && item.vcodec && item.vcodec !== 'none');
  const progressive = withUrl.filter((item) => item.acodec && item.acodec !== 'none');
  const list = (progressive.length ? progressive : withUrl).filter((item) => !/manifest/i.test(item.url));
  const pool = list.length ? list : withUrl;
  pool.sort((a, b) => (b.height || 0) - (a.height || 0) || (b.tbr || 0) - (a.tbr || 0));
  return pool[0]?.url || info?.url || '';
}

function ytdlpBaseArgs(pageUrl, { browser, youtube }) {
  const args = ['--no-warnings', '--no-playlist'];
  if (youtube) {
    args.push('--js-runtimes', 'node', '--remote-components', 'ejs:github');
  }
  if (browser) args.push('--cookies-from-browser', browser);
  args.push(pageUrl);
  return args;
}

async function resolveYtDlp(pageUrl, platform) {
  const bin = await ytdlpBin();
  const youtube = platform === 'youtube';
  const browsers = COOKIE_FIRST.has(platform) ? ['chrome', null] : [null, 'chrome'];
  let lastError = '';
  for (const browser of browsers) {
    const args = ['--skip-download', '-J', ...ytdlpBaseArgs(pageUrl, { browser, youtube })];
    const result = await run(bin, args, youtube ? 90000 : 45000);
    if (result.code !== 0) {
      lastError = result.stderr.trim().split('\n').filter(Boolean).at(-1) || `yt-dlp exit ${result.code}`;
      continue;
    }
    let info;
    try {
      info = JSON.parse(result.stdout);
    } catch {
      lastError = 'yt-dlp returned non-json';
      continue;
    }
    const video = pickVideoUrl(info);
    if (!video) {
      lastError = 'yt-dlp found no video url';
      continue;
    }
    return {
      mode: 'ytdlp',
      raw: {
        extractor: info.extractor,
        id: info.id,
        title: info.title,
        webpage_url: info.webpage_url || pageUrl
      },
      normalized: {
        platform,
        kind: 'post',
        sourceUrl: pageUrl,
        canonicalUrl: info.webpage_url || pageUrl,
        sourceId: String(info.id || ''),
        code: 200,
        msg: 'yt-dlp',
        type: 'video',
        title: info.title || info.fulltitle || '',
        desc: info.description || '',
        author: {
          name: info.uploader || info.channel || info.creator || '',
          id: info.uploader_id || info.channel_id || ''
        },
        cover: info.thumbnail || '',
        primaryVideo: video,
        fallbackUsed: true,
        meta: {
          downloadVia: platform === 'youtube' || platform === 'instagram' || platform === 'ixigua' ? 'ytdlp' : 'http',
          pageUrl,
          cookiesBrowser: browser || '',
          referer: platform === 'pearvideo' ? 'https://www.pearvideo.com/' : ''
        }
      }
    };
  }
  const error = new Error(lastError || 'yt-dlp failed');
  error.ytdlp = true;
  throw error;
}

function decodeMeipai(value) {
  const hex = value.substring(0, 4).split('').reverse().join('');
  const str = value.substring(4);
  const dec = parseInt(hex, 16).toString();
  const pre = dec.substring(0, 2).split('');
  const tail = dec.substring(2).split('');
  const cut = (input, pos) => {
    const start = Number(pos[0]);
    const length = Number(pos[1]);
    const head = input.substring(0, start);
    const mid = input.substr(start, length);
    return head + input.substring(start).replace(mid, '');
  };
  const stripped = cut(str, pre);
  const pos = tail.slice();
  pos[0] = String(stripped.length - Number(pos[0]) - Number(pos[1]));
  return Buffer.from(cut(stripped, pos), 'base64').toString('utf8');
}

async function fetchText(url, referer) {
  const res = await fetch(url, {
    redirect: 'follow',
    signal: AbortSignal.timeout(20000),
    headers: {
      'user-agent': UA,
      accept: 'text/html,application/json;q=0.9,*/*;q=0.8',
      ...(referer ? { referer } : {})
    }
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.text();
}

function jsonStringField(text, field) {
  const match = text.match(new RegExp(`"${field}":"((?:\\\\.|[^"\\\\])*)"`));
  if (!match) return '';
  try {
    return JSON.parse(`"${match[1]}"`);
  } catch {
    return match[1];
  }
}

async function resolveQuanmin(pageUrl) {
  const text = await fetchText(pageUrl, 'https://kg.qq.com/');
  const video = jsonStringField(text, 'playurl_video');
  if (!video.startsWith('http')) return null;
  return {
    mode: 'page',
    raw: { platform: 'quanmin', playurl_video: video },
    normalized: {
      platform: 'quanmin',
      kind: 'post',
      sourceUrl: pageUrl,
      type: 'video',
      title: jsonStringField(text, 'song_name') || jsonStringField(text, 'content'),
      desc: jsonStringField(text, 'content'),
      author: { name: jsonStringField(text, 'nick') },
      cover: jsonStringField(text, 'cover'),
      primaryVideo: video,
      code: 200,
      msg: 'page',
      fallbackUsed: true,
      meta: { downloadVia: 'http', pageUrl }
    }
  };
}

async function signMeipaiUrl(videoUrl) {
  let current = new URL(videoUrl);
  current.protocol = 'https:';
  current.hostname = 'mvvideo1.meitudata.com';
  for (let hop = 0; hop < 5; hop += 1) {
    const res = await fetch(current, {
      method: 'GET',
      redirect: 'manual',
      signal: AbortSignal.timeout(15000),
      headers: {
        'user-agent': UA,
        referer: 'https://www.meipai.com/'
      }
    });
    if (res.status >= 300 && res.status < 400) {
      const location = res.headers.get('location');
      if (!location) break;
      try {
        current = new URL(location, current);
      } catch {
        return '';
      }
      continue;
    }
    break;
  }
  if (!current.searchParams.has('k')) return '';
  return current.toString();
}

function goodMeipaiFileUrl(videoUrl) {
  try {
    const parsed = new URL(videoUrl);
    return parsed.protocol.startsWith('http')
      && /(^|\.)meitudata\.com$/.test(parsed.hostname)
      && parsed.pathname.endsWith('.mp4');
  } catch {
    return false;
  }
}

async function resolveMeipai(pageUrl) {
  const mediaId = pageUrl.match(/\/(?:media|video)\/(?:\d+\/)?(\d+)/)?.[1] || '';
  const pages = [pageUrl, 'https://www.meipai.com/medias/hot', 'https://www.meipai.com/square'];
  const encodedList = [];
  let pageText = '';
  for (const page of pages) {
    let text = '';
    try {
      text = await fetchText(page, 'https://www.meipai.com/');
      pageText += text;
    } catch {
      continue;
    }
    if (mediaId) {
      const tagged = text.match(new RegExp(`data-id="${mediaId}"[^>]*data-video="([^"]+)"`));
      if (tagged) encodedList.push(tagged[1]);
    } else {
      encodedList.push(...[...text.matchAll(/data-video="([^"]+)"/g)].map((match) => match[1]));
    }
    if (encodedList.length && (mediaId || page === pageUrl)) break;
  }
  for (const encoded of encodedList) {
    let video = '';
    try {
      video = decodeMeipai(encoded);
    } catch {
      continue;
    }
    if (!goodMeipaiFileUrl(video)) continue;
    const signed = await signMeipaiUrl(video);
    if (!goodMeipaiFileUrl(signed)) continue;
    const around = pageText.slice(pageText.indexOf(encoded), pageText.indexOf(encoded) + 800);
    const title = around.match(/title="([^"]+)"/)?.[1] || '';
    return {
      mode: 'page',
      raw: { platform: 'meipai', id: mediaId, dataVideo: encoded },
      normalized: {
        platform: 'meipai',
        kind: 'post',
        sourceUrl: pageUrl,
        type: 'video',
        title,
        primaryVideo: signed,
        code: 200,
        msg: 'page',
        fallbackUsed: true,
        meta: { downloadVia: 'http', pageUrl, referer: 'https://www.meipai.com/' }
      }
    };
  }
  return null;
}

async function resolveIxigua(pageUrl) {
  const id = pageUrl.match(/(\d{16,})/)?.[1];
  if (!id) return null;
  const api = new URL('https://api.bugpk.com/api/short_videos');
  api.searchParams.set('url', `https://www.douyin.com/video/${id}`);
  const res = await fetch(api, {
    signal: AbortSignal.timeout(20000),
    headers: {
      accept: 'application/json, text/plain, */*',
      'user-agent': UA,
      referer: 'https://api.bugpk.com/'
    }
  });
  if (!res.ok) return null;
  const payload = await res.json();
  const data = payload?.data;
  const video = data?.url || data?.video_url || '';
  if (Number(payload?.code) !== 200 || !video) return null;
  const author = data.author && typeof data.author === 'object' ? data.author : {};
  return {
    mode: 'ixigua-douyin',
    raw: payload,
    normalized: {
      platform: 'ixigua',
      kind: 'post',
      sourceUrl: pageUrl,
      type: data.type || 'video',
      title: data.title || data.desc || '',
      desc: data.desc || '',
      author: {
        name: author.name || data.author || '',
        id: author.id || '',
        avatar: author.avatar || data.avatar || ''
      },
      cover: data.cover || '',
      primaryVideo: video,
      images: Array.isArray(data.images) ? data.images : [],
      code: 200,
      msg: payload.msg || 'ixigua',
      fallbackUsed: true,
      meta: { downloadVia: 'http', pageUrl }
    }
  };
}

export async function resolveExtra(pageUrl) {
  const platform = labelPlatform(pageUrl, 'generic');
  if (platform === 'ixigua') {
    const parsed = await resolveIxigua(pageUrl);
    if (parsed) return parsed;
  }
  if (platform === 'quanmin') {
    const parsed = await resolveQuanmin(pageUrl);
    if (parsed) return parsed;
  }
  if (platform === 'meipai') {
    const parsed = await resolveMeipai(pageUrl);
    if (parsed) return parsed;
  }
  try {
    return await resolveYtDlp(pageUrl, platform);
  } catch (err) {
    if (platform === 'generic') return null;
    if (/Unsupported URL|No video formats/i.test(String(err.message))) return null;
    throw err;
  }
}

export async function downloadWithYtDlp(pageUrl, filePath, browser) {
  const bin = await ytdlpBin();
  const platform = labelPlatform(pageUrl, 'generic');
  await fs.mkdir(path.dirname(filePath), { recursive: true });
  const args = [
    '-f', 'bv*+ba/b',
    '--merge-output-format', 'mp4',
    '-o', filePath,
    ...ytdlpBaseArgs(pageUrl, { browser: browser || null, youtube: platform === 'youtube' })
  ];
  const result = await run(bin, args, 180000);
  if (result.code !== 0) {
    throw new Error(result.stderr.trim().split('\n').filter(Boolean).at(-1) || 'yt-dlp download failed');
  }
  return filePath;
}
