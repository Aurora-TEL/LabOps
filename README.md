# LabOps

LabOps 是一个用于考研复试展示的智能实验室设备预约与运维管理平台。

项目定位为数据看板型中后台系统，UI 参考智能制造运营平台和 ERP 管理后台，采用浅色科技风，包含左侧导航、顶部栏、指标卡片、ECharts 图表，以及预约、设备、报修、工单、数据分析和角色权限等模块。

## 技术栈

- Frontend: Vue 3, Vite, TypeScript, ECharts
- Backend: FastAPI, SQLAlchemy, Pydantic
- Database: PostgreSQL
- Deployment: Docker, Docker Compose

## 运行环境约束

项目运行环境统一放在 Docker 容器中。宿主机只需要 Git、Docker 和 Docker Compose，不安装项目级 Python、Node 或 PostgreSQL 依赖。

- 后端依赖安装、FastAPI 启动和测试在后端容器内完成。
- 前端依赖安装、Vite 启动和构建在前端容器内完成。
- PostgreSQL 通过 Docker Compose 服务启动。
- 不在宿主机执行 `pip install`、`npm install`、`npm run build` 等项目依赖或构建命令。

## 启动方式

```bash
cp .env.example .env
docker compose up --build
```

默认访问地址：

- 前端: `http://localhost:5173`
- 后端 API: `http://localhost:8000/api/v1`
- 后端 Swagger: `http://localhost:8000/docs`
- PostgreSQL: `localhost:5432`

初始化数据库和演示数据：

```bash
docker compose exec backend alembic upgrade head
docker compose exec backend python -m app.db.seed
```

## 演示账号

| 身份 | 用户名 | 密码 | 登录后页面 | 演示重点 |
| --- | --- | --- | --- | --- |
| 普通用户 | `ordinary01` | `labops123` | `/ordinary` | 设备查询、预约申请、取消本人预约、提交报修、查看本人记录 |
| 设备负责人 | `owner01` | `labops123` | `/owner` | 负责设备状态维护、预约审批、报修派工、工单推进 |
| 实验室管理员 | `labadmin01` | `labops123` | `/dashboard` | 完整运营后台、设备预约报修工单管理 |
| 系统管理员 | `admin` | `password` | `/dashboard` | 全局管理、系统设置、用户角色能力展示 |

## v1.3 演示与验收

v1.3 的重点是“不同身份进入不同前端”：

1. 使用 `ordinary01` 登录，系统直接进入普通用户自助台。
2. 使用 `owner01` 登录，系统直接进入设备负责人工作台。
3. 使用 `admin` 或 `labadmin01` 登录，系统进入完整运营后台。
4. 通过 Swagger 或测试用例说明：前端隐藏按钮只是体验层，后端接口仍会校验 token、权限和数据范围。

详细说明见：

- [v1.3 角色工作台与权限范围](docs/14-v1.3-role-workbenches.md)
- [v1.3 验收与演示手册](docs/15-v1.3-acceptance-demo.md)

## 容器内验证命令

```bash
docker compose build --progress=plain
docker compose up -d --force-recreate
docker compose ps
docker compose exec backend alembic upgrade head
docker compose exec backend python -m app.db.seed
docker compose run --rm -e PYTHONDONTWRITEBYTECODE=1 backend pytest -p no:cacheprovider
docker build --target build -t labops-frontend-build-check ./frontend
```

验证结束后，宿主机不应残留：

- `frontend/node_modules`
- `frontend/dist`
- `backend/.venv`
- `backend/.pytest_cache`
- `__pycache__`

## 开发流程

1. 梳理需求文档、功能模块、角色权限、业务流程。
2. 设计 PostgreSQL 数据库表结构和 ER 关系。
3. 规划 REST API 接口文档。
4. 落地 FastAPI 后端、Vue3 前端和 Docker 容器化配置。
5. 通过多 agent 协作拆分后端、前端、文档、验证任务，由主线程统一集成和验收。

## 目录结构

```text
LabOps/
  docs/                  项目文档与协作分工
  backend/               FastAPI 后端
  frontend/              Vue3 前端
  docker-compose.yml     本地开发容器编排
```

## 文档索引

- [多 Agent 协作开发方案](docs/00-multi-agent-collaboration.md)
- [需求文档](docs/01-requirements.md)
- [功能模块设计](docs/02-modules.md)
- [角色权限设计](docs/03-roles-permissions.md)
- [业务流程设计](docs/04-business-flow.md)
- [数据库设计](docs/05-database-design.md)
- [API 接口规划](docs/06-api-spec.md)
- [复试展示讲解提纲](docs/07-defense-script.md)
- [多 Agent 任务拆分表](docs/08-agent-task-board.md)
- [Docker 部署说明](docs/09-deployment.md)
- [v1.1 开发路线](docs/10-v1.1-roadmap.md)
- [v1.1 验收与演示手册](docs/11-v1.1-acceptance-demo.md)
- [v1.2 开发路线](docs/12-v1.2-roadmap.md)
- [v1.2 验收与演示手册](docs/13-v1.2-acceptance-demo.md)
- [v1.3 角色工作台与权限范围](docs/14-v1.3-role-workbenches.md)
- [v1.3 验收与演示手册](docs/15-v1.3-acceptance-demo.md)
- [v1.4 消息通知与操作审计](docs/16-v1.4-notification-audit.md)
- [v1.4 验收与演示手册](docs/17-v1.4-acceptance-demo.md)
- [v1.5 系统管理与 RBAC 治理中心](docs/18-v1.5-system-management.md)
- [v1.5 验收与演示手册](docs/19-v1.5-acceptance-demo.md)
- [v1.6 设备详情与维护台账](docs/20-v1.6-device-maintenance-ledger.md)
- [v1.6 验收与演示手册](docs/21-v1.6-acceptance-demo.md)
- [v1.7 预约日历与设备占用视图](docs/22-v1.7-reservation-calendar.md)
- [v1.7 验收与演示手册](docs/23-v1.7-acceptance-demo.md)
- [启动、测试与结束说明](docs/24-start-test-stop-guide.md)
- [v1.8 运营分析报表](docs/25-v1.8-operation-analytics-report.md)
- [v1.8 验收与演示手册](docs/26-v1.8-acceptance-demo.md)
