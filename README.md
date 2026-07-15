# Collab Verified Review

面向 `auto-ops` 前端的、以证据为依据的代码 diff review 技能。它不止阅读 diff：先建立与变更直接相关的最小上下文，再把风险变成可验证的假设，并尽量用静态检查、接口证据和真实页面操作确认结论。

## 使用入口

对外只暴露一个技能：`collab-verified-review`。

```text
$collab-verified-review <需求/单据/页面链接/待审 diff>
```

例如：

```text
$collab-verified-review
需求：p176_6942 网段搜索展示所属分组层级
页面：http://dev.test.com:8082/#/ip-address
请 review 当前分支相对基线的 diff。
```

`skills/` 下的其他内容是入口技能调用的内部 playbook，不需要、也不应单独安装为用户可调用技能。

## 审查原则

- 只审 diff 引入、改变或直接暴露的风险；其他文件或页面只能用于证明影响链。
- 没有“变更 → 影响”因果链的问题，列为建议，不阻塞本次 review。
- 风险结论必须尽量附带证据：命令结果、接口契约、浏览器操作、截图或网络记录。
- 不把代码风格建议与功能、数据、安全或交互缺陷混在一起。
- 不凭空推断业务规则；缺失的接口契约或产品语义应作为开放问题说明。

## 两阶段 SOP

1. **识别与报告**：读取需求和 diff，构建最小上下文，形成可证伪的风险假设，并运行非修改性的检查与页面验证。此阶段不修改业务代码。
2. **最小修复与回归**：仅在用户明确批准具体范围后修改代码，并执行与变更相称的回归验证。

审查输出按以下类别排序：已验证缺陷、未验证但与 diff 相关的风险、已验证通过项，以及不阻塞的优化建议。

## 页面验证策略

页面验证按以下优先级选择工具，以复用用户现有登录态：

1. Chrome DevTools：连接已登录的 Chrome，优先用于已有页面、SSO 会话和真实交互。
2. CDP Bridge：在需要复用统一门户会话时作为连接路径。
3. Playwright：前两者不可用时才启用独立浏览器；遇到统一门户登录时由用户手动完成登录。

每次页面验证记录连接方式、环境、账号/角色、前置数据、操作步骤、预期与实际结果；不能连通或缺少测试数据时，明确标记为 blocked，不能据此宣称验证通过。

## 安装

将 `skills/collab-verified-review` 链接或复制到 `$CODEX_HOME/skills/collab-verified-review`，然后重新打开 Codex 会话。在 `/` 菜单中只应看到一个 **Verified Review** 入口。

## 仓库结构

```text
skills/
  collab-verified-review/       # 唯一用户入口
    SKILL.md
    references/                 # SOP、上下文、风险、静态验证、UI 证据和报告模板
docs/                           # 工具兼容性与运行记录
```

当前版本只适配 `auto-ops`，并非多项目通用 review 框架。
