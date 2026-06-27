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
  username: 'admin',
  password: 'password'
});

async function submitLogin() {
  await authStore.signIn(form.username, form.password);
  await router.replace(String(route.query.redirect ?? '/dashboard'));
}
</script>

<template>
  <main class="login-page">
    <section class="login-shell">
      <div class="login-copy">
        <p class="eyebrow">LabOps v1.2</p>
        <h1>登录运营中心</h1>
        <p class="subtle">演示账号已预填。登录后前端会保存 token，并通过 /auth/me 恢复当前用户。</p>
        <div class="login-metrics">
          <span>设备台账</span>
          <span>预约审批</span>
          <span>报修工单</span>
        </div>
      </div>

      <form class="panel login-form" @submit.prevent="submitLogin">
        <div>
          <h2>账号登录</h2>
          <p class="subtle">用于答辩演示的轻量认证流程</p>
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
  width: min(980px, 100%);
  grid-template-columns: minmax(0, 1fr) 390px;
  gap: 28px;
  align-items: center;
}

.login-copy h1 {
  max-width: 520px;
  font-size: 44px;
}

.login-copy .subtle {
  max-width: 560px;
}

.login-metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 24px;
}

.login-metrics span {
  border: 1px solid #d8e5f4;
  border-radius: 999px;
  background: #fff;
  color: var(--blue);
  padding: 8px 12px;
  font-size: 13px;
  font-weight: 900;
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
  .login-shell {
    grid-template-columns: 1fr;
  }

  .login-copy h1 {
    font-size: 34px;
  }
}
</style>
