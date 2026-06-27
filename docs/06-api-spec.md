# LabOps API 接口规划

## 1. 接口风格

- Base URL: `/api/v1`
- 数据格式: JSON
- 认证方式: JWT Bearer Token
- 时间格式: ISO 8601，例如 `2026-06-26T09:00:00+08:00`
- 主键格式: UUID 字符串
- 分页参数: `page` 从 1 开始，`page_size` 默认 20，最大 100

## 2. 通用响应

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
  "code": 40003,
  "message": "insufficient permission",
  "data": null
}
```

## 3. 状态码约定

| code | HTTP 状态 | 说明 |
| --- | --- | --- |
| 0 | 2xx | 成功 |
| 40000 | 400 / 422 | 请求参数错误 |
| 40001 | 401 | 未登录、登录失败或 token 无效 |
| 40003 | 403 | 无权限 |
| 40004 | 404 | 资源不存在 |
| 40900 | 409 | 业务冲突，例如预约时间冲突 |
| 50000 | 500 | 服务端异常 |

## 4. 认证接口

### POST `/auth/login`

用户登录，返回访问令牌和当前用户信息。

请求体：

```json
{
  "username": "ordinary01",
  "password": "labops123"
}
```

响应数据：

```json
{
  "access_token": "jwt-token",
  "token_type": "bearer",
  "expires_in": 7200,
  "user": {
    "id": "604e65b6-2ab3-58a7-9708-770e8836d018",
    "username": "ordinary01",
    "real_name": "Ordinary User Demo",
    "roles": ["ordinary_user"],
    "permissions": [
      "dashboard:view",
      "device:view",
      "reservation:view_self",
      "reservation:create",
      "reservation:cancel_self",
      "repair:view_self",
      "repair:create"
    ]
  }
}
```

### GET `/auth/me`

获取当前登录用户信息。前端根据 `roles` 和 `permissions` 决定登录后进入哪个工作台。

角色分流规则：

- `ordinary_user` / `student`: `/ordinary`
- `device_owner`: `/owner`
- `lab_admin` / `system_admin` / `teacher`: `/dashboard`

### POST `/auth/logout`

退出登录。当前版本由前端清理本地 token，后端保留扩展 token 黑名单的能力。

## 5. 当前演示账号

| 身份 | 用户名 | 密码 | 角色 | 主要权限 |
| --- | --- | --- | --- | --- |
| 普通用户 | `ordinary01` | `labops123` | `ordinary_user` | 预约、取消本人预约、提交报修、查看本人数据 |
| 设备负责人 | `owner01` | `labops123` | `device_owner` | 负责设备维护、预约审批、报修派工、工单推进 |
| 实验室管理员 | `labadmin01` | `labops123` | `lab_admin` | 业务全局管理 |
| 系统管理员 | `admin` | `password` | `system_admin` | 全局业务、用户、角色、权限管理 |

## 6. 看板接口

### GET `/dashboard/summary`

指标卡片汇总。

响应数据：

```json
{
  "device_total": 9,
  "device_available": 5,
  "today_reservations": 2,
  "pending_repairs": 1,
  "open_work_orders": 3
}
```

数据范围：

- 普通用户返回本人预约和本人报修相关摘要。
- 设备负责人返回本人负责设备相关摘要。
- 管理员返回全局摘要。

### GET `/dashboard/device-utilization`

设备利用率或设备健康度趋势。

### GET `/dashboard/repair-trend`

报修趋势。

### GET `/dashboard/reservation-status`

预约状态分布。

## 7. 设备接口

| 方法 | 路径 | 说明 | 关键权限 |
| --- | --- | --- | --- |
| GET | `/devices` | 设备列表 | `device:view` |
| GET | `/devices/{device_id}` | 设备详情 | `device:view` |
| POST | `/devices` | 创建设备 | `device:create` |
| PUT | `/devices/{device_id}` | 更新设备 | `device:update` |
| PATCH | `/devices/{device_id}/status` | 更新设备状态 | `device:update` |
| DELETE | `/devices/{device_id}` | 停用设备 | `device:delete` |

数据范围：

- 普通用户可以查看设备列表，用于预约和报修。
- 设备负责人只能查看和更新 `manager_id == 当前用户` 的设备。
- 设备负责人不能通过 `PUT /devices/{id}` 修改 `manager_id`。
- 管理员可以管理全局设备。

## 8. 预约接口

| 方法 | 路径 | 说明 | 关键权限 |
| --- | --- | --- | --- |
| GET | `/reservations` | 预约列表 | `reservation:view_self` 或 `reservation:view_all` |
| GET | `/reservations/{reservation_id}` | 预约详情 | `reservation:view_self` 或 `reservation:view_all` |
| POST | `/reservations` | 新建预约 | `reservation:create` |
| POST | `/reservations/{reservation_id}/approve` | 通过预约 | `reservation:approve` |
| POST | `/reservations/{reservation_id}/reject` | 驳回预约 | `reservation:approve` |
| POST | `/reservations/{reservation_id}/cancel` | 取消预约 | `reservation:cancel_self` 或 `reservation:cancel_all` |

业务规则：

- 普通用户只能查看和取消本人预约。
- 设备负责人只能审批本人负责设备相关预约。
- 管理员可以查看和处理全局预约。
- 审批预约时会检查同一设备已批准时段是否冲突。

## 9. 报修接口

| 方法 | 路径 | 说明 | 关键权限 |
| --- | --- | --- | --- |
| GET | `/repair-reports` | 报修列表 | `repair:view_self` 或 `repair:view_all` |
| GET | `/repair-reports/{report_id}` | 报修详情 | `repair:view_self` 或 `repair:view_all` |
| POST | `/repair-reports` | 提交报修 | `repair:create` |

数据范围：

- 普通用户只能查看本人报修。
- 设备负责人只能查看本人负责设备相关报修。
- 管理员可以查看全局报修。

## 10. 工单接口

| 方法 | 路径 | 说明 | 关键权限 |
| --- | --- | --- | --- |
| GET | `/work-orders` | 工单列表 | `work_order:create` / `work_order:update` / `work_order:close` |
| GET | `/work-orders/{work_order_id}` | 工单详情 | `work_order:create` / `work_order:update` / `work_order:close` |
| POST | `/work-orders` | 创建工单 | `work_order:create` |
| PATCH | `/work-orders/{work_order_id}/status` | 更新工单状态 | `work_order:update` |
| POST | `/work-orders/{work_order_id}/finish` | 完成并关闭工单 | `work_order:close` |

业务规则：

- 普通用户不能创建或处理工单。
- 设备负责人只能为本人负责设备的报修创建和处理工单。
- 管理员可以处理全局工单。
- 创建工单后，关联报修状态会同步为已派单。
- 完成工单后，关联报修会进入关闭状态。

## 11. 权限说明

前端权限控制用于改善体验：

- 登录后跳转不同工作台。
- 菜单和按钮按角色显示。
- 普通用户和设备负责人不能进入完整管理员后台。

后端权限控制用于保证安全：

- `get_current_user` 解析 Bearer Token。
- `require_permissions` 校验必须具备的权限。
- `require_any_permission` 支持本人数据和全局数据的二选一授权。
- 普通用户、设备负责人的数据范围由后端查询条件限制。

越权访问应返回 403。
