# 在线合同智能审查与修订系统 (Contract Reviewer Plus)

面向企业内部法务与商务团队的高保真在线智能合同审查、原生修订复核与一致性发布系统。

## 1. 核心架构与设计原则

严格遵照 `业务设计/` 与 `技术设计/` 规范实施：
- **版本不可变性**：原始文件与已持久化版本只读；AI 建议和人工改写均生成新快照并执行 CAS 校验。
- **任务与事件分离**：审查长任务通过 `POST /api/review-runs` 异步发起，前端基于 SSE (`GET /api/review-runs/{id}/events`) 订阅，断线不丢失进度且支持游标恢复。
- **Word 原生修订与批注**：以 DOCX 原生修订痕迹为核心，支持生成待复核修订版本，用户在在线工作台中单项/批量采纳或拒绝，并可导出清洁稿与带修订稿。
- **工程可维护性门禁**：通过 `tools/quality/check_file_limits.py` 自动化检查文件物理行数与字节限制。

## 2. 目录结构

```text
apps/
  web/                      # Vue 3 + Vite + TypeScript + Pinia 前端应用
    src/
      app/                  # 路由与入口挂载
      pages/                # 工作台 (WorkbenchPage <=150行) 与合同列表
      features/             # 领域功能：contracts, editor, review, issues, revisions, versions, exports, settings
      shared/               # UI组件库、HTTP客户端、SSE传输与设计变量
  api/                      # Python FastAPI 后端服务
    src/contract_app/
      bootstrap/            # 配置与应用装配工厂
      http/                 # REST 路由（合同、编辑会话、审查任务、复核决定、导出）
      worker/               # 独立后台执行 Worker（租约管理与流水线编排）
      modules/              # 业务模块：contracts, documents, reviews, issues, revisions, exports
      infrastructure/       # 存储、事件总线、ONLYOFFICE适配、模型网关与仓储
tools/
  quality/                  # check_file_limits.py 自动门禁工具
deploy/                     # Docker Compose 与容器编排模板
tests/                      # 单元测试与端到端用例
```

## 3. 运行指南

### 方式一：Docker Compose 全量容器化运行（标准模式）

在项目根目录下执行：
```bash
cd deploy
docker compose up -d --build
```
启动的服务包括：
- **Web 前端**：http://localhost:3000
- **API 服务**：http://localhost:8000 (API 文档: http://localhost:8000/docs)
- **Document Server (ONLYOFFICE)**：http://localhost:8080
- **PostgreSQL 16**：localhost:5432
- **Redis 7**：localhost:6379
- **Review Worker**：独立后台进程

### 方式二：本地极速开发调试

1. **后端启动**：
```bash
# 激活虚拟环境
.\.venv\Scripts\activate
# 启动 API 服务
python apps/api/main.py
```
2. **前端启动**：
```bash
cd apps/web
npm run dev
```
访问 http://localhost:3000 即可进入系统工作台。

## 4. 质量门禁与测试

```bash
# 运行文件大小与代码行数质量门禁
python tools/quality/check_file_limits.py

# 运行后端单元测试
.\.venv\Scripts\pytest tests/unit

# 运行前端严格类型检查与生产打包
cd apps/web && npm run build
```
