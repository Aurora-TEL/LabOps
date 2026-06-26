# LabOps

LabOps 智能实验室设备预约与运维管理平台，用于考研复试展示。

项目定位为数据看板型中后台系统，参考智能制造运营平台与 ERP 管理后台风格，采用浅色科技风 UI，包含预约、设备、报修、工单、数据分析和角色权限等模块。

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

## 开发流程

1. 梳理需求文档、功能模块、角色权限、业务流程。
2. 设计 PostgreSQL 数据库表结构和 ER 关系。
3. 规划 REST API 接口文档。
4. 落地 FastAPI 后端、Vue3 前端和 Docker 容器化配置。

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
