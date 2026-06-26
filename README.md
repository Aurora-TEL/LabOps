# LabOps

LabOps 智能实验室设备预约与运维管理平台。

本项目用于考研复试展示，定位为数据看板型中后台系统，参考智能制造运营平台与 ERP 管理后台风格，采用浅色科技风 UI，包含设备预约、设备台账、故障报修、运维工单、数据分析、角色权限等模块。

## 技术栈

- Frontend: Vue 3, Vite, TypeScript, ECharts
- Backend: FastAPI, SQLAlchemy, Pydantic
- Database: PostgreSQL
- Deployment: Docker, Docker Compose

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
  docker-compose.yml     本地开发编排
```

## 当前阶段

当前仓库处于项目初始化阶段，优先完成文档与架构设计，再进入代码实现。

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
