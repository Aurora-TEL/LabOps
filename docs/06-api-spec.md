# API 接口规划

## 接口风格

- Base URL: `/api/v1`
- 数据格式：JSON
- 认证方式：JWT Bearer Token
- 时间格式：ISO 8601，例如 `2026-06-26T09:00:00+08:00`
- 主键格式：UUID 字符串
- 分页参数：`page` 从 1 开始，`page_size` 默认 20，最大 100
- 排序参数：`sort` 使用字段名，降序使用 `-` 前缀，例如 `-created_at`

## 通用响应

成功响应：

```json
{
  "code": 0,
  "message": "ok",
  "data": {}
}
```

分页响应：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "items": [],
    "page": 1,
    "page_size": 20,
    "total": 0
  }
}
```

错误响应：

```json
{
  "code": 40001,
  "message": "invalid username or password",
  "data": null
}
```

## 状态码约定

| code | HTTP 状态 | 说明 |
| --- | --- | --- |
| 0 | 2xx | 成功 |
| 40000 | 400 | 请求参数错误 |
| 40001 | 401 | 未登录或登录失败 |
| 40003 | 403 | 无权限 |
| 40004 | 404 | 资源不存在 |
| 40900 | 409 | 业务冲突，例如预约时间冲突 |
| 50000 | 500 | 服务端异常 |

## 通用实体字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | UUID | 资源 ID |
| created_at | datetime | 创建时间 |
| updated_at | datetime | 更新时间 |

## 认证接口

### POST `/auth/login`

用户登录，返回访问令牌和当前用户摘要。

请求体：

```json
{
  "username": "admin",
  "password": "password"
}
```

响应数据：

```json
{
  "access_token": "jwt-token",
  "token_type": "bearer",
  "expires_in": 7200,
  "user": {
    "id": "00000000-0000-0000-0000-000000000000",
    "username": "admin",
    "real_name": "系统管理员",
    "roles": ["admin"]
  }
}
```

### POST `/auth/logout`

用户退出。当前阶段由前端清理 token，后端预留 token 黑名单能力。

### GET `/auth/me`

获取当前登录用户信息。

## 健康检查接口

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/health/live` | 进程存活检查，不访问数据库 |
| GET | `/health/ready` | 就绪检查，包含数据库连接探测 |

## 看板接口

### GET `/dashboard/summary`

指标卡片汇总。

响应数据：

```json
{
  "device_total": 128,
  "device_available": 96,
  "today_reservations": 18,
  "pending_repairs": 7,
  "open_work_orders": 5
}
```

### GET `/dashboard/device-utilization`

设备利用率趋势。

查询参数：

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| start_date | date | 起始日期 |
| end_date | date | 结束日期 |
| lab_id | UUID | 可选，实验室 ID |

### GET `/dashboard/reservation-status`

预约状态分布。

### GET `/dashboard/repair-trend`

报修趋势。

查询参数与设备利用率趋势一致。

## 设备接口

### 设备状态

| 状态 | 说明 |
| --- | --- |
| available | 可预约 |
| reserved | 已预约 |
| in_use | 使用中 |
| maintenance | 维护中 |
| disabled | 停用 |

### GET `/devices`

设备列表。

查询参数：

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| page | int | 页码 |
| page_size | int | 每页数量 |
| keyword | string | 设备编号或名称 |
| lab_id | UUID | 实验室筛选 |
| category_id | UUID | 分类筛选 |
| status | string | 状态筛选 |

### POST `/devices`

创建设备。

请求体：

```json
{
  "code": "DEV-001",
  "name": "高速离心机",
  "category_id": "00000000-0000-0000-0000-000000000000",
  "lab_id": "00000000-0000-0000-0000-000000000000",
  "manager_id": "00000000-0000-0000-0000-000000000000",
  "status": "available",
  "health_score": 96.5,
  "purchase_date": "2025-09-01"
}
```

### GET `/devices/{id}`

设备详情。

### PUT `/devices/{id}`

更新设备基础信息。

### PATCH `/devices/{id}/status`

更新设备状态。

请求体：

```json
{
  "status": "maintenance",
  "reason": "定期维护"
}
```

### DELETE `/devices/{id}`

删除设备。建议实现为软删除或停用，避免影响历史预约与工单。

## 预约接口

