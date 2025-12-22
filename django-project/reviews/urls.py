from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('reviews/', views.review_create),
    path('reviews/<int:review_pk>/', views.review_update_or_delete),
    path('reviews/<int:review_pk>/like/', views.review_like),
]