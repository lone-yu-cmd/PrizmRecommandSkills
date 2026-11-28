import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import fs from 'node:fs/promises';
import http from 'node:http';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

import {
  assetName,
  download,
  installedVersion,
  vendorPath
} from '../scripts/ensure_runtime.mjs';

const TEST_DIR = path.dirname(fileURLToPath(import.meta.url));
const SCRIPT_PATH = path.resolve(TEST_DIR, '..', 'scripts', 'ensure_runtime.mjs');

function run(command, args) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, { stdio: ['ignore', 'pipe', 'pipe'] });
    let stdout = '';
    let stderr = '';
    child.stdout.on('data', (chunk) => { stdout += chunk; });
    child.stderr.on('data', (chunk) => { stderr += chunk; });
    child.on('error', reject);
    child.on('close', (code) => resolve({ code, stdout, stderr }));
  });
}

test('assetName returns expected yt-dlp release asset for current platform', () => {
  const asset = assetName();
  if (process.platform === 'darwin') {
    assert.equal(asset, 'yt-dlp_macos');
  } else if (process.platform === 'win32') {
    assert.equal(asset, 'yt-dlp.exe');
  } else if (process.platform === 'linux') {
    assert.match(asset, /^yt-dlp_linux/);
  }
});

test('vendorPath resolves inside scripts/vendor', () => {
  const expectedName = process.platform === 'win32' ? 'yt-dlp.exe' : 'yt-dlp';
  assert.equal(
    vendorPath(),
    path.resolve(TEST_DIR, '..', 'scripts', 'vendor', expectedName)
  );
});

test('installedVersion handles executable, failing executable, and missing binary', async () => {
  const tempDir = await fs.mkdtemp(path.join(os.tmpdir(), 'ensure-runtime-ver-'));
  try {
    const okBin = path.join(tempDir, 'fake-ytdlp-ok.sh');
    await fs.writeFile(okBin, '#!/bin/sh\necho "  2026.10.21  "\n');
    await fs.chmod(okBin, 0o755);
    assert.equal(await installedVersion(okBin), '2026.10.21');

    const failBin = path.join(tempDir, 'fake-ytdlp-fail.sh');
    await fs.writeFile(failBin, '#!/bin/sh\nexit 1\n');
    await fs.chmod(failBin, 0o755);
    assert.equal(await installedVersion(failBin), '');

    assert.equal(await installedVersion(path.join(tempDir, 'missing-bin')), '');
  } finally {
    await fs.rm(tempDir, { recursive: true, force: true });
  }
});

test('download validates HTTP errors, payload size, and writes executable file', async () => {
  const tempDir = await fs.mkdtemp(path.join(os.tmpdir(), 'ensure-runtime-dl-'));
  const server = http.createServer((req, res) => {
    if (req.url === '/not-found') {
      res.writeHead(404);
      res.end('missing');
      return;
    }
    if (req.url === '/too-small') {
      res.writeHead(200);
      res.end('tiny');
      return;
    }
    if (req.url === '/valid') {
      res.writeHead(200);
      res.end(Buffer.alloc(120000, 0x41));
      return;
    }
    res.writeHead(500);
    res.end('unexpected');
  });
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));

  try {
    const { port } = server.address();
    const base = `http://127.0.0.1:${port}`;

    await assert.rejects(
      download(`${base}/not-found`, path.join(tempDir, 'a')),
      /download failed HTTP 404/
    );
    await assert.rejects(
      download(`${base}/too-small`, path.join(tempDir, 'b')),
      /not a yt-dlp binary/
    );

    const dest = path.join(tempDir, 'yt-dlp-downloaded');
    await download(`${base}/valid`, dest);
    const stat = await fs.stat(dest);
    assert.equal(stat.size, 120000);
    if (process.platform !== 'win32') {
      assert.equal(stat.mode & 0o111, 0o111);
    }
  } finally {
    await new Promise((resolve) => server.close(resolve));
    await fs.rm(tempDir, { recursive: true, force: true });
  }
});

test('CLI reports installed vendored yt-dlp offline', async () => {
  const result = await run(process.execPath, [SCRIPT_PATH]);
  assert.equal(result.code, 0, result.stderr);
  assert.match(result.stdout, /^node v/m);
  assert.match(result.stdout, /^yt-dlp \S+ at /m);
  assert.match(result.stdout, /Chrome cookies for YouTube and Instagram/);
});
