from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestListPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Пупсень')
        cls.note = Note.objects.create(
            title='Название ноты',
            text='Текст ноты',
            slug='testNote_one',
            author=cls.author
        )
        cls.note_two = Note.objects.create(
            title='Название ноты',
            text='Текст ноты',
            slug='testNote_two',
            author=cls.author
        )
        cls.reader = User.objects.create(username='Reader')
        cls.reader_note = Note.objects.create(
            title='Название ноты',
            text='Текст ноты',
            slug='testNote_free',
            author=cls.reader
        )

    def test_notes_list_for_author(self):
        self.client.force_login(self.author)
        url = reverse('notes:list')
        response = self.client.get(url)
        self.assertIn('object_list', response.context)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)
        self.assertIn(self.note_two, object_list)
        # Проверяем, что чужая заметка не попала в список
        self.assertNotIn(self.reader_note, object_list)


class TestNoteForms(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Пупсень')
        cls.note = Note.objects.create(
            title='Название ноты',
            text='Текст ноты',
            slug='testNote_one',
            author=cls.author
        )
        cls.reader = User.objects.create(username='Reader')

    def test_add_page_contains_form(self):
        self.client.force_login(self.author)
        url = reverse('notes:add')
        response = self.client.get(url)
        self.assertIn('form', response.context)

    def test_edit_page_contains_form(self):
        self.client.force_login(self.author)
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.client.get(url)
        self.assertIn('form', response.context)

    def test_edit_page_not_available_for_other_user(self):
        self.client.force_login(self.reader)
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
