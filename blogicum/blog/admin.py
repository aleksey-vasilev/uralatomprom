from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe

from .models import Category, Post, User

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
        'post_image',
        'title',
        'pub_date',
        'is_published',
        'author',
        'category',
        'comments_count',
    )
    list_editable = (
        'is_published',
        'category',
    )
    search_fields = ('title',)
    list_filter = ('is_published',)

    @admin.display(description='Комментарии')
    def comments_count(self, obj):
        return obj.comments.count()

    @admin.display(description='Картинка')
    def post_image(self, obj):
        return mark_safe(f'<img src={obj.image.url} width="80" height="60">'
                         ) if (obj.image) else None


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'is_speaker',
                    'full_name', 'organisation',
                    'phone', 'email',
                    'abstract',)


admin.site.unregister(Group)
admin.site.site_title = 'Администрирование Блогикум'
admin.site.site_header = 'Администрирование Блогикум'
