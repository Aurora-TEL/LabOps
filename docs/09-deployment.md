# LabOps Docker 部署说明

## 1. 环境边界

LabOps 的运行环境全部放在 Docker 容器中。宿主机只需要：

- Git
- Docker
- Docker Compose

宿主机不需要安装 Python、Node.js、PostgreSQL，也不要在宿主机执行 `pip install`、`npm install`、`npm run build`、数据库初始化或项目测试依赖安装。

## 2. 服务组成

| 服务 | 容器名 | 说明 | 访问地址 |
| --- | --- | --- | --- |
| postgres | `labops-postgres` | PostgreSQL 数据库 | `localhost:5432` |
| backend | `labops-backend` | FastAPI 后端 | `http://localhost:8000` |
| frontend | `labops-frontend` | Vue3 / Vite 前端 | `http://localhost:5173` |

## 3. 启动

首次启动前复制环境变量模板：

```bash
cp .env.example .env
```

启动服务：

```bash
docker compose up --build
```

后台启动：

```bash
docker compose up -d --build
```

查看状态：

```bash
docker compose ps
```

查看日志：

```bash
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f postgres
```

## 4. 数据库初始化

```bash
docker compose exec backend alembic upgrade head
docker compose exec backend python -m app.db.seed
```

种子数据包含：

- `ordinary01 / labops123`
- `owner01 / labops123`
- `labadmin01 / labops123`
- `admin / password`
- 可演示的设备、预约、报修、工单和运营指标

## 5. 当前推荐验收命令

v1.3 最终集成验收建议执行：

```bash
docker compose build --progress=plain
docker compose up -d --force-recreate
docker compose ps
docker compose exec backend alembic upgrade head
docker compose exec backend python -m app.db.seed
docker compose run --rm -e PYTHONDONTWRITEBYTECODE=1 backend pytest -p no:cacheprovider
docker build --target build -t labops-frontend-build-check ./frontend
```

说明：

- 后端测试使用 `docker compose run`，避免在宿主机安装 Python 依赖。
- 前端生产构建使用 `docker build --target build`，避免 `dist` 写回宿主机。
- 更完整的 v1.3 演示路径见 [v1.3 验收与演示手册](15-v1.3-acceptance-demo.md)。

## 6. 访问地址

- 前端：`http://localhost:5173`
- 后端 Swagger：`http://localhost:8000/docs`
- 后端健康检查：`http://localhost:8000/api/v1/health/live`

## 7. 停止服务

停止服务：

```bash
docker compose down
```

停止并清空数据库卷：

```bash
docker compose down -v
```

## 8. 宿主机产物检查

验证结束后，宿主机不应残留：

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

检查命令：

```bash
git status --short
```

## 9. 常见排错

| 问题 | 建议 |
| --- | --- |
| 后端无法连接数据库 | 检查 `DATABASE_URL` 中主机名是否为 `postgres`，并查看 `docker compose logs postgres` |
| 前端请求 API 失败 | 检查 `VITE_API_BASE_URL` 是否指向 `http://localhost:8000/api/v1` |
| 健康检查失败 | 先执行 `docker compose ps`，再查看 `docker compose logs backend` 和 `docker compose logs frontend` |
| 端口被占用 | 在 `.env` 中调整 `BACKEND_PORT`、`FRONTEND_PORT` 或 `POSTGRES_PORT` 后重启 |
| 演示数据异常 | 执行迁移和种子数据导入；必要时使用 `docker compose down -v` 清空本地演示卷 |
