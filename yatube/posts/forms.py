from django import forms
from django.forms import Textarea

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        verbose_name_plural = ('текст', 'группа', 'изображение')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        verbose_name_plural = ('текст',)
        widgets = {
            'text': Textarea(attrs={'class': 'form-control'})
        }
