# Collab Verified Review

面向 `auto-ops` 前端的 Codex 代码审查专家插件。它把需求事实、Figma、代码 diff、项目契约和真实浏览器行为放进同一条证据链，主动验证疑似缺陷，而不是只做静态评论。

## 使用

推荐从总控 Skill `collab-verified-review` 开始。插件同时保留 5 个职责明确的内部专家 Skill，供总控编排，也可在需要时单独调用。

```text
$collab-verified-review
需求：<CTeam 链接或文字>
Figma：<目标节点链接>
页面：<测试环境 URL>
请 review 当前分支相对基线的 diff。
```

第一阶段只识别、验证和报告，不改业务代码；用户明确批准具体问题后，第二阶段才执行最小修复与回归。

## 内置能力

- CTeam：读取字段、Markdown 正文和内嵌图片。
- Figma MCP：读取目标节点、尺寸、样式和状态。
- CDP Bridge MCP：复用已登录 Chrome，按明确 `tab_id` 验证页面、网络与交互。
- CWUI Knowledge MCP：核对 `@canway/cw-magic-vue` 组件契约和 CW UI/UX 规范。
- 确定性脚本：环境诊断、报告证据门禁、可移植性检查和发布打包。

## 首次配置

1. 安装插件并重新加载 Codex。
2. 在 Chrome 打开 `chrome://extensions/`，开启开发者模式，加载插件内的 `assets/cdp-bridge-extension/`。
3. 按本机方式完成 Figma 授权。
4. CTeam 凭证保存在当前工作区 `.ops-local/`，不得写入插件目录。
5. 运行：

```powershell
py -3 scripts/doctor.py --require-connected
```

## 结构

```text
.codex-plugin/plugin.json       # 插件清单
.mcp.json                       # Figma、CDP Bridge、CWUI MCP
skills/collab-verified-review/  # 总控入口与共享 playbook
skills/collab-review-context/   # 最小上下文专家
skills/collab-review-hypothesis/# 风险假设专家
skills/collab-static-verify/    # 静态验证专家
skills/collab-ui-verify/        # 页面实证专家
skills/collab-review-report/    # 报告汇总专家
assets/cdp-bridge-extension/    # 配套 Chrome 扩展
assets/review-report-template.md
scripts/                        # doctor、证据校验、打包与可移植性检查
```

## 发布

```powershell
py -3 scripts/check_portability.py
py -3 scripts/package_plugin.py
```

生成的 ZIP 不包含凭证、虚拟环境、历史报告或测试现场。
