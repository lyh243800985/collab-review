# Chrome 插件在 Codex Node REPL 中的 `process` shim 兼容修复

## 背景

在 `collab-verified-review` 执行真实页面验证时，需要连接用户当前已登录的 Chrome，读取现有标签页并验证：

- `http://dev.test.com:8082/#/ip-address`
- 页面 DOM
- 页面截图
- 连续刷新后的连接稳定性
- 控制运行时重建后的恢复能力

本次处理日期：2026-07-15。

## 问题现象

按照 Chrome skill 提供的标准方式加载客户端：

```js
const { setupBrowserRuntime } = await import("<chrome-plugin>/scripts/browser-client.mjs");
await setupBrowserRuntime({ globals: globalThis });
const chrome = await agent.browsers.get("extension");
```

插件在模块初始化阶段报错：

```text
TypeError: Cannot redefine property: process
```

错误发生在发现 Chrome、检查扩展连接状态之前，因此它不是以下问题：

- Chrome 未启动；
- Chrome 扩展未连接；
- 用户登录态缺失；
- 目标标签页不存在。

## 根因

插件客户端初始化时会创建一个较完整的 `processShim`，随后直接覆盖全局对象：

```js
globalThis.process = processShim;
globalThis.global = globalThis.global ?? globalThis;
globalThis.global.process = processShim;
```

Codex Node REPL 提供的是受保护、字段精简的 `process`。插件不能覆盖这个只读绑定，所以加载过程直接终止。

只跳过全局赋值仍然不够。插件打包代码还依赖：

```js
process.versions.node
global.process.on(...)
```

REPL 自带的精简对象不具备完整的 `versions`、`on`、`off` 等字段，因此还会继续出现：

```text
Cannot read properties of undefined (reading 'node')
global.process.on is not a function
```

## 修改方案

修改范围仅限插件客户端的 process shim 初始化，不修改浏览器控制协议和业务项目代码。

### 1. 为打包模块提供局部 `process`

```js
const process = processShim;
```

打包代码中的自由变量 `process` 会使用模块局部 shim，不再依赖 REPL 的精简全局对象。

### 2. 为打包模块提供局部 `global`

```js
const global = Object.create(globalThis);
Object.defineProperty(global, "process", { value: processShim });
```

使用 `Object.defineProperty` 创建自有属性，是因为直接执行 `global.process = processShim` 仍可能受到原型链上只读属性的限制。

### 3. 将全局覆盖改为容错写入

```js
try {
  globalThis.process = processShim;
} catch {
  // The Codex Node REPL exposes a protected process binding.
}

globalThis.global = globalThis.global ?? globalThis;

try {
  globalThis.global.process = processShim;
} catch {
  // Keep the REPL-provided process binding when it cannot be replaced.
}
```

这样既保留 REPL 的安全限制，也能让插件内部获得完整 shim。

## 修改文件

当前安装版本为 `26.707.71524`，修改了两份内容相同的客户端文件：

```text
C:\Users\24380\.codex\plugins\cache\openai-bundled\chrome\26.707.71524\scripts\browser-client.mjs
C:\Users\24380\.codex\plugins\cache\openai-bundled\browser\26.707.71524\scripts\browser-client.mjs
```

修改前两份文件的 SHA-256 均为：

```text
57EE77A283EB230C6C6D47353AF13A25CEC4C331B511868C8FBF7CCD3DD1B2F6
```

修改后两份文件的 SHA-256 均为：

```text
02ABB35CCECF19CAC8CEB4B8A493E6083EDBF3342648A6C30A8A495D3776C19C
```

## 备份与恢复

修改前已创建备份：

```text
C:\Users\24380\.codex\plugins\cache\openai-bundled\chrome\26.707.71524\scripts\browser-client.mjs.20260715-before-process-shim-fix.bak
C:\Users\24380\.codex\plugins\cache\openai-bundled\browser\26.707.71524\scripts\browser-client.mjs.20260715-before-process-shim-fix.bak
```

备份哈希与原文件哈希一致。如需恢复，应先退出正在使用浏览器插件的 Codex 任务，再用对应 `.bak` 文件替换当前文件。

## 验证结果

| 验证项 | 结果 | 证据 |
| --- | --- | --- |
| 插件模块加载 | 通过 | `setupBrowserRuntime()` 成功完成 |
| 发现 Chrome | 通过 | `agent.browsers.get("extension")` 返回 Chrome binding |
| 读取现有标签页 | 通过 | 读取到 3 个用户标签页及标题、URL |
| 认领现有测试标签页 | 通过 | 成功认领 `dev.test.com` 标签页 |
| 打开目标页面 | 通过 | URL 为 `http://dev.test.com:8082/#/ip-address` |
| DOM 读取 | 通过 | 读取到“IP地址”“子网网段”和网段表格数据 |
| 截图 | 通过 | 成功获得页面截图 |
| 连续刷新 | 通过 | 连续刷新 3 次，DOM 与截图均成功 |
| 强制重置后发现 Chrome | 通过 | 新连接仍能列出 Chrome 和原标签页 |
| 强制重置后重新认领原标签页 | 未通过 | 连续两次在 `claimTab()` 超时 |

## 当前结论

该兼容补丁解决了阻断 Chrome 验证的初始化错误，已经可以用于常规 code review 页面验证，包括：

- 使用用户当前 Chrome 登录态；
- 读取和认领现有标签页；
- DOM 行为验证；
- 截图取证；
- 页面刷新回归。

但异常中断恢复还不完整：如果控制运行时在未调用 `browser.tabs.finalize(...)` 的情况下被强制重置，旧会话可能继续持有标签页控制锁。新连接可以发现标签页，但重新认领可能超时。

正常结束 Chrome 验证时必须执行：

```js
await chrome.tabs.finalize({ keep: [] });
```

如果需要保留目标页面交给用户继续操作，应按 Chrome skill 的约定将其标记为 `handoff` 或 `deliverable`。

## 已知风险

1. 这是已安装插件缓存中的本地兼容补丁，不是官方版本修复。
2. Codex、Browser 或 Chrome 插件升级、重装、缓存刷新后可能覆盖补丁。
3. 新插件版本的打包结构可能变化，不能直接根据旧行号机械套用。
4. 应先复现 `process` 冲突并检查新文件的 shim 代码，再决定是否继续使用此方案。
5. 强制中断后的标签页锁恢复仍需官方插件或连接层提供可靠的会话清理机制。

## 后续建议

- 每次插件升级后，先使用标准连接方式验证是否已经由官方修复。
- 如果错误再次出现，先比对插件版本和 `browser-client.mjs` 内容，再应用最小兼容修改。
- review 自动化应把 `tabs.finalize(...)` 放入浏览器验证的强制收尾步骤。
- 将“连接建立”和“异常重连恢复”作为两个独立验证项，不能因为首次连接成功就宣称连接完全稳定。
