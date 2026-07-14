<script setup lang="ts">
import { ref } from 'vue'

interface Category {
  id: number
  name: string
}

interface ImageUpload {
  file: File | null
  preview: string | null
}

const categories: Category[] = [
  { id: 2, name: '관광지' },
  { id: 3, name: '레포츠' },
  { id: 4, name: '문화시설' },
  { id: 5, name: '쇼핑' },
  { id: 6, name: '숙박' },
  { id: 7, name: '여행코스' },
  { id: 8, name: '축제행사' }
]

const selectedCategories = ref<Set<number>>(new Set([2]))
const rating = ref(0)
const title = ref('')
const content = ref('')
const nickname = ref('')
const password = ref('')
const images = ref<ImageUpload[]>([
  { file: null, preview: null },
  { file: null, preview: null }
])

const toggleCategory = (categoryId: number) => {
  if (selectedCategories.value.has(categoryId)) {
    selectedCategories.value.delete(categoryId)
  } else {
    selectedCategories.value.add(categoryId)
  }
}

const isCategorySelected = (categoryId: number) => {
  return selectedCategories.value.has(categoryId)
}

const handleRating = (star: number) => {
  rating.value = star
}

const handleImageChange = (index: number, e: Event) => {
  const input = e.target as HTMLInputElement
  if (input.files?.[0]) {
    const file = input.files[0]
    const reader = new FileReader()
    reader.onload = (event) => {
      images.value[index] = {
        file: file,
        preview: event.target?.result as string
      }
    }
    reader.readAsDataURL(file)
  }
}

const handleCancel = () => {
  console.log('취소')
}

const handleSaveDraft = () => {
  console.log('임시저장')
}

const handleSubmit = () => {
  if (!title.value.trim() || !content.value.trim() || !nickname.value.trim() || !password.value.trim()) {
    alert('모든 필드를 입력해주세요.')
    return
  }
  console.log('게시글 작성:', {
    categories: Array.from(selectedCategories.value),
    rating: rating.value,
    title: title.value,
    content: content.value,
    nickname: nickname.value,
    password: password.value,
    images: images.value
  })
}
</script>

<template>
  <div class="upload-board-page">
    <div class="upload-header">
      <button class="header-close-btn" @click="handleCancel">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M18 6L6 18M6 6l12 12" />
        </svg>
      </button>
      <h1 class="header-title">글쓰기</h1>
      <button class="header-draft-btn" @click="handleSaveDraft">임시저장</button>
    </div>

    <div class="upload-content">
      <div class="content-wrapper">
        <div class="form-section">
          <label class="section-label">카테고리</label>
          <div class="category-buttons">
            <button
              v-for="category in categories"
              :key="category.id"
              :class="['category-btn', { active: isCategorySelected(category.id) }]"
              @click="toggleCategory(category.id)"
            >
              {{ category.name }}
            </button>
          </div>
        </div>

        <div class="form-section">
          <label class="section-label">평점</label>
          <div class="rating-section">
            <div class="stars">
              <button
                v-for="star in 5"
                :key="star"
                :class="['star-btn', { active: star <= rating }]"
                @click="handleRating(star)"
              >
                ★
              </button>
            </div>
            <span class="rating-hint">터치해서 선택</span>
          </div>
        </div>

        <div class="form-section">
          <input
            v-model="title"
            type="text"
            class="title-input"
            placeholder="제목"
            maxlength="100"
          />
        </div>

        <div class="form-section">
          <textarea
            v-model="content"
            class="content-input"
            placeholder="내용을 입력하세요..."
            maxlength="2000"
          ></textarea>
        </div>

        <div class="form-section">
          <label class="section-label">사진 첨부</label>
          <div class="image-grid">
            <div
              v-for="(image, index) in images"
              :key="index"
              class="image-upload-box"
            >
              <input
                type="file"
                accept="image/*"
                class="file-input"
                @change="(e) => handleImageChange(index, e)"
              />
              <div v-if="!image.preview" class="upload-placeholder">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M12 5v14M5 12h14" />
                </svg>
                <p>사진</p>
              </div>
              <img v-else :src="image.preview" alt="preview" class="image-preview" />
            </div>
          </div>
        </div>

        <div class="form-section">
          <input
            v-model="nickname"
            type="text"
            class="input-field"
            placeholder="닉네임"
          />
        </div>

        <div class="form-section password-section">
          <input
            v-model="password"
            type="password"
            class="input-field"
            placeholder="비밀번호 ••••"
          />
          <p class="password-hint">* 비밀번호는 수정/삭제 시 필요해요</p>
        </div>

        <button class="submit-btn" @click="handleSubmit">등록하기</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.upload-board-page {
  width: 100%;
  min-height: 100vh;
  background-color: #ffffff;
  display: flex;
  flex-direction: column;
}

