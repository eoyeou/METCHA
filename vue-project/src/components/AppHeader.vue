<template>
  <header>
    <div class="logo hover-trigger">METCHA</div>
    <div class="nav-items hover-trigger">
      <span>Archive</span>
      <span>Index</span>
      <span>Connect</span>
    </div>
  </header>
</template>

<script setup>
// Header component
</script>

<style scoped>
header {
    position: fixed; 
    top: 0; 
    left: 0; 
    width: 100%; 
    padding: 20px 40px;
    display: flex; 
    justify-content: space-between; 
    align-items: center;
    z-index: 100; 
    mix-blend-mode: difference;
}

.logo { 
    font-family: var(--font-display); 
    font-weight: 700; 
    letter-spacing: -2px; 
    font-size: 1.5rem; 
}

.nav-items { 
    display: flex; 
    gap: 30px; 
    font-size: 0.9rem; 
    text-transform: uppercase; 
    letter-spacing: 1px; 
}
</style>

