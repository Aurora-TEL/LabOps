# LabOps Backend

FastAPI 后端服务，提供认证占位、设备、预约、报修、工单和 Dashboard 统计接口骨架。

## 容器运行

后端不在宿主机安装 Python 依赖。请从项目根目录使用 Docker Compose：

```bash
docker compose up -d --build backend
```

默认地址：

- API: `http://localhost:8000/api/v1`
- Swagger: `http://localhost:8000/docs`
- Live health: `http://localhost:8000/api/v1/health/live`
- Ready health: `http://localhost:8000/api/v1/health/ready`

## 容器内测试

```bash
docker compose exec backend pytest
```

## 当前路由

- `GET /api/v1/health/live`
- `GET /api/v1/health/ready`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/logout`
- `GET /api/v1/auth/me`
- `GET|POST /api/v1/devices`
- `GET|PUT|DELETE /api/v1/devices/{device_id}`
- `PATCH /api/v1/devices/{device_id}/status`
- `GET|POST /api/v1/reservations`
- `GET /api/v1/reservations/{reservation_id}`
- `POST /api/v1/reservations/{reservation_id}/approve`
- `POST /api/v1/reservations/{reservation_id}/reject`
- `POST /api/v1/reservations/{reservation_id}/cancel`
- `GET|POST /api/v1/repair-reports`
- `GET /api/v1/repair-reports/{report_id}`
- `GET|POST /api/v1/work-orders`
- `GET /api/v1/work-orders/{work_order_id}`
- `PATCH /api/v1/work-orders/{work_order_id}/status`
- `POST /api/v1/work-orders/{work_order_id}/finish`
- `GET /api/v1/dashboard/summary`
- `GET /api/v1/dashboard/device-utilization`
- `GET /api/v1/dashboard/reservation-status`
- `GET /api/v1/dashboard/repair-trend`

## 下一步

1. 按 `docs/05-database-design.md` 补 SQLAlchemy models 和 Alembic 首个迁移。
2. 将占位数据下沉到 service 层并接入真实数据库。
3. 实现 JWT 登录、密码哈希和角色权限校验。
4. 补预约时间冲突、工单状态流转等业务规则测试。
