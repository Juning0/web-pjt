const ADJECTIVES = [
  '멋진', '잘생긴', '유쾌한', '용감한', '느긋한', '상냥한',
  '엉뚱한', '씩씩한', '수줍은', '똑똑한', '든든한', '발랄한',
]

const NOUNS = [
  '수박', '당근', '호랑이', '고양이', '너구리', '펭귄',
  '감자', '고래', '다람쥐', '토끼', '올빼미', '수달',
]

export function randomNickname() {
  const adjective = ADJECTIVES[Math.floor(Math.random() * ADJECTIVES.length)]
  const noun = NOUNS[Math.floor(Math.random() * NOUNS.length)]
  return `${adjective} ${noun}`
}

const NICKNAME_PREFIX = /^\[(.+?)\]\s*([\s\S]*)$/

// 백엔드 Post/Comment에는 nickname 필드가 없어 "[닉네임] 내용" 형태로 저장한다.
export function parseAuthoredContent(raw) {
  const match = NICKNAME_PREFIX.exec(raw || '')
  if (!match) return { nickname: '익명', body: raw || '' }
  return { nickname: match[1], body: match[2] }
}
