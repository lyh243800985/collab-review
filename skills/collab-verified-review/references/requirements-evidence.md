# 需求证据

输入包含 `devops.cwoa.net`、CTeam 或 CW 单据链接时，先建立需求事实，再解释 diff。

## 读取顺序

1. 从链接提取 query `id` 和 `/vteam/{team}/`。
2. 在用户当前工作区运行：

```powershell
node <skill-dir>/scripts/fetch_issue.js "<cteam-url>"
```

3. 从返回值提取编号、标题、状态、优先级、正文、负责人和需求类型。
4. 正文包含图片时，使用 `fetch_issue_image.js` 下载到当前工作区 `.temp/cteam/`，并实际查看图片。
5. 下载认证失败而 Chrome 已登录时，使用 CDP Bridge 在独立标签页打开图片并截图；把该证据标记为浏览器登录态回退，不冒充原附件下载。

凭证只从当前工作区 `.ops-local/` 或环境变量读取。不要在输出中展示 token、密码、Cookie 或完整认证响应。需要配置细节时读取 [cteam-api-guide.md](cteam-api-guide.md)。

## 事实分层

```yaml
ticket_facts: []
image_facts: []
figma_facts: []
repository_facts: []
inferences: []
unknowns: []
```

正文有影响验收判断的图片但尚未读取时，需求范围只能标记为不完整。
