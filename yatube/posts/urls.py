from django.urls import path

from . import views

urlpatterns = [
    path('new/',
         views.new_post, name='new_post'),
    path('<str:username>/',
         views.profile, name='profile'),
    path('<str:username>/<int:post_id>/',
         views.post_view, name='post'),
    path('<str:username>/<int:post_id>/comment',
         views.add_comment, name='comment'),
    path('<str:username>/<int:post_id>/edit/',
         views.edit_post, name='edit_post'),
    path('group/<slug:slug>/',
         views.group_posts, name='group'),
    path('',
         views.index, name='index'),
]
