from django.contrib import admin
from .models import Review, ReviewEmbedding

admin.site.register(Review)
admin.site.register(ReviewEmbedding)