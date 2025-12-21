from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('movies.urls')),
    path('api/', include('reviews.urls')),
    path('api/accounts/', include('dj_rest_auth.urls')),  # 로그인/로그아웃
    path('api/accounts/', include('accounts.urls')),  # 회원가입
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
