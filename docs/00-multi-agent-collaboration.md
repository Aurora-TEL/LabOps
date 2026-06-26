# LabOps 多 Agent 协作开发方案

## 1. 协作目标

LabOps 采用“主控线程 + 模块线程”的方式推进。主控线程负责规划、验收、合并和冲突处理；模块线程分别负责产品文档、数据库、后端、前端和部署。这样既能并行开发，又能避免多个聊天框同时改同一批文件导致混乱。

## 2. 主控线程职责

当前聊天框作为主控线程，负责：

- 维护项目总目标和阶段计划。
- 拆分任务并分派给不同聊天框。
- 维护文件修改边界。
- 审查模块线程产出的文档和代码。
- 最终整合前端、后端、数据库和 Docker。
- 运行验证命令并整理复试演示材料。

主控线程优先修改：

- `README.md`
- `docs/00-multi-agent-collaboration.md`
- `docs/08-agent-task-board.md`
- 跨模块整合文件

## 3. Agent 分工总表

| Agent | 核心职责 | 主要产出 | 修改范围 |
| --- | --- | --- | --- |
| A0 主控整合 Agent | 任务拆分、里程碑、验收、合并冲突 | 协作方案、任务看板、README、最终整合 | `README.md`, `docs/00-*`, `docs/08-*` |
| A1 产品需求 Agent | 需求、模块、权限、流程、复试讲解 | 产品文档、流程文档、讲解稿 | `docs/01-*`, `docs/02-*`, `docs/03-*`, `docs/04-*`, `docs/07-*` |
| A2 数据库架构 Agent | PostgreSQL 表结构、ER 关系、种子数据 | 数据库设计、模型草案、初始化数据 | `docs/05-*`, `backend/app/models/`, `backend/app/db/`, `backend/alembic/` |
| A3 API 后端 Agent | FastAPI 项目结构、接口、认证、业务逻辑 | 路由、Schema、Service、测试 | `backend/` |
| A4 前端看板 Agent | Vue3 中后台界面、ECharts 图表、页面路由 | Dashboard、设备、预约、报修、分析页面 | `frontend/` |
| A5 Docker 部署 Agent | 容器化、本地启动、环境变量 | Dockerfile、Compose、启动说明 | `docker-compose.yml`, `.env.example`, `backend/Dockerfile`, `frontend/Dockerfile`, `docs/09-deployment.md` |

## 4. 文件边界规则

1. 每个聊天框只修改自己负责的目录或文件。
2. 如果必须跨目录修改，先在主控线程登记原因。
3. 不同 Agent 不要同时改同一个文件。
4. 数据库字段、接口路径、前端字段名必须以文档为准。
5. 主控线程负责最终统一命名、格式和运行验证。

## 5. 运行环境规则

LabOps 的开发和演示运行环境统一放在 Docker 容器中。宿主机只作为代码编辑和 Git 工作区，不安装项目运行依赖。

硬性约束：

- 宿主机只要求安装 Git、Docker 和 Docker Compose。
- 不在宿主机执行 `pip install`、`poetry install`、`uv sync`、`npm install`、`pnpm install`、`yarn install` 等项目依赖安装命令。
- 不在宿主机生成 `node_modules/`、Python 虚拟环境、数据库数据目录等运行产物。
- 后端依赖安装、FastAPI 启动、pytest 测试应在后端容器内执行。
- 前端依赖安装、Vite 启动、构建检查应在前端容器内执行。
- PostgreSQL 只通过 `docker-compose.yml` 中的数据库服务启动。

如果某个 Agent 需要验证运行结果，应优先使用 `docker compose` 或容器内命令。若当前环境无法运行 Docker，则在总结中明确说明“未做真实容器运行验证”，不要改为宿主机安装依赖。

## 6. 推荐开发顺序

| 阶段 | 目标 | 负责人 | 验收标准 |
| --- | --- | --- | --- |
| M1 文档冻结 | 需求、模块、权限、流程完整 | A1 | `docs/01` 到 `docs/04` 可用于复试讲解 |
| M2 架构冻结 | 数据库和 API 文档完整 | A2, A3 | ER 关系清晰，接口覆盖核心流程 |
| M3 后端可运行 | FastAPI 服务、数据库连接、核心接口 | A3 | 后端能启动，健康检查通过 |
| M4 前端可演示 | Vue3 看板和核心页面完成 | A4 | 首页、设备、预约、报修、分析页面可访问 |
| M5 容器化联调 | 一键启动完整系统 | A5, A0 | `docker compose up` 可启动数据库、后端、前端 |
| M6 复试材料 | 演示脚本和答辩问题整理 | A0, A1 | 有完整演示路径和讲解稿 |

## 6.1 v1.1 合并顺序与风险控制

v1.1 推荐按“数据库 -> 后端 -> 前端 -> Docker/QA”的顺序合并。原因是数据库迁移决定核心表和字段，后端依赖这些结构形成 API 契约，前端再依赖 API 契约完成真实数据联调。

合并时重点检查四类风险：

- 数据库迁移：确认 Alembic 迁移、SQLAlchemy 模型和种子数据一致。
- API 契约：确认路径、字段名、状态枚举和错误响应与文档一致。
- 前端 fallback：确认 fallback 只用于演示兜底，不隐藏真实接口失败。
- 容器健康检查：确认 `docker compose ps`、首页、Swagger 和核心 API 都能访问。

详细清单见 `docs/11-v1.1-acceptance-demo.md`。

## 7. 分派方式

为每个模块新开一个聊天框时，先复制 `docs/08-agent-task-board.md` 中对应 Agent 的“启动提示”。模块线程完成后，把改动交回主控线程，由主控线程检查 Git 状态、运行验证并决定是否提交。

## 8. 当前文件锁

| 文件或目录 | 当前负责人 | 状态 |
| --- | --- | --- |
| `docs/01-requirements.md` | A1 产品需求 Agent | 已有初稿 |
| `docs/02-modules.md` | A1 产品需求 Agent | 已有初稿 |
| `docs/03-roles-permissions.md` | A1 产品需求 Agent | 已有初稿 |
| `docs/04-business-flow.md` | A1 产品需求 Agent | 已有初稿 |
| `docs/05-database-design.md` | A2 数据库架构 Agent | 待细化 |
| `docs/06-api-spec.md` | A3 API 后端 Agent | 待细化 |
| `backend/` | A3 API 后端 Agent | 已建骨架 |
| `frontend/` | A4 前端看板 Agent | 已建骨架 |
| Docker 相关文件 | A5 Docker 部署 Agent | 待实现 |
