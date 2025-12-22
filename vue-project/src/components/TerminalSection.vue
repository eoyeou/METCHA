<template>
  <div class="section-container terminal-section">
    <div class="section-label">INPUT_DATA // REVIEW</div>
    
    <input 
      type="text" 
      class="input-huge hover-trigger" 
      placeholder="TYPE_TITLE"
      v-model="title"
    >
    
    <input 
      type="range" 
      class="range-slider hover-trigger" 
      min="0" 
      max="100"
      v-model="rating"
      @input="updateRating"
    >
    <div class="rating-display">
      RATING_VAL: <span>{{ rating }}</span>%
    </div>

    <textarea 
      class="input-huge textarea-input" 
      placeholder="ENTER_THOUGHTS..."
      v-model="thoughts"
    ></textarea>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const title = ref('')
const rating = ref(50)
const thoughts = ref('')

const updateRating = () => {
  // Rating is automatically updated via v-model
}
</script>

<style scoped>
.terminal-section {
    display: flex; 
    align-items: center; 
    justify-content: center; 
    flex-direction: column;
    background: #050505;
}

.section-label {
    font-family: var(--font-display); 
    margin-bottom: 20px; 
    color: #333;
}

.input-huge {
    background: transparent; 
    border: none; 
    border-bottom: 2px solid #333;
    font-size: 3rem; 
    color: var(--text-primary); 
    font-family: var(--font-tech);
    width: 80%; 
    text-align: center; 
    padding: 20px; 
    outline: none;
    transition: 0.3s;
}

.input-huge:focus { 
    border-color: var(--accent-acid); 
    letter-spacing: 2px; 
}

.input-huge::placeholder { 
    color: #333; 
    -webkit-text-stroke: 1px #333; 
    color: transparent; 
}

.textarea-input {
    font-size: 1.5rem; 
    height: 150px; 
    resize: none; 
    border: 1px solid #333; 
    margin-top: 40px;
    text-align: left;
    padding: 20px;
}

.range-slider {
    -webkit-appearance: none; 
    width: 50%; 
    height: 2px; 
    background: #333; 
    margin: 40px 0;
}

.range-slider::-webkit-slider-thumb {
    -webkit-appearance: none; 
    width: 20px; 
    height: 20px; 
    background: var(--accent-acid); 
    cursor: none;
    box-shadow: 0 0 20px var(--accent-acid);
}

.rating-display {
    font-family: var(--font-tech); 
    color: var(--accent-acid);
}

.rating-display span {
    color: var(--accent-acid);
}
</style>

