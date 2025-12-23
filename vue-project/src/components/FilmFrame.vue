<template>
  <div class="film-frame hover-trigger">
    <img :src="imageUrl" :alt="title" class="film-img">
    <div class="film-label">{{ title }}</div>
  </div>
</template>

<script setup>
defineProps({
  imageUrl: {
    type: String,
    required: true
  },
  title: {
    type: String,
    required: true
  }
})
</script>

<style scoped>
.film-frame {
    width: 40vw; 
    height: 70vh;
    position: relative;
    margin-right: 5vw;
    flex-shrink: 0;
    transition: 0.5s;
    overflow: hidden;
    border: 1px solid #333;
}

.film-frame:hover { 
    transform: scale(1.05) skewX(-2deg); 
    border-color: var(--accent-acid); 
}

.film-img {
    width: 100%; 
    height: 100%; 
    object-fit: cover;
    filter: grayscale(100%) contrast(120%);
    transition: 0.5s;
}

.film-frame:hover .film-img { 
    filter: grayscale(0%); 
}

.film-label {
    position: absolute; 
    bottom: 20px; 
    left: 20px; 
    font-family: var(--font-display); 
    font-size: 2rem; 
    mix-blend-mode: difference;
}
</style>

