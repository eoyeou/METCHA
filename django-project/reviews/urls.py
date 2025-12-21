from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('reviews/', views.review_create),
    path('reviews/<int:review_pk>/', views.review_update),
    path('reviews/<int:review_pk>/', views.review_delete),
]