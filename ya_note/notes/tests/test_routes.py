from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.note = Note.objects.create(
            title='Заметка тестовая',
            text='Тестовый текст заметки',
            slug='testsnote',
            author=cls.author
        )

    def test_pages_availability(self):
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:signup', None),
        )

        for item in urls:
            name, key = item
            with self.subTest(name=name):
                url = reverse(name, args=key)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    # С более новой версии джанги в логауте применяют post запрос
    # потому проверяю отдельно
    def test_logout_anonymous(self):
        url = reverse('users:logout')
        response = self.client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_edit_and_delete(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )

        urlses = (
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
        )

        for item in users_statuses:
            user, statues = item
            self.client.force_login(user)
            for name, key in urlses:
                with self.subTest(name=name, user=user):
                    url = reverse(name, args=key)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, statues)

    def test_note_add_availability(self):
        self.client.force_login(self.author)
        url = reverse('notes:add')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # переодресация для анонима
        self.client.logout()
        login_url = reverse('users:login')
        url_add = reverse('notes:add')
        redirect_url = f'{login_url}?next={url_add}'
        response = self.client.get(url_add)
        self.assertRedirects(response, redirect_url)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        urlses = (
            ('notes:edit'),
            ('notes:delete'),
        )

        for name in urlses:
            with self.subTest(name=name):
                url = reverse(name, args=(self.note.slug,))
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_detail_note_for_author(self):
        self.client.force_login(self.author)
        url = reverse('notes:detail', args=(self.note.slug,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # для анонима
        self.client.force_login(self.reader)
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_note_list(self):
        self.client.force_login(self.author)
        url = reverse('notes:list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        self.client.logout()
        login_url = reverse('users:login')
        redirect_url = f'{login_url}?next={url}'
        response = self.client.get(url)
        self.assertRedirects(response, redirect_url)
