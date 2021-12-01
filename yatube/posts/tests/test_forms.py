import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import get_object_or_404
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import PostForm
from ..models import Comment, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class CreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Leo_test')
        cls.group = Group.objects.create(
            title='test_title',
            slug='test_group',
            description='test_description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=CreateFormTests.group,
            text="Test_text",
        )
        cls.form = PostForm()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(CreateFormTests.user)
        self.new_text = 'Тест титульника'
        self.update_text = 'Обновленная'
        self.new_comment = 'Невозможно, но факт!'

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        """Тестируем создание поста через форму"""
        post_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'group': CreateFormTests.group.id,
            'text': self.new_text,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': CreateFormTests.post.author})
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        new_post = Post.objects.latest('pub_date')
        self.assertEqual(new_post.text, self.new_text)
        self.assertEqual(new_post.group, CreateFormTests.group)
        self.assertEqual(new_post.author, CreateFormTests.user)
        self.assertTrue(new_post.image, uploaded)

    def test_edit_post(self):
        """Тестируем корректировку поста через форму."""
        form_data = {
            'group': CreateFormTests.group.id,
            'text': self.update_text,
        }
        response = self.authorized_client.post(reverse(
            'posts:post_edit',
            kwargs={'post_id': self.post.id}),
            data=form_data, follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': self.post.id})
        )
        upd_post = get_object_or_404(Post, id=self.post.id)
        self.assertEqual(upd_post.text, self.update_text)
        self.assertEqual(upd_post.group, CreateFormTests.group)
        self.assertEqual(upd_post.author, CreateFormTests.user)

    def test_create_post_non_auth(self):
        """Тестируем создание поста анонимом."""
        post_count = Post.objects.count()
        form_data = {
            'group': CreateFormTests.group.id,
            'text': self.new_text,
        }
        response = self.client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, (
            reverse('users:login') + '?next=' + reverse(
                'posts:post_create'
            )))
        self.assertEqual(Post.objects.count(), post_count)

    def test_edit_post_non_auth(self):
        """Тестируем корректировку поста анонимом."""
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'image': uploaded,
            'text': self.update_text,
        }
        response = self.client.post(reverse(
            'posts:post_edit',
            kwargs={'post_id': CreateFormTests.post.id}),
            data=form_data, follow=True
        )
        upd_post = get_object_or_404(Post, id=self.post.id)
        self.assertNotEqual(upd_post.text, self.update_text)
        self.assertNotEqual(upd_post.image, uploaded)

        self.assertRedirects(response, (
            reverse(
                'users:login') + '?next=' + reverse(
                    'posts:post_edit', kwargs={'post_id': self.post.id}
            )))

    def test_comment_create_auth_user(self):
        """
        Проверяем что комментарий возможно создать
        авторизованному пользователю.
        """
        count_posts_comments = Comment.objects.count()
        form_data = {
            'text': self.new_comment,
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', args=[self.post.id]),
            data=form_data,
            follow=True,
        )
        count_comments_after_request = Comment.objects.count()
        create_comment = Comment.objects.first()
        self.assertEqual(
            count_comments_after_request,
            count_posts_comments + 1
        )
        self.assertEqual(create_comment.text, self.new_comment)
        self.assertEqual(create_comment.author, self.user)
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )

    def test_comment_create_non_auth(self):
        """
        Проверяем что аноним не может комментрировать посты.
        """
        count_posts_comments = Comment.objects.count()
        form_data = {
            'text': self.new_comment,
        }
        self.client.post(
            reverse('posts:add_comment', args=[self.post.id]),
            data=form_data,
            follow=True,
        )
        count_comments_after_request = Comment.objects.count()
        self.assertNotEqual(
            count_comments_after_request,
            count_posts_comments + 1
        )
