# CTeam 接口说明与凭证管理

## 接口信息

### 获取单据详情

```text
GET https://devops.cwoa.net/api/open/CTeam/api/service_open/issue/2.1.0/{team}/{issueId}/one?userId={userId}
```

参数说明：

| 参数 | 位置 | 说明 |
|------|------|------|
| `team` | 路径 | 项目团队标识，从单据 URL 的 `/vteam/{team}/` 提取，默认 `aiops` |
| `issueId` | 路径 | 单据 ID，从 URL query 参数 `id` 提取（32 位十六进制字符串） |
| `userId` | query | CW 用户名，从凭证文件读取 |
| `X-DEVOPS-ACCESS-TOKEN` | Header | 访问 Token，从凭证文件读取 |

接口文档：<https://devops.cwoa.net/open/document.html#/b3b7eb0851f642a9a0a47d4c56827585>

## 图片与附件读取说明

- 单据详情接口适合获取 `title`、`desc`、`stateCn`、`priorityCn` 等结构化字段。
- 若 `desc` 中出现 Markdown 图片或 `/ms/vteam/api/user/file/{team}/download/{fileId}` 一类下载链接，默认只将其视为图片路径线索。
- 默认不再假设仅凭 `userId + X-DEVOPS-ACCESS-TOKEN` 就能直接读取图片附件；图片下载需要另一套网页登录态。
- 当前默认主路径已验证可行：使用 `./.ops-local/cw-browser-login.json` 中的 `loginUrl + username + password`，在终端中模拟登录获取会话 cookie，再直接请求图片下载地址并落盘到 `.temp/`。
- 当前插件对外只保留一个入口：`collab-verified-review`；CTeam 是主 Skill 的内部取证能力。
- 处理图文型单据时，默认采用：
  1. 先通过 Open API 获取单据骨架
  2. 再通过终端脚本模拟登录并下载图片内容
  3. 只有当终端链路仍不足以支持判断时，才补充其他信息源

## 响应结构

```json
{
  "status": 0,
  "message": "string",
  "data": {
    "id": "e25a0761332049cab9fe4cc02fd498dc",
    "title": "工作项标题",
    "desc": "工作项描述（Markdown 格式）",
    "typeClassify": "DEMAND",
    "priority": "CENTRAL",
    "priorityCn": "中",
    "state": "68b20f90ac3749cd8700436362a4aa42",
    "stateCn": "Backlog",
    "number": "p195_113",
    "projectId": "gdcaa5",
    "assignId": "zhangsan",
    "createUser": "zhangsan",
    "createTime": "2023-01-01 00:00:00",
    "updateUser": "zhangsan",
    "updateTime": "2023-01-01 00:00:00",
    "fileId": "附件 ID 列表，逗号分隔",
    "parentId": "父工作项 ID"
  }
}
```

## 凭证管理

### 存储位置

凭证保存在项目根目录：

```text
{项目根目录}/.ops-local/cw-credentials.json
```

首次执行 `--init-credentials` 时，脚本会自动确保 `.ops-local/` 已存在；若项目根目录存在 `.git` 且 `.gitignore` 中还没有 `.ops-local/`，脚本会自动补充忽略规则，确保凭证不会被 git 追踪提交。也可以使用 `CW_USER_ID` 与 `CW_ACCESS_TOKEN` 环境变量，不生成凭证文件。

### 凭证文件格式

```json
{
  "userId": "your-username",
  "token": "your-access-token"
}
```

## 登录配置管理

### 存储位置

```text
{项目根目录}/.ops-local/cw-browser-login.json
```

### 登录配置文件格式

```json
{
  "loginUrl": "https://paas.cwoa.net/login/",
  "username": "your-username",
  "password": "your-password"
}
```

### 用途说明

- 这份配置用于终端里模拟网页登录并获取会话 cookie
- 当前默认由 `fetch_issue_image.js` 复用，不要求先启动页面会话
- 若文件缺失，取得用户同意后再执行脚本初始化模板，由用户在本地填写

### 凭证缺失时的处理流程

当脚本返回 `MISSING_CREDENTIALS` 时：

1. 告知用户需要配置 CW 平台凭证，并询问用户选择以下方向：
2. `创建模板文件（推荐）`
3. `本次跳过（仅保留当前可读取信息）`
4. `其他（请描述）`
5. 若用户选择 `创建模板文件`：先在 `{项目根目录}/.ops-local/cw-credentials.json` 创建以下模板：
6. 若项目根目录存在 `.git` 且 `.gitignore` 中还没有 `.ops-local/`，则同时写入 `.ops-local/` 忽略规则，并明确告知用户已补写。
7. 若用户选择 `本次跳过（仅保留当前可读取信息）`：本轮跳过接口链路，并在输出中明确写出“接口结构化字段未补齐”。

```json
{
  "userId": "",
  "token": ""
}
```

8. 明确引导用户：
9. `userId` 填 CW 用户名。
10. `token` 填 `X-DEVOPS-ACCESS-TOKEN`。
11. token 获取地址是 `https://devops.cwoa.net/devops/console/userCenter/userToken`。
12. 在用户确认文件已填写完成前，暂停接口读取。
13. 用户确认后，重新执行凭证检查。不要让用户在聊天中粘贴 token；优先由用户直接填写本地模板，或设置环境变量。

```bash
node <skill-dir>/scripts/fetch_issue.js --init-credentials
```

14. 保存成功或模板填写完成后，重新获取单据详情。

## 常见错误处理

| 错误输出 | 原因 | 处理方式 |
|---------|------|---------|
| `ERROR_401` | token 无效或过期 | 请用户重新生成 token，重新保存凭证 |
| `ERROR_403` | 无权限访问 | 确认 team 名称是否正确，或是否有访问权限 |
| `ERROR_404` | 单据不存在 | 确认 issueId 是否正确 |
| `ERROR_BUSINESS` | 接口业务错误 | 输出 `code` 和 `message` 供用户判断 |
| `ERROR_NETWORK` | 网络连接失败 | 检查网络，确认是否需要 VPN |
| `ERROR_PARSE` | 响应非 JSON | 可能接口异常，原始响应已输出 |

图片脚本返回 `ERROR_HTTP_401` 时，说明配置文件存在但网页登录认证未成功或已过期。更新本地登录配置后只重试一次；仍失败且 Chrome 已登录时，按 `SKILL.md` 的 CDP Bridge 独立标签页回退流程读取图片。

## 脚本调用

```bash
node <skill-dir>/scripts/fetch_issue.js --check-credentials
node <skill-dir>/scripts/fetch_issue.js --init-credentials
node <skill-dir>/scripts/fetch_issue.js 4cb92f2552394cc1800923ef42464a4d aiops
node <skill-dir>/scripts/fetch_issue.js "https://devops.cwoa.net/devops/console/vteam/m68126/twDemand?id=..."
node <skill-dir>/scripts/fetch_issue_image.js --check-login-config
node <skill-dir>/scripts/fetch_issue_image.js --init-login-config
node <skill-dir>/scripts/fetch_issue_image.js https://devops.cwoa.net/ms/vteam/api/user/file/m68126/download/abc123
```

依赖：Node.js >= 18。
