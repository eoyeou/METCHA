<template>
  <div class="hero-wrapper section-container" style="padding: 0;">
    <div class="hero-title-layer">
      <h1 class="kinetic-type">VISUAL<br>OVERLOAD</h1>
    </div>
    
    <div class="film-strip">
      <FilmFrame
        v-for="(film, index) in films"
        :key="index"
        :image-url="film.imageUrl"
        :title="film.title"
      />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import FilmFrame from './FilmFrame.vue'

const films = ref([
  {
    imageUrl: 'https://images.unsplash.com/photo-1535905557558-afc4877a26fc?auto=format&fit=crop&q=80&w=600',
    title: 'SCIFI_01'
  },
  {
    imageUrl: 'https://images.unsplash.com/photo-1626814026160-2237a95fc5a0?auto=format&fit=crop&q=80&w=600',
    title: 'DYSTOPIA'
  },
  {
    imageUrl: 'https://images.unsplash.com/photo-1542204165-65bf26472b9b?auto=format&fit=crop&q=80&w=600',
    title: 'NOIR_RED'
  },
  {
    imageUrl: 'https://images.unsplash.com/photo-1485846234645-a62644f84728?auto=format&fit=crop&q=80&w=600',
    title: 'ABSTRACT'
  }
])
</script>

<style scoped>
.hero-wrapper {
    height: 100vh;
    display: flex;
    align-items: center;
    overflow-x: auto; /* 가로 스크롤 */
    white-space: nowrap;
    scrollbar-width: none; /* 스크롤바 숨김 */
}

.hero-wrapper::-webkit-scrollbar { 
    display: none; 
}

.hero-title-layer {
    position: absolute; 
    top: 50%; 
    left: 50%; 
    transform: translate(-50%, -50%);
    z-index: 10; 
    pointer-events: none; 
    text-align: center;
}

.hero-title-layer h1 { 
    font-size: 10vw; 
    color: white; 
    mix-blend-mode: exclusion; 
}

.film-strip {
    display: flex; 
    gap: 0; 
    padding-left: 40px;
}
</style>

