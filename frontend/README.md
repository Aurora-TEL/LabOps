# LabOps Frontend

Vue 3 + Vite + TypeScript + ECharts 前端看板，用于展示 LabOps 智能实验室设备预约与运维管理平台。

## 容器运行

前端不在宿主机安装 Node 依赖。请从项目根目录使用 Docker Compose：

```bash
docker compose up -d --build frontend
```

访问：

```text
http://localhost:5173
```

## 容器内构建

```bash
docker compose exec frontend npm run build
```

## 页面结构

```text
src/
  api/                 API 适配层，当前返回 mock 数据
  components/common/   指标卡片、状态标签、ECharts 面板
  layouts/             左侧导航 + 顶部栏的中后台布局
  mock/                看板、设备、预约、工单、分析 mock 数据
  router/              页面路由
  stores/              Pinia 运营数据 store
  styles/              全局浅色科技风样式
  views/
    dashboard/         首页指标卡片、图表和摘要
    devices/           设备台账与运行状态
    reservations/      预约列表
    repairs/           报修工单看板
    analytics/         数据分析页面
    system/            角色权限和系统设置规划
```

## 后续接接口计划

1. 在 `src/api/operations.ts` 中引入 HTTP client。
2. 将当前 `Promise.resolve(mock)` 替换为真实 `/api/v1` 请求。
3. 在 Pinia store 中补 loading、error、分页和筛选参数。
4. 将新增、审核、派工、验收等按钮接入后端 REST API。
