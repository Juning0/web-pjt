<script setup lang="ts">
import { RouterView } from 'vue-router'
import ChatBot from './components/ChatBot.vue'
</script>

<template>
  <RouterView />
  <ChatBot />
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #app {
  width: 100%;
  height: 100%;
  background-color: #ffffff;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  color: #333;
}
</style>
