<template>
  <div id="app">
    <CustomCursor />
    <RouterView />
  </div>
</template>

<script setup>
import { RouterView } from 'vue-router'
import CustomCursor from './components/CustomCursor.vue'
</script>

<style>
</style>
