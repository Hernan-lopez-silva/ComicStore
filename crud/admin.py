from django.contrib import admin
from .models import Comic


@admin.register(Comic)
class ComicAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'price')
    search_fields = ('title', 'description')
    list_filter = ('price',)