<script setup>
import { ref } from 'vue'
import ChatWidget from '@/components/ChatWidget.vue'

const toast = ref('')
let toastTimer

function showIntegrationEvent(source) {
  toast.value = `“${source.title}” 선택 이벤트가 전달되었습니다.`
  window.clearTimeout(toastTimer)
  toastTimer = window.setTimeout(() => {
    toast.value = ''
  }, 2800)
}
</script>

<template>
  <div class="site-shell">
    <header class="site-header">
      <a class="site-logo" href="#" aria-label="LocalHub 홈">
        <span class="logo-pin" aria-hidden="true"></span>
        <strong>LocalHub</strong>
      </a>
      <nav aria-label="주요 메뉴">
        <a href="#explore">둘러보기</a>
        <a href="#recommend">추천</a>
        <a href="#community">커뮤니티</a>
      </nav>
      <button type="button">로그인</button>
    </header>

    <main>
      <section id="explore" class="hero-section">
        <p class="eyebrow">대전·충청 여행을 한곳에서</p>
        <h1>오늘은 어디로<br />떠나볼까요?</h1>
        <p class="hero-copy">지역의 장소와 사람들의 생생한 후기를 함께 찾아보세요.</p>
        <form class="search-bar" @submit.prevent>
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <circle cx="11" cy="11" r="6.5" />
            <path d="m16 16 4 4" />
          </svg>
          <input aria-label="지역 또는 장소 검색" placeholder="지역 또는 장소를 검색해 보세요" />
          <button type="submit">검색</button>
        </form>
        <div class="category-chips" aria-label="장소 카테고리">
          <button type="button" class="active">전체</button>
          <button type="button">관광지</button>
          <button type="button">음식점</button>
          <button type="button">숙박</button>
          <button type="button">문화시설</button>
          <button type="button">축제·행사</button>
        </div>
      </section>

      <section id="recommend" class="content-section">
        <div class="section-heading">
          <div>
            <p class="eyebrow">LOCAL PICK</p>
            <h2>지금 둘러보기 좋은 장소</h2>
          </div>
          <button type="button">전체 보기 <span aria-hidden="true">→</span></button>
        </div>
        <div class="place-grid">
          <article v-for="card in 3" :key="card" class="place-card">
            <div :class="['place-image', `image-${card}`]">
              <span>{{ card === 1 ? '관광지' : card === 2 ? '음식점' : '문화시설' }}</span>
            </div>
            <div class="place-body">
              <h3>{{ ['대전의 새로운 발견', '현지인이 찾는 맛집', '주말 문화 산책'][card - 1] }}</h3>
              <p><span class="stars">★★★★★</span> 아직 등록된 리뷰가 없어요</p>
              <small>대전·충청권 지역 정보</small>
            </div>
          </article>
        </div>
      </section>

      <section id="community" class="community-banner">
        <div>
          <p class="eyebrow">COMMUNITY</p>
          <h2>직접 다녀온 이야기를 나눠보세요</h2>
          <p>여행 후기와 별점을 남기고, 다른 지역 주민의 추천도 확인할 수 있어요.</p>
        </div>
        <button type="button">커뮤니티 둘러보기</button>
      </section>
    </main>

    <Transition name="toast">
      <p v-if="toast" class="event-toast" role="status">{{ toast }}</p>
    </Transition>

    <ChatWidget
      @select-location="showIntegrationEvent"
      @select-post="showIntegrationEvent"
    />
  </div>
</template>
