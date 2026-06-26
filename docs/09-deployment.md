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

## 3. 环境变量

首次启动前复制环境变量模板：

```bash
cp .env.example .env
```

关键变量：

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `POSTGRES_DB` | `labops` | 数据库名 |
| `POSTGRES_USER` | `labops` | 数据库用户 |
| `POSTGRES_PASSWORD` | `labops_dev_password` | 数据库密码 |
| `DATABASE_URL` | `postgresql+psycopg://labops:labops_dev_password@postgres:5432/labops` | 后端容器访问数据库的连接串 |
| `CORS_ORIGINS` | `["http://localhost:5173"]` | 后端允许的前端来源 |
| `VITE_API_BASE_URL` | `http://localhost:8000/api/v1` | 前端访问后端 API 的基础地址 |
| `VITE_API_PROXY_TARGET` | `http://backend:8000` | Vite 开发服务器代理 `/api` 的后端容器地址 |

前端 API client 会优先使用 `VITE_API_BASE_URL`。如果需要走容器内反向代理，可将 `VITE_API_BASE_URL` 设为 `/api/v1` 或不设置该变量；开发模式由 Vite 将 `/api` 转发到 `VITE_API_PROXY_TARGET`，预览镜像由 nginx 将 `/api/` 转发到 `backend:8000`。

## 4. 启动

在项目根目录执行：

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

## 5. 验证

后端健康检查：

```bash
curl http://localhost:8000/api/v1/health/live
```

前端访问：

```text
http://localhost:5173
```

Swagger 文档：

```text
http://localhost:8000/docs
```

## 6. 容器内命令

所有测试和维护命令都通过容器执行：

```bash
docker compose exec backend pytest
docker compose exec frontend npm run build
docker compose exec postgres psql -U labops -d labops
```

## 7. 停止

停止服务：

```bash
docker compose down
```

停止并清空数据库卷：

```bash
docker compose down -v
```
