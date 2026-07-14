import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/board',
      name: 'boardList',
      component: () => import('../views/BoardListView.vue'),
    },
    {
      path: '/board/:id',
      name: 'boardDetail',
      component: () => import('../views/BoardDetailView.vue'),
    },
    {
      path: '/upload-board',
      name: 'uploadBoard',
      component: () => import('../views/UploadBoardView.vue'),
    },
    {
      path: '/calendar',
      name: 'calendar',
      component: () => import('../views/CalendarView.vue'),
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('../views/AboutView.vue'),
    },
  ],
})

export default router
