from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

from .models import Category, Post, Location, User

admin.site.empty_value_display = 'Не задано'


class PostInline(admin.StackedInline):
    model = Post
    extra = 0


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    inlines = (
        PostInline,
    )


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'pub_date',
        'is_published',
        'author',
        'location',
        'category',
        'comments_count',
    )
    list_editable = (
        'is_published',
        'category',
        'location'
    )
    search_fields = ('title',)
    list_filter = ('is_published',)

    @admin.display(description='Комментарии')
    def comments_count(self, obj):
        return obj.comments.count()


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    inlines = (
        PostInline,
    )


admin.site.unregister(User)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'is_staff',
        'posts_count'
    )

    @admin.display(description='Кол-во постов пользователя')
    def posts_count(self, obj):
        return obj.posts.count()


admin.site.unregister(Group)
admin.site.site_title = 'Администрирование Блогикум'
admin.site.site_header = 'Администрирование Блогикум'
