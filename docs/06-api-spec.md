# API 接口规划

## 接口风格

- Base URL: `/api/v1`
- 数据格式：JSON
- 认证方式：JWT Bearer Token
- 时间格式：ISO 8601

## 通用响应

```json
{
  "code": 0,
  "message": "ok",
  "data": {}
}
```

## 认证接口

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/auth/login` | 用户登录 |
| POST | `/auth/logout` | 用户退出 |
| GET | `/auth/me` | 获取当前用户 |

## 看板接口

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/dashboard/summary` | 指标卡片汇总 |
| GET | `/dashboard/device-utilization` | 设备利用率趋势 |
| GET | `/dashboard/reservation-status` | 预约状态分布 |
| GET | `/dashboard/repair-trend` | 报修趋势 |

## 设备接口

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/devices` | 设备列表 |
| POST | `/devices` | 创建设备 |
| GET | `/devices/{id}` | 设备详情 |
| PUT | `/devices/{id}` | 更新设备 |
| PATCH | `/devices/{id}/status` | 更新设备状态 |
| DELETE | `/devices/{id}` | 删除设备 |

## 预约接口

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/reservations` | 预约列表 |
| POST | `/reservations` | 提交预约 |
| GET | `/reservations/{id}` | 预约详情 |
| POST | `/reservations/{id}/approve` | 审核通过 |
| POST | `/reservations/{id}/reject` | 审核拒绝 |
| POST | `/reservations/{id}/cancel` | 取消预约 |

## 报修与工单接口

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/repair-reports` | 报修列表 |
| POST | `/repair-reports` | 提交报修 |
| GET | `/repair-reports/{id}` | 报修详情 |
| POST | `/work-orders` | 创建工单 |
| GET | `/work-orders` | 工单列表 |
| PATCH | `/work-orders/{id}/status` | 更新工单状态 |
| POST | `/work-orders/{id}/finish` | 完成工单 |

## 系统管理接口

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/users` | 用户列表 |
| POST | `/users` | 创建用户 |
| GET | `/roles` | 角色列表 |
| GET | `/permissions` | 权限列表 |
| GET | `/labs` | 实验室列表 |
| POST | `/labs` | 创建实验室 |
