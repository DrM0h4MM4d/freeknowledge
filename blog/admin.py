from django.contrib.admin.options import ModelAdmin
from .models import (
    Article,
    Category,
    Comment,
    Likes,
    ViewsMid,
)
from django.contrib import admin


# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = [
            # 'parent__title',
            'get_parents',
            'title',
            'slug',
            'desc',
    ]
    prepopulated_fields = {'slug': ('title',)}
    list_filter = [
            'parent',
            'title',
            'slug',
            'desc',
    ]


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'slug',
        'text',
        'date_cr',
        'date_up',
        'published',
        'get_author',
        'get_categories',
        'image_tag',
    ]
    prepopulated_fields = {'slug': ('title',)}
    list_filter = [
        'title',
        'slug',
        'text',
        'date_cr',
        'date_up',
        'published',
    ]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = [
            'to_article',
            'title',
            'text',
            'date_cr',
    ]
    list_filter = [
            'to_article',
            'title',
            'text',
            'date_cr',
    ]


@admin.register(Likes)
class LikesAdmin(ModelAdmin):
    list_display = [
        'post',
    ]


admin.site.register(ViewsMid)
