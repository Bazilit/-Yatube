from django.contrib.auth import get_user_model
from django.db import models


class Group(models.Model):
    title = models.CharField(
        verbose_name='Заголовок',
        max_length=200, help_text='Кратко опишите заголовок'
    )
    slug = models.SlugField(
        verbose_name='Адрес для страницы с задачей',
        max_length=200, unique=True,
        help_text='Укажите адрес для страницы задачи'
    )
    description = models.TextField(
        verbose_name='Описание группы',
        null=True, blank=True,
        help_text='Краткое описание группы'
    )

    def __str__(self):
        return self.title


User = get_user_model()


class Post(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    group = models.ForeignKey(
        Group,
        blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name='posts'
    )
    text = models.TextField(verbose_name='Текст', help_text='Напишите статью')
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='posts/',
        blank=True,
    )
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        verbose_name='Комментируемый пост.',
        blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        blank=True, null=True,
        verbose_name='Автор комментария.',
        on_delete=models.CASCADE,
        related_name='comments',
    )
    text = models.TextField(
        verbose_name='Текст комментария.',
        max_length=2000,
        help_text='Введите текст комментария.'
    )
    created = models.DateTimeField(auto_now_add=True)


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
        related_name='follower',
        blank=True, null=True,
    )
    author = models.ForeignKey(
        User,
        verbose_name='На кого подписываются',
        on_delete=models.CASCADE,
        related_name='following',
        blank=True, null=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_follow')
        ]
