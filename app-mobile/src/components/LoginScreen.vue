<template>
  <div class="login-wrap">
    <div class="login-card">
      <div class="login-logo">🍷</div>
      <h1>Home Cellar</h1>
      <form @submit.prevent="signIn">
        <input
          v-model="email"
          type="email"
          placeholder="Email"
          autocomplete="email"
          required
        />
        <input
          v-model="password"
          type="password"
          placeholder="Password"
          autocomplete="current-password"
          required
        />
        <button type="submit" :disabled="loading">
          {{ loading ? 'Signing in…' : 'Sign in' }}
        </button>
        <p v-if="error" class="error">{{ error }}</p>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { supabase } from '../supabase'

const emit = defineEmits(['signed-in'])

const email    = ref('')
const password = ref('')
const loading  = ref(false)
const error    = ref('')

async function signIn() {
  loading.value = true
  error.value   = ''
  const { data, error: err } = await supabase.auth.signInWithPassword({
    email: email.value,
    password: password.value,
  })
  loading.value = false
  if (err) {
    error.value = err.message
  } else {
    emit('signed-in', data.session)
  }
}
</script>

<style scoped>
.login-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: #f5f6fa;
  padding: 20px;
}

.login-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 16px rgba(0,0,0,0.12);
  padding: 48px 36px;
  width: 100%;
  max-width: 360px;
  text-align: center;
}

.login-logo { font-size: 3rem; margin-bottom: 10px; }
h1 { font-size: 1.4rem; font-weight: 600; color: #2c3e50; margin-bottom: 32px; }

form { display: flex; flex-direction: column; gap: 14px; }

input {
  padding: 14px 16px;
  border: 1px solid #ccc;
  border-radius: 8px;
  font-size: 1rem;
  outline: none;
  -webkit-appearance: none;
}
input:focus { border-color: #8B1A1A; }

button {
  padding: 14px;
  background: #8B1A1A;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  margin-top: 4px;
  min-height: 50px;
}
button:active:not(:disabled) { background: #6d1414; }
button:disabled { opacity: 0.6; cursor: not-allowed; }

.error {
  color: #c0392b;
  font-size: 0.875rem;
  margin-top: 2px;
}
</style>
