<template>
  <div class="detail-layout section-container" style="padding:0;">
    <div class="visual-area">
      <div class="visual-overlay"></div>
      <h1 class="rotated-title">DUNE:PART2</h1>
    </div>
    
    <div class="content-area">
      <div class="floating-tag">NOW_PLAYING</div>
      
      <h2 class="big-title hover-trigger">
        DUNE:<br>
        <span style="color:var(--accent-acid)">PROPHET</span>
      </h2>
      
      <div class="meta-data">
        ID: 2024_DV_02 <br>
        RUNTIME: 166m <br>
        AUDIO: ATMOS_MAX
      </div>

      <p class="description">
        모래와 스파이스, 그리고 운명. <br>
        시각적 쾌감이 극대화된 스페이스 오페라의 정점. 
        단순한 영화가 아니라 체험에 가깝다.
      </p>

      <div class="review-glitch hover-trigger">
        <strong style="color:var(--accent-acid)">USER_X99:</strong> <br>
        "압도적이다. 스크린이 나를 삼키는 느낌."
      </div>
    </div>
  </div>
</template>

<script setup>
// Detail section component
</script>

<style scoped>
.detail-layout {
    display: grid; 
    grid-template-columns: 2fr 1fr;
    min-height: 100vh;
}

.visual-area {
    position: relative;
    background: url('https://images.unsplash.com/photo-1626814026160-2237a95fc5a0?auto=format&fit=crop&q=80&w=800') no-repeat center/cover;
    filter: grayscale(100%);
}

.visual-overlay {
    position: absolute; 
    top: 0; 
    left: 0; 
    width: 100%; 
    height: 100%;
    background: linear-gradient(180deg, transparent 0%, #000 100%);
}

.rotated-title {
    position: absolute; 
    bottom: -40px; 
    left: -20px; 
    font-size: 8rem; 
    color: transparent; 
    -webkit-text-stroke: 2px white; 
    opacity: 0.2; 
    transform: rotate(-90deg); 
    transform-origin: left bottom;
    font-family: var(--font-display);
}

.content-area {
    padding: 60px;
    display: flex; 
    flex-direction: column; 
    justify-content: center;
    border-left: 1px solid #222;
    position: relative;
}

.floating-tag {
    position: absolute; 
    padding: 10px 20px; 
    border: 1px solid var(--accent-acid);
    color: var(--accent-acid); 
    font-family: var(--font-display); 
    font-size: 0.8rem;
    transform: rotate(-90deg); 
    left: -30px; 
    top: 100px;
}

.big-title { 
    font-size: 4rem; 
    line-height: 0.9; 
    margin-bottom: 20px; 
    font-family: var(--font-display); 
}

.meta-data { 
    font-family: 'Courier New', monospace; 
    color: #888; 
    margin-bottom: 40px; 
    border-top: 1px solid #333; 
    border-bottom: 1px solid #333; 
    padding: 20px 0;
}

.description {
    line-height: 1.8; 
    font-size: 1.1rem; 
    margin-bottom: 40px;
}

.review-glitch {
    background: #111; 
    padding: 20px; 
    margin-top: 20px;
    border-left: 3px solid var(--accent-acid);
}
</style>

