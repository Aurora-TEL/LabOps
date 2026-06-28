# LabOps 启动、测试与结束说明

本文档用于本地演示、复试答辩和日常验收。LabOps 的运行、测试、构建都应在 Docker 容器中完成，宿主机只负责 Git 和 Docker，不安装项目级 Python、Node.js 或 PostgreSQL 依赖。

## 1. 启动前准备

确认宿主机已安装：

- Git
- Docker Desktop
- Docker Compose

进入项目根目录：

```bash
cd LabOps
```

首次运行时复制环境变量文件：

```bash
cp .env.example .env
```

Windows PowerShell 可使用：

```powershell
Copy-Item .env.example .env
```

## 2. 启动服务

推荐后台启动：

```bash
docker compose up -d --build
```

查看服务状态：

```bash
docker compose ps
```

正常情况下应看到三个服务运行：

| 服务 | 容器名 | 说明 |
| --- | --- | --- |
| postgres | `labops-postgres` | PostgreSQL 数据库 |
| backend | `labops-backend` | FastAPI 后端 |
| frontend | `labops-frontend` | Vue3 前端 |

访问地址：

- 前端：`http://localhost:5173`
- 后端 Swagger：`http://localhost:8000/docs`
- 后端 API：`http://localhost:8000/api/v1`
- 健康检查：`http://localhost:8000/api/v1/health/live`

## 3. 初始化数据库

启动容器后执行数据库迁移：

```bash
docker compose exec backend alembic upgrade head
```

导入演示数据：

```bash
docker compose exec backend python -m app.db.seed
```

演示账号：

| 身份 | 用户名 | 密码 | 登录后页面 |
| --- | --- | --- | --- |
| 普通用户 | `ordinary01` | `labops123` | `/ordinary` |
| 设备负责人 | `owner01` | `labops123` | `/owner` |
| 实验室管理员 | `labadmin01` | `labops123` | `/dashboard` |
| 系统管理员 | `admin` | `password` | `/dashboard` |

## 4. 启动后检查

检查容器健康状态：

```bash
docker compose ps
```

查看后端日志：

```bash
docker compose logs -f backend
```

查看前端日志：

```bash
docker compose logs -f frontend
```

查看数据库日志：

```bash
docker compose logs -f postgres
```

浏览器检查：

1. 打开 `http://localhost:5173`。
2. 使用 `ordinary01 / labops123` 登录，确认进入普通用户自助台。
3. 使用 `owner01 / labops123` 登录，确认进入设备负责人工作台。
4. 使用 `admin / password` 登录，确认进入完整后台。
5. 打开 `http://localhost:8000/docs`，确认 Swagger 可访问。

## 5. 后端测试

后端测试必须在 backend 容器中执行：

```bash
docker compose run --rm -e PYTHONDONTWRITEBYTECODE=1 backend pytest -p no:cacheprovider
```

测试覆盖重点：

- 登录认证
- RBAC 权限校验
- 设备管理与负责人数据范围
- 预约创建、审批、取消、冲突检测
- 预约日历与可用性接口
- 报修与工单流转
- 通知与审计日志
- 系统管理接口
- 数据库模型约束

## 6. 前端构建测试

前端生产构建必须通过 Docker build 执行，避免在宿主机生成 `node_modules` 或 `dist`：

```bash
docker build --target build -t labops-frontend-build-check ./frontend
```

该命令会检查：

- TypeScript 类型
- Vue 单文件组件编译
- Vite 生产构建
- 前端依赖安装是否在镜像构建过程中完成

## 7. 完整验收命令

复试演示前建议完整执行一次：

```bash
docker compose build --progress=plain
docker compose up -d --force-recreate
docker compose ps
docker compose exec backend alembic upgrade head
docker compose exec backend python -m app.db.seed
docker compose run --rm -e PYTHONDONTWRITEBYTECODE=1 backend pytest -p no:cacheprovider
docker build --target build -t labops-frontend-build-check ./frontend
```

如果以上命令均通过，即可说明：

- 数据库迁移可执行
- 演示数据可重复初始化
- 后端业务测试通过
- 前端生产构建通过
- 项目运行环境不依赖宿主机 Python 或 Node 项目依赖

## 8. 结束服务

普通结束，不删除数据库数据：

```bash
docker compose down
```

适用于临时关机、暂停开发、下次继续保留演示数据。

## 9. 结束并清空数据

如果需要重置数据库卷，执行：

```bash
docker compose down -v
```

该命令会删除 Docker volume 中的 PostgreSQL 数据。下次启动后需要重新执行：

```bash
docker compose exec backend alembic upgrade head
docker compose exec backend python -m app.db.seed
```

## 10. 宿主机产物检查

结束后建议检查宿主机是否残留项目依赖或构建产物：

```bash
git status --short
```

不应出现以下目录或文件：

```text
frontend/node_modules
frontend/dist
frontend/tsconfig.tsbuildinfo
backend/.venv
backend/.pytest_cache
backend/**/__pycache__
.venv
.pytest_cache
```

如果 `frontend/node_modules` 出现在宿主机项目目录中，说明曾经在宿主机执行过前端依赖安装或某些命令把容器依赖映射到了宿主机，应删除后继续使用 Docker 流程。

## 11. 常见问题

| 问题 | 处理方法 |
| --- | --- |
| 端口被占用 | 修改 `.env` 中的 `FRONTEND_PORT`、`BACKEND_PORT`、`POSTGRES_PORT` 后重启 |
| 前端打不开 | 执行 `docker compose ps`，确认 `labops-frontend` 是否 healthy |
| 后端接口失败 | 查看 `docker compose logs backend` |
| 数据库连接失败 | 查看 `docker compose logs postgres`，确认 backend 的 `DATABASE_URL` 主机名为 `postgres` |
| 登录账号不存在 | 重新执行 `docker compose exec backend python -m app.db.seed` |
| 数据混乱 | 执行 `docker compose down -v` 后重新启动、迁移、导入种子数据 |

## 12. 答辩说明话术

可以这样介绍：

> 这个项目的运行环境全部放在 Docker 容器里，前端、后端和 PostgreSQL 都由 Docker Compose 编排。宿主机不安装项目级 Python、Node 或数据库依赖，所以演示和测试环境是可复现的。

测试部分可以这样说：

> 后端通过容器内 pytest 验证登录、权限、设备、预约、报修、工单、通知、审计和系统管理等核心流程；前端通过 Docker build 执行 TypeScript 检查和 Vite 生产构建，避免只在开发环境能跑。

结束部分可以这样说：

> 普通结束使用 `docker compose down` 保留数据库数据；如果需要恢复全新演示环境，使用 `docker compose down -v` 清空数据库卷，再重新执行迁移和种子数据初始化。
