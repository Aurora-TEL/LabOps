# LabOps 多 Agent 任务拆分表

## 1. 总任务看板

| 编号 | Agent | 阶段 | 任务 | 输入依赖 | 输出文件 | 验收标准 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| T-001 | A0 主控整合 | M1 | 建立协作方案和目录骨架 | 项目需求 | `docs/00-*`, `docs/08-*`, 目录骨架 | 职责边界清晰，后续线程可直接接任务 | 已完成 |
| T-002 | A1 产品需求 | M1 | 完善需求文档 | 用户原始需求、参考图 | `docs/01-requirements.md` | 能讲清背景、痛点、目标和范围 | 已完成初稿 |
| T-003 | A1 产品需求 | M1 | 完善功能模块 | 需求文档 | `docs/02-modules.md` | 模块覆盖看板、预约、设备、报修、分析、系统管理 | 已完成初稿 |
| T-004 | A1 产品需求 | M1 | 完善角色权限 | 需求文档 | `docs/03-roles-permissions.md` | RBAC 角色、权限矩阵、鉴权思路完整 | 已完成初稿 |
| T-005 | A1 产品需求 | M1 | 完善业务流程 | 模块文档、权限文档 | `docs/04-business-flow.md` | 预约、审核、报修、工单流程完整 | 已完成初稿 |
| T-006 | A2 数据库架构 | M2 | 设计 PostgreSQL 表结构 | `docs/01-*` 到 `docs/04-*` | `docs/05-database-design.md` | 表字段、主外键、枚举、索引清晰 | 已分派 |
| T-007 | A2 数据库架构 | M2 | 设计 ER 关系和初始化数据 | 数据库设计 | `docs/05-database-design.md`, `backend/app/db/` | 能支撑演示数据和核心流程 | 已分派 |
| T-008 | A3 API 后端 | M2 | 细化 REST API 文档 | 需求、数据库设计 | `docs/06-api-spec.md` | 接口覆盖认证、看板、设备、预约、报修、工单 | 已分派 |
| T-009 | A3 API 后端 | M3 | 搭建 FastAPI 项目 | API 文档、目录骨架 | `backend/` | 后端可启动，`/health` 可访问 | 已分派 |
| T-010 | A3 API 后端 | M3 | 实现核心业务接口 | 数据库模型、API 文档 | `backend/app/api/`, `backend/app/services/` | 设备、预约、报修、工单接口可用 | 已分派 |
| T-011 | A4 前端看板 | M4 | 搭建 Vue3 项目 | 参考图、模块文档 | `frontend/` | 前端可启动，基础布局完成 | 已分派 |
| T-012 | A4 前端看板 | M4 | 实现 Dashboard 页面 | API 文档、参考图 | `frontend/src/views/dashboard/` | 指标卡片和 ECharts 图表完成 | 已分派 |
| T-013 | A4 前端看板 | M4 | 实现业务页面 | 模块文档、API 文档 | `frontend/src/views/` | 设备、预约、报修、分析页面可演示 | 已分派 |
| T-014 | A5 Docker 部署 | M5 | 编写 Docker 配置 | 后端、前端项目结构 | Docker 相关文件 | 支持本地一键启动 | 已分派 |
| T-015 | A0 主控整合 | M6 | 联调验收与复试演示 | 全部模块 | `README.md`, `docs/07-*` | 有完整演示路径和答辩材料 | 待开始 |

## 2. 项目目录骨架

```text
LabOps/
  docs/
    00-multi-agent-collaboration.md
    01-requirements.md
    02-modules.md
    03-roles-permissions.md
    04-business-flow.md
    05-database-design.md
    06-api-spec.md
    07-defense-script.md
    08-agent-task-board.md
  backend/
    app/
      api/
        v1/
          endpoints/
      core/
      db/
      models/
      schemas/
      services/
    alembic/
      versions/
    tests/
  frontend/
    public/
    src/
      api/
      assets/
      components/
        common/
      layouts/
      mock/
      router/
      stores/
      styles/
      types/
      views/
        analytics/
        dashboard/
        devices/
        repairs/
        reservations/
        system/
  docker-compose.yml
  README.md
```

