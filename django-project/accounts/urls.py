# accounts/urls.py
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('preferences/', views.set_preferences, name='set-preferences'),
    path('profile/', views.profile_detail, name='profile-detail'),
    path('profile/<int:user_id>/', views.profile_detail, name='profile-detail'),
    path('profile/reviews/', views.profile_reviews, name='profile-reviews'),
    path('profile/reviews/<int:user_id>/', views.profile_reviews, name='profile-reviews'),
    path('profile/preference-report/', views.preference_report, name='preference-report'),
    path('profile/preference-report/<int:user_id>/', views.preference_report, name='preference-report'),
    path('users/<int:user_id>/follow/', views.follow_user, name='follow-user'),
    path('users/<int:user_id>/followers/', views.followers_list, name='followers-list'),
    path('users/<int:user_id>/following/', views.following_list, name='following-list'),
]