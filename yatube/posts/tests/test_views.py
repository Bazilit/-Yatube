from http import HTTPStatus

from django import forms
from django.conf import settings as st
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from ..models import Group, Post, User


class PostsVievTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Leo_test')
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.group = Group.objects.create(
            title='test_title',
            slug='test_group',
            description='test_description',
        )
        for i in range(15):
            cls.post = Post.objects.create(
                author=cls.user,
                group=PostsVievTests.group,
                text="Test_text",
                image=uploaded
            )
        cls.count_user_posts = Post.objects.filter(author=cls.user).count()
        cls.last_count_pages = Post.objects.all().count() % st.PАGES

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsVievTests.user)
        self.home_url = 'posts/index.html'
        self.author_url = 'about/author.html'
        self.tech_url = 'about/tech.html'
        self.group_url = 'posts/group_list.html'
        self.profile_url = 'posts/profile.html'
        self.post_detail_url = 'posts/post_detail.html'
        self.create_url = 'posts/create_post.html'

    def get_objects_params(self, response, dict, pk=None):
        if pk is None:
            first_object = response.context[dict]
        else:
            first_object = response.context[dict][pk]
        if self.post.id is not None:
            self.assertEqual(
                self.post.id,
                PostsVievTests.post.id,
                'id постов не совпадают.'
            )
        if first_object.author.username is not None:
            self.assertEqual(
                first_object.author.username,
                PostsVievTests.post.author.username,
                'Авторы не совпадают.'
            )
        if first_object.pub_date.date() is not None:
            self.assertEqual(
                first_object.pub_date.date(),
                timezone.now().date(),
                'Дата не совпадает.'
            )
        if first_object.text is not None:
            self.assertEqual(
                first_object.text,
                PostsVievTests.post.text,
                'Текст постов не совпадает.'
            )
        if first_object.group.title is not None:
            self.assertEqual(
                first_object.group.title,
                PostsVievTests.group.title,
                'Заголовкок не совпадает.'
            )
        if first_object.group.slug is not None:
            self.assertEqual(
                first_object.group.slug,
                PostsVievTests.group.slug,
                'slug группы не совпадают.'
            )
        if first_object.group.description is not None:
            self.assertEqual(
                first_object.group.description,
                PostsVievTests.group.description,
                'Описание группы не совпадает.'
            )
        if first_object.image is not None:
            self.assertEqual(
                first_object.image,
                PostsVievTests.post.image,
                'Изображение не передается.'
            )

    def test_pages_uses_correct_template(self):
        """
        Проверяем, что view функции используют корректные
        запросы и статус подключения 200
        """
        templates_pages_names = {
            f'{self.home_url}': reverse('posts:index'),
            f'{self.group_url}': reverse(
                'posts:group_list',
                kwargs={'slug': PostsVievTests.group.slug}
            ),
            f'{self.profile_url}': reverse(
                'posts:profile',
                kwargs={'username': PostsVievTests.user}
            ),
            f'{self.post_detail_url}': reverse(
                'posts:post_detail',
                kwargs={'post_id': PostsVievTests.post.id}
            ),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

    def test_create_page_correct_template(self):
        """Проверка корректности подключения view функции create post"""
        response = self.authorized_client.get(reverse('posts:post_create'))
        template = f'{self.create_url}'
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, template)

    def test_edit_page_correct_template(self):
        """Проверка корректности подключения view функции edit post"""
        response = self.authorized_client.get(reverse(
            'posts:post_edit',
            kwargs={'post_id': PostsVievTests.post.id})
        )
        template = f'{self.create_url}'
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, template)

    def test_home_page_get_correct_context(self):
        """
        Проверяем корректность отображения
        содержимого на главной странице.
        """
        response = self.authorized_client.post(reverse('posts:index'))
        PostsVievTests.get_objects_params(
            self, response, 'page_obj', 0
        )

    def test_group_list_page_get_correct_context(self):
        """
        Проверяем корректность отображения
        содержимого на странице группы.
        """
        response = self.authorized_client.post(reverse(
            'posts:group_list',
            kwargs={'slug': PostsVievTests.group.slug})
        )
        PostsVievTests.get_objects_params(
            self, response, 'page_obj', 0
        )

    def test_profile_page_get_correct_context(self):
        """
        Проверяем корректность отображения
        содержимого на странице пользователя.
        """
        response = self.authorized_client.post(reverse(
            'posts:profile',
            kwargs={'username': PostsVievTests.post.author.username})
        )
        post_count_obj = response.context['post_count']
        PostsVievTests.get_objects_params(
            self, response, 'page_obj', 0
        )
        self.assertEqual(post_count_obj, PostsVievTests.count_user_posts)

    def test_post_detail_page_get_correct_context(self):
        """
        Проверяем корректность отображения
        содержимого на странице выбранного поста.
        """
        response = self.authorized_client.post(reverse(
            'posts:post_detail',
            kwargs={'post_id': PostsVievTests.post.id})
        )
        post_count_obj = response.context['count']
        PostsVievTests.get_objects_params(
            self, response, 'post'
        )
        self.assertEqual(post_count_obj, PostsVievTests.count_user_posts)

    def test_create_post_page_get_correct_context(self):
        """
        Проверяем корректность отображения
        содержимого на странице создания поста.
        """
        response = self.authorized_client.post(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_post_page_get_correct_context(self):
        """
        Проверяем корректность отображения
        содержимого на странице создания поста.
        """
        response = self.authorized_client.post(reverse(
            'posts:post_edit',
            kwargs={'post_id': PostsVievTests.post.id})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_create_post_correct(self):
        """
        Проверка создания поста с указанием группы.
        Его корректность отображения на главной странице,
        страницы группы, профайле пользователя.
        Проверка на отсутствие ошибки отнесения не к той группе.
        """
        user_max = User.objects.create_user(username='Max_test')
        self.authorized_client = Client()
        self.authorized_client.force_login(user_max)
        group = Group.objects.create(
            title='test_title',
            slug='Admin_group',
            description='test_description',
        )
        post = Post.objects.create(
            author=user_max,
            group=group,
            text="Next_test_text",
        )
        response = self.authorized_client.post(reverse('posts:index'))
        new_context_1 = response.context['page_obj'][0]
        self.assertEqual(self.post.id, PostsVievTests.post.id)
        self.assertEqual(new_context_1.author.username, post.author.username)
        self.assertEqual(new_context_1.text, post.text)
        self.assertEqual(new_context_1.group.slug, group.slug)
        response = self.authorized_client.post(reverse(
            'posts:group_list',
            kwargs={'slug': group.slug})
        )
        new_context_2 = response.context['page_obj'][0]
        self.assertEqual(self.post.id, PostsVievTests.post.id)
        self.assertEqual(new_context_2.author.username, post.author.username)
        self.assertEqual(new_context_2.text, post.text)
        self.assertEqual(new_context_2.group.slug, group.slug)
        response = self.authorized_client.post(reverse(
            'posts:profile',
            kwargs={'username': post.author.username})
        )
        new_context_3 = response.context['page_obj'][0]
        self.assertEqual(self.post.id, PostsVievTests.post.id)
        self.assertEqual(new_context_3.author.username, post.author.username)
        self.assertEqual(new_context_3.group.slug, group.slug)

    def test_paginator(self):
        """Проверяем корректность работы Паджинатора."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), st.PАGES)
        response = self.authorized_client.get(reverse(
            'posts:index') + '?page=2'
        )
        self.assertEqual(len(
            response.context['page_obj']),
            PostsVievTests.last_count_pages
        )
        response = self.authorized_client.post(reverse(
            'posts:group_list',
            kwargs={'slug': PostsVievTests.group.slug})
        )
        self.assertEqual(len(response.context['page_obj']), st.PАGES)
        response = self.authorized_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': PostsVievTests.group.slug}) + '?page=2'
        )
        self.assertEqual(len(
            response.context['page_obj']),
            PostsVievTests.last_count_pages
        )
        response = self.authorized_client.post(reverse(
            'posts:profile',
            kwargs={'username': PostsVievTests.post.author.username})
        )
        self.assertEqual(len(response.context['page_obj']), st.PАGES)
        response = self.authorized_client.post(reverse(
            'posts:profile',
            kwargs={'username': PostsVievTests.post.author.username})
            + '?page=2'
        )
        self.assertEqual(len(
            response.context['page_obj']),
            PostsVievTests.last_count_pages
        )

    def test_cache_correct_worked(self):
        response = self.authorized_client.get(reverse('posts:index'))
        content_before_deletion = response.content
        Post.objects.all().delete()
        response = self.authorized_client.get(reverse('posts:index'))
        content_after_deletion = response.content
        self.assertEqual(
            content_before_deletion,
            content_after_deletion,
            'Кэширование не работает.'
        )
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(
            content_before_deletion,
            response.content,
            'Кэширование после очистки не работает.'
        )
