<script setup lang="ts">
const handleWrite = () => {
  console.log('글쓰기 클릭')
}
</script>

<template>
  <button class="write-button" @click="handleWrite">
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25z" />
      <path d="M20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z" />
    </svg>
    <span>글쓰기</span>
  </button>
</template>

<style scoped>
.write-button {
  position: fixed;
  bottom: 32px;
  right: 32px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border: none;
  border-radius: 50px;
  background-color: #333;
  color: #ffffff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  z-index: 100;
}

.write-button:hover {
  background-color: #555;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.3);
  transform: translateY(-2px);
}

.write-button svg {
  width: 18px;
  height: 18px;
}

@media (max-width: 640px) {
  .write-button {
    bottom: 24px;
    right: 24px;
    padding: 10px 20px;
    font-size: 13px;
  }

  .write-button svg {
    width: 16px;
    height: 16px;
  }
}
</style>
