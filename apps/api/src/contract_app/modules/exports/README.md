# exports 模块

## 1. 职责与边界
- 职责：基于已持久化的文档版本生成交付副本（带修订稿、清洁稿及格式化审查意见书）。
- 不负责：修改合同工作 head 指针或篡改当前版本修订状态。

## 2. 公开入口与关键类型
- `ExportJob`: 导出任务实体。
- `CreateExportUseCase`: 发起导出任务。
- `GenerateCleanDraftUseCase`: 生成已采纳修订的清洁版 DOCX。
- `GenerateTrackChangesUseCase`: 生成包含原生 OOXML 批注和修订标记的 DOCX。
- `GenerateReportUseCase`: 导出 Markdown / DOCX 审查意见报告书。

## 3. 依赖方向
- 允许依赖：`documents` 模块、`issues` 模块、`infrastructure/storage`、`shared`。
- 不允许依赖：前端组件。

## 4. 关键不变量
- 导出产物必须绑定明确的不可变源版本 ID。
- 清洁稿只在导出副本上生效，不直接消除工作当前版本的修订历史。

## 5. 验证与阅读
- 测试：`tests/unit/test_exports.py`。
- 修改阅读清单：`domain/export_job.py` -> `application/create_export.py`。
