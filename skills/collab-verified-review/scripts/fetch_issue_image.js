#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');
const https = require('https');
const crypto = require('crypto');

function fileExists(rootDir, relativePath) {
  return fs.existsSync(path.join(rootDir, relativePath));
}

function findWorkspaceRoot(startDir) {
  let currentDir = path.resolve(startDir);
  while (true) {
    if (
      fileExists(currentDir, '.git') ||
      fileExists(currentDir, '.github') ||
      fileExists(currentDir, 'AGENTS.md') ||
      fileExists(currentDir, 'CLAUDE.md')
    ) {
      return currentDir;
    }
    const parentDir = path.dirname(currentDir);
    if (parentDir === currentDir) return path.resolve(startDir);
    currentDir = parentDir;
  }
}

// Keep credentials and downloaded evidence in the user's active workspace.
const PROJECT_ROOT = findWorkspaceRoot(process.env.UI_AUDIT_WORKSPACE || process.cwd());
const LOCAL_DIR = path.join(PROJECT_ROOT, '.ops-local');
const LOGIN_CONFIG_PATH = path.join(LOCAL_DIR, 'cw-browser-login.json');
const GITIGNORE_PATH = path.join(PROJECT_ROOT, '.gitignore');
const TEMP_DIR = path.join(PROJECT_ROOT, '.temp', 'cteam');

function ensureLocalDir() {
  fs.mkdirSync(LOCAL_DIR, { recursive: true });
}

function ensureGitignoreEntry() {
  const entry = '.ops-local/';
  const comment = '# Local ops data\n';

  if (!fs.existsSync(GITIGNORE_PATH)) {
    fs.writeFileSync(GITIGNORE_PATH, `${comment}${entry}\n`, 'utf8');
    return;
  }

  const content = fs.readFileSync(GITIGNORE_PATH, 'utf8');
  if (!content.includes(entry)) {
    const prefix = content.endsWith('\n') ? '' : '\n';
    fs.appendFileSync(GITIGNORE_PATH, `${prefix}${comment}${entry}\n`, 'utf8');
  }
}

function loadLoginConfig() {
  if (process.env.CW_LOGIN_URL && process.env.CW_USERNAME && process.env.CW_PASSWORD) {
    return {
      loginUrl: process.env.CW_LOGIN_URL,
      username: process.env.CW_USERNAME,
      password: process.env.CW_PASSWORD,
      source: 'environment',
    };
  }
  if (!fs.existsSync(LOGIN_CONFIG_PATH)) {
    return null;
  }

  try {
    return JSON.parse(fs.readFileSync(LOGIN_CONFIG_PATH, 'utf8'));
  } catch {
    return null;
  }
}

function checkLoginConfig() {
  const config = loadLoginConfig();
  if (!config) {
    console.log(`MISSING_LOGIN_CONFIG: ${LOGIN_CONFIG_PATH}`);
    process.exit(2);
  }
  if (!config.loginUrl) {
    console.log('MISSING_LOGIN_CONFIG: loginUrl');
    process.exit(2);
  }
  if (!config.username) {
    console.log('MISSING_LOGIN_CONFIG: username');
    process.exit(2);
  }
  if (!config.password) {
    console.log('MISSING_LOGIN_CONFIG: password');
    process.exit(2);
  }
  console.log(`LOGIN_CONFIG_OK: ${config.source || LOGIN_CONFIG_PATH}`);
}

function initLoginConfigTemplate() {
  ensureLocalDir();
  if (!fs.existsSync(LOGIN_CONFIG_PATH)) {
    fs.writeFileSync(
      LOGIN_CONFIG_PATH,
      JSON.stringify({ loginUrl: '', username: '', password: '' }, null, 2),
      'utf8'
    );
  }
  ensureGitignoreEntry();
  console.log(`LOGIN_CONFIG_TEMPLATE_CREATED: ${LOGIN_CONFIG_PATH}`);
}

function parseSetCookieHeader(setCookieHeaders) {
  const cookies = [];
  for (const header of setCookieHeaders || []) {
    const parts = header.split(';').map(item => item.trim()).filter(Boolean);
    if (!parts.length) continue;
    const [nameValue, ...attributes] = parts;
    const separatorIndex = nameValue.indexOf('=');
    if (separatorIndex === -1) continue;
    const cookie = {
      name: nameValue.slice(0, separatorIndex),
      value: nameValue.slice(separatorIndex + 1),
      domain: null,
      path: '/',
      secure: false
    };

    for (const attribute of attributes) {
      const [attributeName, ...attributeValueParts] = attribute.split('=');
      const key = attributeName.toLowerCase();
      const value = attributeValueParts.join('=');
      if (key === 'domain') cookie.domain = value.toLowerCase();
      if (key === 'path') cookie.path = value || '/';
      if (key === 'secure') cookie.secure = true;
    }
    cookies.push(cookie);
  }
  return cookies;
}

