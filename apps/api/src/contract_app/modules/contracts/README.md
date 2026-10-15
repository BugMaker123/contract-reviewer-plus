# contracts 模块

## 1. 职责与边界
- 职责：管理合同元信息、工作 head 指针、审查状态与立场偏好。
- 不负责：文档正文存储、DOCX 解析、模型审查流水线执行或修订批注生成。

## 2. 公开入口与关键类型
- `Contract`: 合同领域实体（包含 `head_version_id`, `latest_review_run_id`, `revision`）。
- `CreateContractUseCase`: 创建新合同并初始化原始版本。
- `GetContractUseCase`, `ListContractsUseCase`: 查询合同详情及工作台列表。

## 3. 依赖方向
- 允许依赖：`documents` 模块（创建初始版本）、`shared` 基础库。
- 不允许依赖：FastAPI 框架直接对象、模型适配层、特定编辑器 SDK。

## 4. 关键不变量
- 合同 `head_version_id` 永远指向一个已持久化且不可变的 `DocumentVersion`。
- 每次版本前进必须递增 `revision`，防止并发覆盖。

## 5. 验证与阅读
- 测试：`tests/unit/test_contracts.py`。
- 修改阅读清单：`domain/contract.py` -> `application/create_contract.py`。
