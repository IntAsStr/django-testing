from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.models import Note

User = get_user_model()


class TestNoteEditDelete(TestCase):

    NOTE_TEXT = 'Текст комментария'
    NEW_NOTE_TEXT = 'Обновлённый комментарий'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')

        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text=cls.NOTE_TEXT,
            slug='test-note',
            author=cls.author
        )

        cls.detail_url = reverse('notes:detail', args=(cls.note.slug,))
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.list_url = reverse('notes:list')
        cls.login_url = reverse('users:login')
        cls.add_url = reverse('notes:add')

    def test_author_can_delete_note(self):
        self.client.force_login(self.author)
        response = self.client.post(self.delete_url)
        self.assertRedirects(response, reverse('notes:success'))
        note_count = Note.objects.count()
        self.assertEqual(note_count, 0)

    def test_reader_cannot_delete_note(self):
        self.client.force_login(self.reader)
        response = self.client.post(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_author_can_edit_comment(self):
        self.client.force_login(self.author)
        form_data = {
            'title': 'Обновлённый заголовок',
            'text': self.NEW_NOTE_TEXT,
            'slug': 'test-note'
        }
        response = self.client.post(self.edit_url, data=form_data)
        expected_url = reverse('notes:success')
        self.assertRedirects(response, expected_url)

    def test_reader_cannot_edit_note(self):
        self.client.force_login(self.reader)
        form_data = {
            'title': 'Обновлённый заголовок',
            'text': self.NEW_NOTE_TEXT,
            'slug': 'updated-note'
        }
        response = self.client.post(self.edit_url, data=form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_author_sees_only_own_notes(self):
        self.client.force_login(self.author)
        url = reverse('notes:list')
        response = self.client.get(url)
        notes_in_list = list(response.context['object_list'])
        self.assertEqual(len(notes_in_list), 1)
        self.assertEqual(notes_in_list[0].slug, self.note.slug)

    def test_authenticated_user_can_create_note(self):
        self.client.force_login(self.author)
        note_data = {
            'title': 'Новая заметка',
            'text': 'Текст новой заметки',
            'slug': 'new-note',
        }
        response = self.client.post(self.add_url, data=note_data)
        self.assertRedirects(response, reverse('notes:success'))

    def test_same_slug(self):
        self.client.force_login(self.author)
        note_data = {
            'title': 'Новая заметка',
            'text': 'Текст новой заметки',
            'slug': 'test-note',
        }
        response = self.client.post(self.add_url, data=note_data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(response.context['form'].errors)
        self.assertEqual(Note.objects.filter(slug='test-note').count(), 1)

    def test_auto_slug_generation(self):
        self.client.force_login(self.author)
        note_data = {
            'title': 'Новая заметка с интересным названием',
            'text': 'Текст заметки',
            # Поле slug отсутствует
        }
        response = self.client.post(self.add_url, data=note_data)
        self.assertRedirects(response, reverse('notes:success'))
        note = Note.objects.get(title='Новая заметка с интересным названием')
        self.assertTrue(note.slug)
        expected_slug = slugify(note_data['title'])
        self.assertEqual(note.slug, expected_slug)