class CookieJar {
  constructor() {
    this.cookies = [];
  }

  storeFromResponse(urlString, setCookieHeaders) {
    const url = new URL(urlString);
    for (const cookie of parseSetCookieHeader(setCookieHeaders)) {
      cookie.domain = cookie.domain || url.hostname.toLowerCase();
      this.cookies = this.cookies.filter(existing => {
        return !(
          existing.name === cookie.name &&
          existing.domain === cookie.domain &&
          existing.path === cookie.path
        );
      });
      this.cookies.push(cookie);
    }
  }

  getCookieHeader(urlString) {
    const url = new URL(urlString);
    const isHttps = url.protocol === 'https:';
    const hostname = url.hostname.toLowerCase();
    const pathname = url.pathname || '/';

    return this.cookies
      .filter(cookie => {
        if (cookie.secure && !isHttps) return false;
        if (!hostnameMatches(hostname, cookie.domain)) return false;
        return pathname.startsWith(cookie.path || '/');
      })
      .map(cookie => `${cookie.name}=${cookie.value}`)
      .join('; ');
  }
}

function hostnameMatches(hostname, domain) {
  const normalizedDomain = (domain || '').replace(/^\./, '').toLowerCase();
  return hostname === normalizedDomain || hostname.endsWith(`.${normalizedDomain}`);
}

function httpRequest(targetUrl, options = {}) {
  const url = new URL(targetUrl);
  const method = options.method || 'GET';
  const headers = { ...(options.headers || {}) };
  const body = options.body || null;

  if (body && !headers['Content-Length']) {
    headers['Content-Length'] = Buffer.byteLength(body);
  }

  return new Promise((resolve, reject) => {
    const request = https.request(
      {
        hostname: url.hostname,
        port: url.port || 443,
        path: `${url.pathname}${url.search}`,
        method,
        headers,
      },
      response => {
        const chunks = [];
        response.on('data', chunk => chunks.push(chunk));
        response.on('end', () => {
          resolve({
            statusCode: response.statusCode,
            headers: response.headers,
            body: Buffer.concat(chunks),
          });
        });
      }
    );

    request.on('error', reject);
    request.setTimeout(20000, () => {
      request.destroy(new Error('request timeout after 20s'));
    });
    if (body) {
      request.write(body);
    }
    request.end();
  });
}

function parseLoginPage(html) {
  return {
    csrfToken: matchFirstGroup(html, /name="csrfmiddlewaretoken" value="([^"]+)"/),
    appId: matchFirstGroup(html, /name="app_id" value="([^"]*)"/) || 'None',
    publicKeyBase64: matchFirstGroup(html, /PASSWORD_RSA_PUBLIC_KEY = "([^"]+)"/),
  };
}

function matchFirstGroup(text, regex) {
  const match = text.match(regex);
  return match ? match[1] : '';
}

function encryptPassword(publicKeyBase64, password) {
  const pem = Buffer.from(publicKeyBase64, 'base64').toString('utf8');
  return crypto
    .publicEncrypt(
      {
        key: pem,
        padding: crypto.constants.RSA_PKCS1_PADDING,
      },
      Buffer.from(password, 'utf8')
    )
    .toString('base64');
}

async function loginWithConfig(config) {
  const cookieJar = new CookieJar();
  const loginUrl = config.loginUrl;
  const loginPage = await httpRequest(loginUrl, {
    headers: {
      'User-Agent': 'collab-verified-review/cteam-reader',
    },
  });
  cookieJar.storeFromResponse(loginUrl, loginPage.headers['set-cookie']);

  if (loginPage.statusCode !== 200) {
    throw new Error(`unexpected login page status: ${loginPage.statusCode}`);
  }

  const loginPageHtml = loginPage.body.toString('utf8');
  const { csrfToken, appId, publicKeyBase64 } = parseLoginPage(loginPageHtml);
  if (!csrfToken || !publicKeyBase64) {
    throw new Error('failed to parse login page csrf token or public key');
  }

  const encryptedPassword = encryptPassword(publicKeyBase64, config.password);
  const formData = new URLSearchParams({
    csrfmiddlewaretoken: csrfToken,
    username: config.username,
    password: encryptedPassword,
    next: '',
    app_id: appId,
  }).toString();

  const postHeaders = {
    'User-Agent': 'collab-verified-review/cteam-reader',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Referer': loginUrl,
  };
  const loginCookies = cookieJar.getCookieHeader(loginUrl);
  if (loginCookies) {
    postHeaders.Cookie = loginCookies;
  }

  const loginResp = await httpRequest(loginUrl, {
    method: 'POST',
    headers: postHeaders,
    body: formData,
  });
  cookieJar.storeFromResponse(loginUrl, loginResp.headers['set-cookie']);

  if (![200, 302, 303].includes(loginResp.statusCode)) {
    throw new Error(`unexpected login submit status: ${loginResp.statusCode}`);
  }

  let redirectUrl = resolveRedirectUrl(loginUrl, loginResp.headers.location);
  let redirectCount = 0;
  while (redirectUrl && redirectCount < 5) {
    const redirectHeaders = {
      'User-Agent': 'collab-verified-review/cteam-reader',
    };
    const cookieHeader = cookieJar.getCookieHeader(redirectUrl);
    if (cookieHeader) {
      redirectHeaders.Cookie = cookieHeader;
    }
    const redirectResp = await httpRequest(redirectUrl, { headers: redirectHeaders });
    cookieJar.storeFromResponse(redirectUrl, redirectResp.headers['set-cookie']);
    redirectUrl = resolveRedirectUrl(redirectUrl, redirectResp.headers.location);
    redirectCount += 1;
  }

  return cookieJar;
}

