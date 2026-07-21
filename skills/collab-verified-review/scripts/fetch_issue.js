#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');
const https = require('https');

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

// Resolve user data from the active workspace, never from the installed plugin cache.
const PROJECT_ROOT = findWorkspaceRoot(process.env.UI_AUDIT_WORKSPACE || process.cwd());
const LOCAL_DIR = path.join(PROJECT_ROOT, '.ops-local');
const CREDENTIALS_PATH = path.join(LOCAL_DIR, 'cw-credentials.json');
const GITIGNORE_PATH = path.join(PROJECT_ROOT, '.gitignore');
const BASE_URL = 'https://devops.cwoa.net/api/open/CTeam/api/service_open/issue/2.1.0';

function loadCredentials() {
  if (process.env.CW_USER_ID && process.env.CW_ACCESS_TOKEN) {
    return { userId: process.env.CW_USER_ID, token: process.env.CW_ACCESS_TOKEN, source: 'environment' };
  }
  if (!fs.existsSync(CREDENTIALS_PATH)) return null;
  try {
    return JSON.parse(fs.readFileSync(CREDENTIALS_PATH, 'utf8'));
  } catch {
    return null;
  }
}

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

function initCredentialsTemplate() {
  ensureLocalDir();
  if (!fs.existsSync(CREDENTIALS_PATH)) {
    fs.writeFileSync(CREDENTIALS_PATH, JSON.stringify({ userId: '', token: '' }, null, 2), 'utf8');
  }
  ensureGitignoreEntry();
  console.log(`CREDENTIALS_TEMPLATE_CREATED: ${CREDENTIALS_PATH}`);
}

function checkCredentials() {
  const credentials = loadCredentials();
  if (!credentials) {
    console.log(`MISSING_CREDENTIALS: ${CREDENTIALS_PATH}`);
    process.exit(2);
  }
  if (!credentials.userId) {
    console.log('MISSING_CREDENTIALS: userId');
    process.exit(2);
  }
  if (!credentials.token) {
    console.log('MISSING_CREDENTIALS: token');
    process.exit(2);
  }
  console.log(`CREDENTIALS_OK: ${credentials.source || CREDENTIALS_PATH}`);
}

function parseIssueArgument(value, fallbackTeam) {
  if (!/^https?:\/\//i.test(value)) return { issueId: value, team: fallbackTeam || 'aiops' };
  const url = new URL(value);
  const issueId = url.searchParams.get('id');
  const teamMatch = url.pathname.match(/\/vteam\/([^/]+)\//);
  if (!issueId) throw new Error('CTeam URL is missing query parameter: id');
  return { issueId, team: teamMatch ? teamMatch[1] : (fallbackTeam || 'aiops') };
}

function httpGet(targetUrl, headers) {
  return new Promise((resolve, reject) => {
    const parsedUrl = new URL(targetUrl);
    const request = https.request(
      {
        hostname: parsedUrl.hostname,
        path: `${parsedUrl.pathname}${parsedUrl.search}`,
        method: 'GET',
        headers,
      },
      (response) => {
        const chunks = [];
        response.on('data', (chunk) => chunks.push(chunk));
        response.on('end', () => {
          resolve({
            statusCode: response.statusCode,
            body: Buffer.concat(chunks).toString('utf8'),
          });
        });
      }
    );

    request.on('error', reject);
    request.setTimeout(15000, () => {
      request.destroy(new Error('request timeout after 15s'));
    });
    request.end();
  });
}

async function fetchIssue(issueId, team = 'aiops') {
  const credentials = loadCredentials();
  if (!credentials || !credentials.userId || !credentials.token) {
    process.stderr.write(`MISSING_CREDENTIALS: ${CREDENTIALS_PATH}\n`);
    process.exit(2);
  }

  const targetUrl = `${BASE_URL}/${team}/${issueId}/one?userId=${encodeURIComponent(credentials.userId)}`;
  const headers = {
    'X-DEVOPS-ACCESS-TOKEN': credentials.token,
    'Content-Type': 'application/json',
  };

  let result;
  try {
    result = await httpGet(targetUrl, headers);
  } catch (error) {
    process.stderr.write(`ERROR_NETWORK: ${error.message}\n`);
    process.exit(1);
  }

  const { statusCode, body } = result;

  if (statusCode === 200) {
    let data;
    try {
      data = JSON.parse(body);
    } catch {
      process.stderr.write(`ERROR_PARSE: ${body}\n`);
      process.exit(1);
    }

    if (data.status !== 0) {
      process.stderr.write(`ERROR_BUSINESS: code=${data.status} message=${data.message || ''}\n`);
      process.exit(1);
    }

    process.stdout.write(`${JSON.stringify(data, null, 2)}\n`);
    return;
  }

  if (statusCode === 401) {
    process.stderr.write('ERROR_401: token invalid or expired\n');
    process.exit(1);
  }
  if (statusCode === 403) {
    process.stderr.write(`ERROR_403: forbidden team=${team} id=${issueId}\n`);
    process.exit(1);
  }
  if (statusCode === 404) {
    process.stderr.write(`ERROR_404: not found team=${team} id=${issueId}\n`);
    process.exit(1);
  }

  process.stderr.write(`ERROR_HTTP_${statusCode}: ${body}\n`);
  process.exit(1);
}

const [, , command, ...args] = process.argv;

if (!command) {
  process.stderr.write('Usage: node fetch_issue.js <issueId> [team]\n');
  process.stderr.write('   or: node fetch_issue.js <cteamUrl>\n');
  process.stderr.write('   or: node fetch_issue.js --check-credentials\n');
  process.stderr.write('   or: node fetch_issue.js --init-credentials\n');
  process.exit(1);
}

if (command === '--check-credentials') {
  checkCredentials();
} else if (command === '--init-credentials') {
  initCredentialsTemplate();
} else {
  let target;
  try {
    target = parseIssueArgument(command, args[0]);
  } catch (error) {
    process.stderr.write(`ERROR_INPUT: ${error.message}\n`);
    process.exit(1);
  }
  fetchIssue(target.issueId, target.team).catch((error) => {
    process.stderr.write(`UNEXPECTED_ERROR: ${error.message}\n`);
    process.exit(1);
  });
}
