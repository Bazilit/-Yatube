from http import HTTPStatus

from django.test import TestCase


class ViewTestClass(TestCase):
    def setUp(self):
        self.error_response = '/nonexist-page/'
        self.not_found_html = 'core/404.html'

    def test_404_error(self):
        """Проверка шаблона и корректности статуса для ошибки 404."""
        response = self.client.get(self.error_response)
        self.assertTemplateUsed(
            response, self.not_found_html,
            'Шаблон 404.html не найден.'
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
