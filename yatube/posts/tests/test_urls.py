from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая группа',
        )

    def setUp(self):
        self.user = User.objects.create_user(username='leo')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.home_url = 'posts/index.html'
        self.author_url = 'about/author.html'
        self.tech_url = 'about/tech.html'
        self.group_url = 'posts/group_list.html'
        self.profile_url = 'posts/profile.html'
        self.post_detail_url = 'posts/post_detail.html'

    def test_non_auth_users_correct_template(self):
        """
        URL-адрес использует соответствующий шаблон.
        Пользователь неавторизован.
        """
        templates_url_names = {
            f'{self.home_url}': reverse('posts:index'),
            f'{self.author_url}': reverse('about:author'),
            f'{self.tech_url}': reverse('about:tech'),
            f'{self.group_url}': reverse(
                'posts:group_list',
                kwargs={'slug': PostModelTest.group.slug}
            ),
            f'{self.profile_url}': reverse(
                'posts:profile',
                kwargs={'username': self.user}
            ),
            f'{self.post_detail_url}': reverse(
                'posts:post_detail',
                kwargs={'post_id': PostModelTest.post.id}
            ),
        }
        for template, adress in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_auth_users_correct_template(self):
        """
        URL-адрес использует соответствующий шаблон.
        Пользователь авторизован.
        """
        templates_url_names = {
            f'{self.home_url}': reverse('posts:index'),
            f'{self.author_url}': reverse('about:author'),
            f'{self.tech_url}': reverse('about:tech'),
            f'{self.group_url}': reverse(
                'posts:group_list',
                kwargs={'slug': PostModelTest.group.slug}
            ),
            f'{self.profile_url}': reverse(
                'posts:profile',
                kwargs={'username': self.user}
            ),
            f'{self.post_detail_url}': reverse(
                'posts:post_detail',
                kwargs={'post_id': PostModelTest.post.id}
            ),
        }
        for template, adress in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_urls_app_users(self):
        """Проверяем доступность URL приложения users"""
        url_names = {
            reverse('users:login'): HTTPStatus.OK,
            reverse('users:signup'): HTTPStatus.OK,
            reverse('users:logout'): HTTPStatus.OK,
            reverse('users:password_change'): HTTPStatus.FOUND,
            reverse('users:password_reset'): HTTPStatus.OK,
            reverse('users:password_change_done'): HTTPStatus.FOUND,
            reverse(
                'users:password_reset_confirm',
                kwargs={'uidb64': 'uidb', 'token': 'token'}
            ): HTTPStatus.OK,
            reverse('users:password_reset_done'): HTTPStatus.OK,
        }
        for url, expected_value in url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, expected_value)

    def test_urls_app_about(self):
        """Проверяем доступность URL приложения about"""
        url_names = {
            reverse('about:author'): HTTPStatus.OK,
            reverse('about:tech'): HTTPStatus.OK,
        }
        for url, expected_value in url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, expected_value)

    def test_urls_app_posts(self):
        """Проверяем доступность URL приложения posts"""
        url_names = {
            reverse('posts:index'): HTTPStatus.OK,
            reverse(
                'posts:group_list',
                kwargs={'slug': PostModelTest.group.slug}
            ): HTTPStatus.OK,
            reverse(
                'posts:profile',
                kwargs={'username': self.user}
            ): HTTPStatus.OK,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostModelTest.post.id}
            ): HTTPStatus.OK,
            reverse('posts:post_create'): HTTPStatus.OK,
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostModelTest.post.id}
            ): HTTPStatus.OK,
            reverse(
                'posts:post_delete',
                kwargs={'post_id': PostModelTest.post.id}
            ): HTTPStatus.OK,
        }
        for url, expected_value in url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, expected_value)
