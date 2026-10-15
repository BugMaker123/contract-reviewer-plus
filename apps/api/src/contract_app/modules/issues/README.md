# issues 模块

## 1. 职责与边界
- 职责：管理条款级结构化问题组（IssueGroup）、风险多点归并、用户处理备注与针对意见追问。
- 不负责：底层 OOXML 修订标签生成、DOCX 保存回调。

## 2. 公开入口与关键类型
- `IssueGroup`: 条款问题组实体（风险点、法务意见、证据与处理状态）。
- `ListIssuesUseCase`: 查询审查任务关联的问题组。
- `AddCommentUseCase`: 为问题组添加人工复核备注。
- `IssueFollowupUseCase`: 针对该次审查的特定意见进行法务追问。

## 3. 依赖方向
- 允许依赖：`shared`。
- 不允许依赖：UI 逻辑、特定文档服务厂商代码。

## 4. 关键不变量
- 同一条款的多个风险点必须归并在一个问题组中，不产生重复孤立卡片。
- 问题组状态变化必须与修订命令执行确认保持最终一致。

## 5. 验证与阅读
- 测试：`tests/unit/test_issues.py`。
- 修改阅读清单：`domain/issue_group.py` -> `application/list_issues.py`。
