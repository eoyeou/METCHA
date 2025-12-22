<template>
  <div id="cursor" ref="cursorRef" :class="{ 'cursor-hover': isHovering }"></div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const cursorRef = ref(null)
const isHovering = ref(false)

const handleMouseMove = (e) => {
  if (cursorRef.value) {
    cursorRef.value.style.left = e.clientX + 'px'
    cursorRef.value.style.top = e.clientY + 'px'
  }
  
  // Check if hovering over interactive elements
  const target = e.target
  if (target.closest('.hover-trigger') || target.closest('a') || target.closest('button') || target.closest('input') || target.closest('textarea')) {
    isHovering.value = true
  } else {
    isHovering.value = false
  }
}

onMounted(() => {
  document.addEventListener('mousemove', handleMouseMove)
})

onUnmounted(() => {
  document.removeEventListener('mousemove', handleMouseMove)
})
</script>

<style scoped>
#cursor {
    position: fixed; 
    top: 0; 
    left: 0; 
    width: 20px; 
    height: 20px;
    background: var(--accent-acid); 
    border-radius: 50%;
    pointer-events: none; 
    z-index: 9999;
    mix-blend-mode: difference;
    transition: transform 0.1s;
}

#cursor { 
    transform: scale(1); 
}

#cursor.cursor-hover {
    transform: scale(4);
}
</style>