function resolveRedirectUrl(baseUrl, locationHeader) {
  if (!locationHeader) return '';
  return new URL(locationHeader, baseUrl).toString();
}

function normalizeImageUrl(input) {
  if (!input) return '';
  if (/^https?:\/\//i.test(input)) return input;
  if (input.startsWith('/')) {
    return `https://devops.cwoa.net${input}`;
  }
  return `https://devops.cwoa.net/${input.replace(/^\/+/, '')}`;
}

function guessExtension(contentType, buffer) {
  if (contentType) {
    if (contentType.includes('png')) return '.png';
    if (contentType.includes('jpeg') || contentType.includes('jpg')) return '.jpg';
    if (contentType.includes('gif')) return '.gif';
    if (contentType.includes('webp')) return '.webp';
    if (contentType.includes('svg')) return '.svg';
  }

  const signature = buffer.subarray(0, 8).toString('hex').toUpperCase();
  if (signature.startsWith('89504E470D0A1A0A')) return '.png';
  if (signature.startsWith('FFD8FF')) return '.jpg';
  if (signature.startsWith('47494638')) return '.gif';
  if (signature.startsWith('52494646')) return '.webp';
  return '.bin';
}

function buildOutputPath(imageUrl, requestedOutputPath, responseBuffer, contentType) {
  if (requestedOutputPath) {
    return path.isAbsolute(requestedOutputPath)
      ? requestedOutputPath
      : path.join(PROJECT_ROOT, requestedOutputPath);
  }

  fs.mkdirSync(TEMP_DIR, { recursive: true });
  const fileId = imageUrl.split('/').pop().split('?')[0] || `issue-image-${Date.now()}`;
  const extension = guessExtension(contentType, responseBuffer);
  return path.join(TEMP_DIR, `cteam-image-${fileId}${extension}`);
}

async function fetchIssueImage(imageUrlInput, outputPathInput) {
  const config = loadLoginConfig();
  if (!config || !config.loginUrl || !config.username || !config.password) {
    process.stderr.write(`MISSING_LOGIN_CONFIG: ${LOGIN_CONFIG_PATH}\n`);
    process.exit(2);
  }

  const imageUrl = normalizeImageUrl(imageUrlInput);
  const cookieJar = await loginWithConfig(config);
  const headers = {
    'User-Agent': 'collab-verified-review/cteam-reader',
  };
  const cookieHeader = cookieJar.getCookieHeader(imageUrl);
  if (cookieHeader) {
    headers.Cookie = cookieHeader;
  }

  const imageResp = await httpRequest(imageUrl, { headers });
  if (imageResp.statusCode !== 200) {
    process.stderr.write(`ERROR_HTTP_${imageResp.statusCode}: ${imageResp.body.toString('utf8')}\n`);
    process.exit(1);
  }

  const contentType = imageResp.headers['content-type'] || '';
  const outputPath = buildOutputPath(imageUrl, outputPathInput, imageResp.body, contentType);
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.writeFileSync(outputPath, imageResp.body);

  process.stdout.write(
    `${JSON.stringify({
      ok: true,
      status: imageResp.statusCode,
      contentType,
      url: imageUrl,
      outputPath,
      size: imageResp.body.length,
    }, null, 2)}\n`
  );
}

const [, , command, ...args] = process.argv;

if (!command) {
  process.stderr.write('Usage: node fetch_issue_image.js <imageUrl> [outputPath]\n');
  process.stderr.write('   or: node fetch_issue_image.js --check-login-config\n');
  process.stderr.write('   or: node fetch_issue_image.js --init-login-config\n');
  process.exit(1);
}

if (command === '--check-login-config') {
  checkLoginConfig();
} else if (command === '--init-login-config') {
  initLoginConfigTemplate();
} else {
  fetchIssueImage(command, args[0]).catch(error => {
    process.stderr.write(`UNEXPECTED_ERROR: ${error.message}\n`);
    process.exit(1);
  });
}