### 预约状态

| 状态 | 说明 |
| --- | --- |
| pending | 待审核 |
| approved | 已通过 |
| rejected | 已拒绝 |
| canceled | 已取消 |
| completed | 已完成 |

### GET `/reservations`

预约列表。

查询参数：

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| page | int | 页码 |
| page_size | int | 每页数量 |
| device_id | UUID | 设备筛选 |
| applicant_id | UUID | 申请人筛选 |
| status | string | 状态筛选 |
| start_time | datetime | 开始时间下限 |
| end_time | datetime | 结束时间上限 |

### POST `/reservations`

提交预约。

请求体：

```json
{
  "device_id": "00000000-0000-0000-0000-000000000000",
  "start_time": "2026-06-27T09:00:00+08:00",
  "end_time": "2026-06-27T11:00:00+08:00",
  "purpose": "材料样品检测"
}
```

业务规则：

- `end_time` 必须晚于 `start_time`
- 同一设备同一时间段不能存在已通过或使用中的冲突预约
- 普通用户只能取消自己的预约，管理员和实验室管理员可审核预约

### GET `/reservations/{id}`

预约详情。

### POST `/reservations/{id}/approve`

审核通过。

### POST `/reservations/{id}/reject`

审核拒绝。

请求体：

```json
{
  "reject_reason": "该时段设备需要维护"
}
```

### POST `/reservations/{id}/cancel`

取消预约。

## 报修接口

### 报修状态

| 状态 | 说明 |
| --- | --- |
| submitted | 已提交 |
| accepted | 已受理 |
| assigned | 已派单 |
| closed | 已关闭 |

### GET `/repair-reports`

报修列表。

查询参数：

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| page | int | 页码 |
| page_size | int | 每页数量 |
| device_id | UUID | 设备筛选 |
| reporter_id | UUID | 报修人筛选 |
| status | string | 状态筛选 |
| fault_type | string | 故障类型筛选 |

### POST `/repair-reports`

提交报修。

请求体：

```json
{
  "device_id": "00000000-0000-0000-0000-000000000000",
  "fault_type": "hardware",
  "description": "设备启动后异常震动"
}
```

### GET `/repair-reports/{id}`

报修详情。

## 工单接口

### 工单状态

| 状态 | 说明 |
| --- | --- |
| pending | 待处理 |
| processing | 处理中 |
| finished | 已完成 |
| canceled | 已取消 |

### GET `/work-orders`

工单列表。

查询参数：

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| page | int | 页码 |
| page_size | int | 每页数量 |
| assignee_id | UUID | 处理人筛选 |
| status | string | 状态筛选 |
| priority | string | 优先级筛选 |

### POST `/work-orders`

创建工单。

请求体：

```json
{
  "repair_report_id": "00000000-0000-0000-0000-000000000000",
  "assignee_id": "00000000-0000-0000-0000-000000000000",
  "priority": "high"
}
```

### GET `/work-orders/{id}`

工单详情。

### PATCH `/work-orders/{id}/status`

更新工单状态。

请求体：

```json
{
  "status": "processing"
}
```

### POST `/work-orders/{id}/finish`

完成工单。

请求体：

```json
{
  "result": "更换转子固定组件，试运行正常"
}
```

## 系统管理接口

系统管理接口后续用于角色权限与基础数据维护，本阶段仅保留规划。

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/users` | 用户列表 |
| POST | `/users` | 创建用户 |
| GET | `/roles` | 角色列表 |
| GET | `/permissions` | 权限列表 |
| GET | `/labs` | 实验室列表 |
| POST | `/labs` | 创建实验室 |

## v1.1 backend implementation notes

- The current backend business endpoints return the unified `{code, message, data}` envelope for both success and common API errors.
- List endpoints support `page` and `page_size` consistently. Device, reservation, repair report, and work order list endpoints also support the filters documented above.
- Until the database model integration lands, the business layer uses an in-memory service boundary in `backend/app/services/business.py`. Endpoint handlers are intentionally thin so the service can be replaced by SQLAlchemy repositories without changing the REST contract.
- Reservation creation and approval check approved-reservation time conflicts for the same device and return `40900` on conflicts.
- Work order creation marks the linked repair report as `assigned`; finishing a work order marks the linked repair report as `closed`.
