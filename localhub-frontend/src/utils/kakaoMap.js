let loadPromise = null

export function loadKakaoMaps() {
  if (loadPromise) return loadPromise

  loadPromise = new Promise((resolve, reject) => {
    if (window.kakao?.maps) {
      resolve(window.kakao)
      return
    }

    const appKey = import.meta.env.VITE_KAKAO_MAP_KEY
    if (!appKey) {
      reject(new Error('VITE_KAKAO_MAP_KEY가 설정되지 않았어요. .env를 확인해 주세요.'))
      return
    }

    const script = document.createElement('script')
    script.src = `https://dapi.kakao.com/v2/maps/sdk.js?appkey=${appKey}&autoload=false&libraries=clusterer`
    script.onerror = () => reject(new Error('카카오맵 SDK를 불러오지 못했어요.'))
    script.onload = () => {
      window.kakao.maps.load(() => resolve(window.kakao))
    }
    document.head.appendChild(script)
  })

  return loadPromise
}
