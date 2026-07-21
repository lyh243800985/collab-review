# Figma 证据

只读取与本次增量需求和 diff 相关的节点、页面变体与交互状态。Figma 中的完整旧页面不是默认审查范围。

## 使用规则

- 使用插件声明的 Figma MCP 获取结构化节点、尺寸、样式、文案和必要截图；不要用浏览器网页截图替代结构化 Figma 事实。
- 把需求范围内节点、关联回归区域、范围外区域和范围不明区域分开。
- UI 差异使用 Figma 数值或规范作为 expected，使用 DOM、computed style 或页面截图作为 actual。
- 自适应区域验证约束关系，不机械比较绝对宽度。
- 只有同时具备设计依据与页面事实时，才把像素或规范差异升级为已验证缺陷。
- 缺少设计状态时标记开放问题；不要用模型偏好补齐设计。

```yaml
figma_reference:
  file: <url or key>
  nodes: []
  states: []
in_scope: []
related_regression_scope: []
out_of_scope: []
unknown_scope: []
```
