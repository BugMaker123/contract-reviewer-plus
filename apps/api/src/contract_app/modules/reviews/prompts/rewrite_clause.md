# 条款修订改写提示词 (v1.0)

针对问题组中的条款及统一解决方案，输出明确的修订操作清单（RevisionOperations）。
每个操作项格式如下：
- kind: 必须是 "insert"、"delete"、"replace" 或 "comment" 之一
- anchor: 定位的精确原文段落或锚点
- expected_text: 拟删除或拟被替换的精确原文字符串
- replacement_text: 拟插入或替换后的新条款文本
- public_reason: 面向用户的公开修订理由

约束：
- 只允许针对风险条款进行最小必要改写。
- 绝不得删空整段正文。
