#!/usr/bin/env node
// Install the official standalone yt-dlp into scripts/vendor for this skill.
// Usage: node scripts/ensure_runtime.mjs

import { spawn } from 'node:child_process';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const RELEASE = 'https://github.com/yt-dlp/yt-dlp/releases/latest/download';

function assetName() {
  if (process.platform === 'win32') return 'yt-dlp.exe';
  if (process.platform === 'darwin') return 'yt-dlp_macos';
  if (process.platform === 'linux') {
    if (process.arch === 'arm64') return 'yt-dlp_linux_aarch64';
    if (process.arch === 'arm') return 'yt-dlp_linux_armv7l';
    return 'yt-dlp_linux';
  }
  return '';
}

function vendorPath() {
  const name = process.platform === 'win32' ? 'yt-dlp.exe' : 'yt-dlp';
  return path.join(path.dirname(fileURLToPath(import.meta.url)), 'vendor', name);
}

function run(command, args) {
  return new Promise((resolve) => {
    const child = spawn(command, args);
    let stdout = '';
    let stderr = '';
    child.stdout.on('data', (chunk) => { stdout += chunk; });
    child.stderr.on('data', (chunk) => { stderr += chunk; });
    child.on('error', (err) => resolve({ code: 127, stdout, stderr: err.message }));
    child.on('close', (code) => resolve({ code, stdout, stderr }));
  });
}

async function installedVersion(bin) {
  const result = await run(bin, ['--version']);
  if (result.code !== 0) return '';
  return result.stdout.trim();
}

async function download(url, dest) {
  const response = await fetch(url, {
    redirect: 'follow',
    headers: { 'user-agent': 'social-content-parser' }
  });
  if (!response.ok) {
    throw new Error(`download failed HTTP ${response.status} for ${url}`);
  }
  const bytes = Buffer.from(await response.arrayBuffer());
  if (bytes.length < 100000) {
    throw new Error(`download was only ${bytes.length} bytes, not a yt-dlp binary`);
  }
  await fs.writeFile(dest, bytes);
  if (process.platform !== 'win32') await fs.chmod(dest, 0o755);
}

async function main() {
  console.log(`node ${process.version}`);
  const bin = vendorPath();
  const existing = await installedVersion(bin);
  if (existing) {
    console.log(`yt-dlp ${existing} at ${bin}`);
    console.log('Chrome cookies for YouTube and Instagram stay in the local Chrome profile.');
    return;
  }

  const asset = assetName();
  if (!asset) {
    throw new Error(`no standalone yt-dlp build for ${process.platform}/${process.arch}`);
  }
  await fs.mkdir(path.dirname(bin), { recursive: true });
  const url = `${RELEASE}/${asset}`;
  console.log(`downloading ${url}`);
  await download(url, bin);
  const version = await installedVersion(bin);
  if (!version) {
    await fs.rm(bin, { force: true });
    throw new Error(`downloaded yt-dlp at ${bin} did not run`);
  }
  console.log(`yt-dlp ${version} at ${bin}`);
  console.log('Chrome cookies for YouTube and Instagram stay in the local Chrome profile.');
}

main().catch((err) => {
  console.error(err?.message || err);
  process.exit(1);
});
