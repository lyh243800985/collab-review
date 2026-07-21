---
name: collab-verified-review
description: 基于需求、CTeam 单据、Figma、代码 diff、项目契约和真实浏览器行为执行证据驱动的前端代码审查。用户要求 review PR、分支、补丁或当前修改，并希望验证功能、UI、UX、接口、状态或关联页面回归时使用；只把由 diff 引入、改变或直接暴露的问题列为风险。这是插件的总控入口，并按阶段调用内部专家 Skill。
---

# 验证式前端 Diff Review

把审查当作“需求事实 → diff 风险假设 → 静态或页面验证 → 分级结论”的闭环，不做全仓扫描。

## 开始前

1. 读取 [review-sop.md](references/review-sop.md)。
2. 输入含 CTeam/CW 单据链接时，读取 [requirements-evidence.md](references/requirements-evidence.md)，运行本 Skill 的读单脚本，并实际查看影响判断的正文图片。
3. 输入含 Figma 时，读取 [figma-evidence.md](references/figma-evidence.md)，使用插件声明的 Figma MCP 获取相关节点和状态。
4. 建立最小代码上下文时读取 [context-map.md](references/context-map.md)。
5. 页面或交互风险出现时读取 [ui-evidence.md](references/ui-evidence.md)；首次使用、CDP 不可用或标签页为空时读取 [cdp-setup.md](references/cdp-setup.md)，并运行插件根目录的 `scripts/doctor.py`。
6. 生成结论前读取 [risk-hypothesis.md](references/risk-hypothesis.md)、[static-verification.md](references/static-verification.md) 和 [report-template.md](references/report-template.md)。

## 内部专家编排

- `collab-review-context`：建立最小代码与契约上下文。
- `collab-review-hypothesis`：把疑点转成可证伪假设。
- `collab-static-verify`：执行非修改性的定向检查。
- `collab-ui-verify`：通过 Figma 与真实页面验证行为。
- `collab-review-report`：按证据等级汇总结论。

总控负责范围和最终结论；子 Skill 只承担对应阶段，不得自行扩大审查范围。

## Phase 1：识别与验证

1. 明确 diff/base、变更文件、需求目标、页面路由和本次排除项。
2. 从需求字段、正文、图片、Figma 和仓库契约建立事实集；来源不可互相冒充。
3. 只读取解释 diff 所需的路由、组件、状态、权限、接口和代表性消费者。
4. 将疑点写成可证伪假设。没有“changed location → 触发条件 → 可观察影响”因果链的内容降为建议。
5. 执行非修改性的定向静态检查。禁止运行 build，也禁止运行带 `--fix` 的检查。
6. 对功能、UI、UX、接口或关联页面风险，在真实页面复现最小触发链；优先复用已登录 Chrome，并保留 DOM、截图、控制台或网络证据。
7. 输出已验证缺陷、未验证的 diff 风险、已验证通过、开放问题与范围外建议。说明检查过和未检查的层。
8. 同步生成机器可读 JSON，并运行插件根目录 `scripts/validate_review.py <report.json>`。门禁未通过时只能修正分类或补证据，不能绕过校验发布结论。
9. 给出最小修复范围并等待用户明确批准。Phase 1 不修改业务代码、测试、配置或外部系统。

## Phase 2：最小修复与回归

仅处理用户明确批准的 finding：

1. 重述批准项、暂缓项与排除项。
2. 进行最小代码修改，不顺带修复建议项或历史问题。
3. 运行与风险相称的静态检查和真实页面回归。
4. 记录修改文件、实际证据、仍受阻内容和用户暂缓的设计项。

## 硬边界

- 需求外历史问题只作建议；若范围外页面被本次 diff 回归，仍属于本次风险。
- Figma 展示的整页旧内容不自动进入验收范围。
- 缺少接口字段、业务规则或设计说明时标记开放问题，不替产品或后端做决定。
- 浏览器连通、交互稳定和中断恢复是不同结论，不能以一次连接成功概括全部稳定性。
- 未真实执行的页面路径不能写成“通过”或“已复现”。
- 不执行会改变测试或生产数据的最终提交动作，除非用户明确授权并具备可恢复数据。
- 只对批准项改代码；Code Review 的批准不等于授权全量重构。