## 3. 统一运行环境约束

所有 Agent 必须遵守：

- 项目运行环境全部放在 Docker 容器中。
- 宿主机不安装项目依赖，不执行宿主机级 `pip install`、`poetry install`、`uv sync`、`npm install`、`pnpm install`、`yarn install`。
- 后端启动、测试和依赖安装通过后端容器完成。
- 前端启动、构建和依赖安装通过前端容器完成。
- PostgreSQL 只使用 Docker Compose 服务。
- 如果 Docker 当前不可用，可以只做静态检查并说明未完成容器运行验证，不要切换到宿主机安装依赖。

## 4. 分派给不同聊天框的启动提示

### A1 产品需求 Agent

你是 LabOps 项目的产品需求 Agent。请只修改 `docs/01-requirements.md`、`docs/02-modules.md`、`docs/03-roles-permissions.md`、`docs/04-business-flow.md`、`docs/07-defense-script.md`。目标是把“智能实验室设备预约与运维管理平台”整理成适合考研复试展示的产品文档，包括项目背景、核心痛点、用户角色、功能模块、业务流程、角色权限、展示亮点和答辩讲解稿。不要修改后端、前端和 Docker 文件。

### A2 数据库架构 Agent

你是 LabOps 项目的数据库架构 Agent。请先阅读 `docs/01-requirements.md`、`docs/02-modules.md`、`docs/03-roles-permissions.md`、`docs/04-business-flow.md`，然后完善 `docs/05-database-design.md`。数据库使用 PostgreSQL，要求设计用户、角色、权限、实验室、设备分类、设备、预约、报修、工单、维护记录、运营指标等表，写清字段、类型、主键、外键、索引、枚举状态和 ER 关系。后续实现阶段只修改 `backend/app/models/`、`backend/app/db/`、`backend/alembic/`。

### A3 API 后端 Agent

你是 LabOps 项目的 FastAPI 后端 Agent。请基于 `docs/06-api-spec.md` 和 `docs/05-database-design.md` 实现后端。技术栈为 FastAPI、SQLAlchemy、Pydantic、PostgreSQL。请将代码限制在 `backend/` 目录，优先实现项目结构、配置、数据库连接、健康检查、认证占位、设备、预约、报修、工单和看板统计接口。不要修改 `frontend/`。不要在宿主机安装 Python 依赖；运行和测试必须通过 Docker 容器完成。

### A4 前端看板 Agent

你是 LabOps 项目的 Vue3 前端 Agent。请基于用户提供的智能制造运营平台/ERP 后台参考图，设计浅色科技风中后台界面。请将代码限制在 `frontend/` 目录，优先实现左侧导航、顶部栏、首页指标卡片、ECharts 图表、设备状态、预约列表、报修工单和数据分析页面。不要修改 `backend/`。不要在宿主机安装 Node 依赖；运行和构建必须通过 Docker 容器完成。

### A5 Docker 部署 Agent

你是 LabOps 项目的 Docker 部署 Agent。请为 FastAPI、Vue3、PostgreSQL 编写容器化配置。请主要修改 `docker-compose.yml`、`.env.example`、`backend/Dockerfile`、`frontend/Dockerfile` 和部署说明文档。目标是支持本地使用 `docker compose up` 启动数据库、后端和前端。部署文档必须明确宿主机不安装项目依赖，依赖安装、启动、测试和构建全部在容器中完成。

## 5. 主控验收清单

每个 Agent 完成任务后，主控线程按以下清单验收：

- 是否只修改了被分派的文件范围。
- 是否和已有需求、数据库、API 命名保持一致。
- 是否能解释该模块在复试演示中的作用。
- 是否有必要的运行或静态检查。
- 是否遵守“项目依赖和运行全部在容器中”的约束。
- 是否没有引入无关重构和无关文件。
