# revisions 模块

## 1. 职责与边界
- 职责：管理 AI 审查生成的修订计划（RevisionPlan）、离散修订操作（RevisionOperation）与人工复核采纳/拒绝命令（DecisionCommand）。
- 不负责：直接解析 HTTP 头部、展示前端交互弹窗。

## 2. 公开入口与关键类型
- `RevisionPlan`, `RevisionOperation`: 审查结果的修订操作指令。
- `DecisionCommand`: 采纳/拒绝复核命令（支持幂等键与版本 CAS 校验）。
- `ApplyDecisionUseCase`: 执行采纳或拒绝命令，并联动更新问题组与文档版本。

## 3. 依赖方向
- 允许依赖：`documents` 模块、`issues` 模块、`shared`。
- 不允许依赖：特定前端状态管理器。

## 4. 关键不变量
- 执行复核命令前必须校验 `expected_version_id`，版本不一致返回 409 冲突。
- 只有保存检查点确认后，命令状态才由 `awaiting_save` 转为 `confirmed`。

## 5. 验证与阅读
- 测试：`tests/unit/test_revisions.py`。
- 修改阅读清单：`domain/operation.py` -> `application/apply_decision.py`。
