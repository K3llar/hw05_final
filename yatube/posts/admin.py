from django.contrib import admin

from .models import Post, Group

empty_value = '-пусто-'


class SiteAdmin(admin.ModelAdmin):
    pass


@admin.register(Post)
class PostAdmin(SiteAdmin):
    list_display = ('pk', 'text', 'pub_date', 'author', 'group')
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = empty_value


@admin.register(Group)
class GroupAdmin(SiteAdmin):
    list_display = ('title', 'slug', 'description')
    search_fields = ('title',)
    empty_value_display = empty_value
