<script setup lang="ts">
import { LockKeyhole, LogIn, UserRound } from 'lucide-vue-next';
import { reactive } from 'vue';
import { useRoute, useRouter } from 'vue-router';

import DataState from '@/components/common/DataState.vue';
import { useAuthStore } from '@/stores/auth';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const form = reactive({
  username: 'ordinary01',
  password: 'labops123'
});

const demoAccounts = [
  { label: '普通用户', username: 'ordinary01', password: 'labops123', note: '预约设备、提交报修、查看个人记录' },
  { label: '设备负责人', username: 'owner01', password: 'labops123', note: '设备状态维护、预约审批、维修工单' },
  { label: '实验室管理员', username: 'labadmin01', password: 'labops123', note: '全局设备、预约、报修运营后台' },
  { label: '系统管理员', username: 'admin', password: 'password', note: '用户角色、系统配置与全局管理' }
];

function useAccount(account: (typeof demoAccounts)[number]) {
  form.username = account.username;
  form.password = account.password;
}

async function submitLogin() {
  await authStore.signIn(form.username, form.password);
  const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : authStore.landingPath;
  await router.replace(redirect === '/dashboard' && !authStore.isAdminUser ? authStore.landingPath : redirect);
}
</script>

<template>
  <main class="login-page">
    <section class="login-shell">
      <div class="login-copy">
        <p class="eyebrow">LabOps v1.3</p>
        <h1>智能实验室设备预约与运维平台</h1>
        <p class="subtle">按身份进入不同前端：普通用户使用预约报修自助台，设备负责人进入运维工作台，管理员进入完整运营后台。</p>
        <div class="account-grid">
          <button v-for="account in demoAccounts" :key="account.username" class="account-card" type="button" @click="useAccount(account)">
            <strong>{{ account.label }}</strong>
            <span>{{ account.username }}</span>
            <small>{{ account.note }}</small>
          </button>
        </div>
      </div>

      <form class="panel login-form" @submit.prevent="submitLogin">
        <div>
          <h2>账号登录</h2>
          <p class="subtle">选择左侧演示账号后登录，系统会自动进入对应工作台。</p>
        </div>

        <label class="form-field">
          <span>用户名</span>
          <div>
            <UserRound :size="18" />
            <input v-model.trim="form.username" required autocomplete="username" />
          </div>
        </label>

        <label class="form-field">
          <span>密码</span>
          <div>
            <LockKeyhole :size="18" />
            <input v-model="form.password" required type="password" autocomplete="current-password" />
          </div>
        </label>

        <DataState v-if="authStore.error" :error="authStore.error" />

        <button class="text-button primary submit-button" type="submit" :disabled="authStore.loading">
          <LogIn :size="18" />{{ authStore.loading ? '登录中' : '登录' }}
        </button>
      </form>
    </section>
  </main>
</template>

<style scoped>
.login-page {
  display: grid;
  min-height: 100vh;
  place-items: center;
  background:
    linear-gradient(120deg, rgba(247, 251, 255, 0.96), rgba(231, 241, 251, 0.92)),
    repeating-linear-gradient(90deg, rgba(23, 105, 224, 0.045) 0 1px, transparent 1px 86px);
  padding: 24px;
}

.login-shell {
  display: grid;
  width: min(1040px, 100%);
  grid-template-columns: minmax(0, 1fr) 390px;
  gap: 28px;
  align-items: center;
}

.login-copy h1 {
  max-width: 620px;
  font-size: 44px;
}

.login-copy .subtle {
  max-width: 650px;
}

.account-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin-top: 24px;
}

.account-card {
  display: flex;
  min-height: 122px;
  flex-direction: column;
  align-items: flex-start;
  gap: 7px;
  border: 1px solid #d8e5f4;
  border-radius: 8px;
  background: #fff;
  color: #172033;
  padding: 14px;
  text-align: left;
  box-shadow: 0 12px 28px rgba(26, 57, 96, 0.08);
}

.account-card:hover {
  border-color: var(--blue);
}

.account-card strong {
  font-size: 16px;
}

.account-card span {
  color: var(--blue);
  font-size: 13px;
  font-weight: 900;
}

.account-card small {
  color: var(--muted);
  line-height: 1.5;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 18px;
  padding: 24px;
}

.form-field {
  display: grid;
  gap: 8px;
  color: #304057;
  font-size: 13px;
  font-weight: 800;
}

.form-field div {
  display: flex;
  align-items: center;
  gap: 10px;
  min-height: 42px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: #fff;
  padding: 0 12px;
  color: var(--muted);
}

.form-field input {
  width: 100%;
  min-width: 0;
  border: 0;
  outline: 0;
  color: var(--text);
}

.submit-button {
  width: 100%;
  min-height: 42px;
}

@media (max-width: 820px) {
  .login-shell,
  .account-grid {
    grid-template-columns: 1fr;
  }

  .login-copy h1 {
    font-size: 34px;
  }
}
</style>
