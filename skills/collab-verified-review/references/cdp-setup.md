# CDP Bridge 设置与诊断

插件内置 CDP Bridge MCP 配置和配套 Chrome 扩展。扩展受 Chrome 安全策略限制，需要每台机器首次手动加载一次。

## 诊断

在用户当前工作区运行：

```powershell
python <plugin-root>/scripts/doctor.py --require-connected
```

结果区分：服务未启动、扩展未连接、扩展包无效、CTeam 配置缺失和 Figma 环境授权缺失。配置存在只代表字段完整，不代表远端认证有效。

## 首次安装扩展

1. 打开 `chrome://extensions/`。
2. 开启开发者模式。
3. 点击“加载已解压的扩展程序”。
4. 选择 `<plugin-root>/assets/cdp-bridge-extension/`。
5. 调用一次 CDP Bridge 的标签页查询，等待扩展连接，再重跑 doctor。

## Review 使用规则

- 所有页面操作显式指定 `tab_id`，禁止依赖活动页。
- 多页面可并行；同一页面的有状态交互保持串行。
- 创建临时标签页时使用命名分组；完成后将分组标为已完成或精确关闭测试页。
- ACK 超时表示结果未知。先检查页面、网络或下载副作用，禁止立即重复点击。
- 工具失败与业务缺陷分栏记录，不能把连接错误归因给产品页面。
