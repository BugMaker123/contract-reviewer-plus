# reviews 模块

## 1. 职责与边界
- 职责：管理审查任务生命周期（ReviewRun）、租约心跳、执行流水线编排、模型输出校验与结果发布。
- 不负责：直接存储 DOCX 二进制数据、管理前端界面状态。

## 2. 公开入口与关键类型
- `ReviewRun`: 审查任务实体（状态、分阶段进度、租约所有者、错误码）。
- `ReviewStatus`, `PipelineStage`: 任务和阶段枚举。
- `StartReviewUseCase`: 创建快照并投递审查任务。
- `CancelReviewUseCase`: 幂等取消正在执行的审查。
- `RunPipelineUseCase`: 执行多阶段流水线。

## 3. 依赖方向
- 允许依赖：`documents` 模块、`issues` 模块、`revisions` 模块、`ports/model_gateway`、`shared`。
- 不允许依赖：特定数据库 ORM 实现、HTTP 路由控制器。

## 4. 关键不变量
- 审查输入必须绑定已持久化的不可变快照版本。
- 取消命令必须生效并在执行阶段立刻中断发布；超时不重置。

## 5. 验证与阅读
- 测试：`tests/unit/test_reviews.py`。
- 修改阅读清单：`domain/review_run.py` -> `application/run_pipeline.py`。
