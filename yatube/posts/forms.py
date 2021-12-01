from django.forms import ModelForm

from .models import Comment, Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['text', 'group', 'image']
        labes = {
            'text': 'text',
            'group': 'group',
        }
        help_texts = {
            'text': 'Текст нового поста',
            'group': 'Группа к которой относится запись'
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['post', 'author', 'text']
