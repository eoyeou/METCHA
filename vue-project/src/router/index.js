import { createRouter, createWebHistory } from 'vue-router'
import MovieDetailView from '../views/MovieDetailView.vue'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import ProfileView from '../views/ProfileView.vue'
import ReviewCreateView from '../views/ReviewCreateView.vue'
import SearchResultsView from '../views/SearchResultsView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/movies/:id',
      name: 'movieDetail',
      component: MovieDetailView
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView
    },
    {
      path: '/profile',
      name: 'profile',
      component: ProfileView
    },
    {
      path: '/reviews/create',
      name: 'reviewCreate',
      component: ReviewCreateView
    },
    {
      path: '/search',
      name: 'searchResults',
      component: SearchResultsView
    }
  ]
})

export default router
