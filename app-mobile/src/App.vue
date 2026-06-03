<template>
  <LoginScreen v-if="!session" @signed-in="session = $event" />
  <WineList v-else @sign-out="signOut" />
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { supabase } from './supabase'
import LoginScreen from './components/LoginScreen.vue'
import WineList    from './components/WineList.vue'

const session = ref(null)

async function signOut() {
  await supabase.auth.signOut()
  session.value = null
}

onMounted(async () => {
  const { data } = await supabase.auth.getSession()
  session.value = data.session
  supabase.auth.onAuthStateChange((_event, s) => { session.value = s })
})
</script>

<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: #f5f6fa;
  color: #2c3e50;
  -webkit-text-size-adjust: 100%;
  overscroll-behavior: none;
}

#app { height: 100vh; overflow: hidden; }
</style>