.upload-header {
  width: 100%;
  padding: 16px 20px;
  background-color: #ffffff;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.header-close-btn {
  width: 32px;
  height: 32px;
  min-width: 32px;
  border: none;
  background-color: transparent;
  color: #333;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s;
  padding: 0;
}

.header-close-btn:hover {
  color: #666;
}

.header-close-btn svg {
  width: 24px;
  height: 24px;
}

.header-title {
  flex: 1;
  text-align: center;
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.header-draft-btn {
  border: none;
  background-color: transparent;
  color: #666;
  font-size: 13px;
  cursor: pointer;
  padding: 0;
  transition: color 0.2s;
}

.header-draft-btn:hover {
  color: #333;
}

.upload-content {
  flex: 1;
  padding: 20px;
  background-color: #ffffff;
  overflow-y: auto;
}

.content-wrapper {
  max-width: 800px;
  margin: 0 auto;
}

.form-section {
  margin-bottom: 20px;
}

.section-label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #333;
  margin-bottom: 10px;
}

.category-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.category-btn {
  padding: 8px 16px;
  border: 2px solid #e5e7eb;
  border-radius: 20px;
  background-color: #ffffff;
  color: #333;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.category-btn:hover {
  border-color: #333;
}

.category-btn.active {
  background-color: #333;
  color: #ffffff;
  border-color: #333;
}

.rating-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.stars {
  display: flex;
  gap: 4px;
}

.star-btn {
  background-color: transparent;
  border: none;
  font-size: 32px;
  cursor: pointer;
  padding: 0;
  color: #e5e7eb;
  transition: color 0.2s;
}

.star-btn.active {
  color: #ffc107;
}

.rating-hint {
  font-size: 12px;
  color: #999;
}

.title-input {
  width: 100%;
  padding: 14px 16px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  background-color: #ffffff;
  color: #333;
  font-size: 14px;
  font-family: inherit;
  transition: border-color 0.2s;
}

.title-input:focus {
  outline: none;
  border-color: #333;
}

.title-input::placeholder {
  color: #999;
}

.content-input {
  width: 100%;
  padding: 14px 16px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  background-color: #ffffff;
  color: #333;
  font-size: 14px;
  font-family: inherit;
  resize: vertical;
  min-height: 150px;
  transition: border-color 0.2s;
}

.content-input:focus {
  outline: none;
  border-color: #333;
}

.content-input::placeholder {
  color: #999;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 6px;
}

.image-upload-box {
  position: relative;
  aspect-ratio: 4 / 3;
  max-height: 100px;
  border: 2px dashed #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
  background-color: #fafafa;
  transition: border-color 0.2s;
}

.image-upload-box:hover {
  border-color: #333;
}

.file-input {
  position: absolute;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
  z-index: 2;
}

.upload-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #999;
}

.upload-placeholder svg {
  width: 32px;
  height: 32px;
  opacity: 0.5;
}

.upload-placeholder p {
  font-size: 12px;
  margin: 0;
}

.image-preview {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.input-field {
  width: 100%;
  padding: 14px 16px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  background-color: #ffffff;
  color: #333;
  font-size: 14px;
  font-family: inherit;
  transition: border-color 0.2s;
}

.input-field:focus {
  outline: none;
  border-color: #333;
}

.input-field::placeholder {
  color: #999;
}

.password-section {
  margin-bottom: 32px;
}

.password-hint {
  font-size: 12px;
  color: #999;
  margin-top: 6px;
  margin-bottom: 0;
}

.submit-btn {
  width: 100%;
  padding: 16px;
  background-color: #333;
  color: #ffffff;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.submit-btn:hover {
  background-color: #555;
}

@media (max-width: 768px) {
  .upload-header {
    padding: 14px 16px;
  }

  .upload-content {
    padding: 16px;
  }

  .header-title {
    font-size: 16px;
  }
}

@media (max-width: 640px) {
  .upload-header {
    padding: 12px 16px;
    gap: 8px;
  }

  .upload-content {
    padding: 16px 12px;
  }

  .header-title {
    font-size: 16px;
  }

  .header-draft-btn {
    font-size: 12px;
  }

  .section-label {
    font-size: 12px;
  }

  .category-btn {
    padding: 6px 12px;
    font-size: 12px;
  }

  .title-input,
  .content-input,
  .input-field {
    font-size: 14px;
    padding: 12px 14px;
  }

  .content-input {
    min-height: 120px;
  }

  .star-btn {
    font-size: 28px;
  }

  .submit-btn {
    padding: 14px;
    font-size: 15px;
  }
}
</style>
