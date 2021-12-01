from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая группа',
        )

    def setUp(self):
        self.title_help_texts = 'Кратко опишите заголовок'
        self.slug_help_texts = 'Укажите адрес для страницы задачи'
        self.description_help_texts = 'Краткое описание группы'
        self.title_verboses = 'Заголовок'
        self.slug_verboses = 'Адрес для страницы с задачей'
        self.description_verboses = 'Описание группы'
        self.text_verboses = 'Текст'
        self.text_help_texts = 'Напишите статью'

    def test_post_models_have_correct_object_names(self):
        """Проверяем, что у модели post корректно работает __str__."""
        post = PostModelTest.post
        expected_object_name = post.text[:15]
        self.assertEqual(expected_object_name, str(post))

    def test_group_models_have_correct_object_names(self):
        """Проверяем, что у модели group корректно работает __str__."""
        group = PostModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))

    def test_post_text_verbose_name_help_text(self):
        """Проверяем, verbose_name и help_text поля text модели Post."""
        verbose = Post._meta.get_field('text').verbose_name
        help_text = Post._meta.get_field('text').help_text
        self.assertEqual(verbose, self.text_verboses)
        self.assertEqual(help_text, self.text_help_texts)

    def test_post_text_verbose_name_help_text(self):
        """Проверяем, verbose_name и help_text модели Group."""
        group = PostModelTest.group
        field_help_texts = {
            'title': self.title_help_texts,
            'slug': self.slug_help_texts,
            'description': self.description_help_texts
        }
        field_verboses = {
            'title': self.title_verboses,
            'slug': self.slug_verboses,
            'description': self.description_verboses,
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).help_text, expected_value)
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name, expected_value)
