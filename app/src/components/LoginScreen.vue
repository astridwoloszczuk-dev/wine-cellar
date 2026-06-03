<template>
  <div class="login-wrap">
    <div class="login-card">
      <div class="login-logo">🍷</div>
      <h1>Wine Cellar</h1>
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
  height: 100vh;
  background: #f5f6fa;
}

.login-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 16px rgba(0,0,0,0.12);
  padding: 40px 36px;
  width: 320px;
  text-align: center;
}

.login-logo { font-size: 2.5rem; margin-bottom: 8px; }
h1 { font-size: 1.3rem; font-weight: 600; color: #2c3e50; margin-bottom: 28px; }

form { display: flex; flex-direction: column; gap: 12px; }

input {
  padding: 9px 12px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 0.9rem;
  outline: none;
}
input:focus { border-color: #8B1A1A; }

button {
  padding: 10px;
  background: #8B1A1A;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  margin-top: 4px;
}
button:hover:not(:disabled) { background: #a02020; }
button:disabled { opacity: 0.6; cursor: not-allowed; }

.error {
  color: #c0392b;
  font-size: 0.82rem;
  margin-top: 2px;
}
</style>
