# documents 模块

## 1. 职责与边界
- 职责：维护不可变文档版本历史（DocumentVersion）、编辑会话生命周期（EditorSession）与文件对象存储。
- 不负责：模型推理、风险分类、审查工作流逻辑。

## 2. 公开入口与关键类型
- `DocumentVersion`: 不可变版本模型（记录 content_hash、parent_id 与 kind）。
- `EditorSession`: 受控在线编辑会话。
- `CreateVersionUseCase`: 发布新版本（含内容去重和哈希计算）。
- `HandleSaveCallbackUseCase`: 处理文档服务保存回调，创建保存检查点。

## 3. 依赖方向
- 允许依赖：`infrastructure/storage`（对象读写）、`shared`。
- 不允许依赖：上层 reviews 逻辑、外部前端 SDK。

## 4. 关键不变量
- 历史版本文件永远只读且不可变；新内容永远生成新版本记录。
- 只有通过检查点校验的回调才能推进当前工作 head。

## 5. 验证与阅读
- 测试：`tests/unit/test_documents.py`。
- 修改阅读清单：`domain/version.py` -> `application/docx_service.py`。
