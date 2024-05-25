from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()

notes_on_list_page = 11


class TestListPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.other_author = User.objects.create(username='Читатель простой')
        cls.one_note = Note.objects.create(
            author=cls.author,
            title='Заголовок',
            text='Текст комментария',
            slug='note111',
        )
        # От имени одного пользователя создаём заметки:
        all_notes = [
            Note(
                author=cls.author,
                title=f'Заголовок {index}',
                text=f'Просто текст {index}',
                slug=f'note_{index}'
            )
            for index in range(notes_on_list_page)
        ]
        Note.objects.bulk_create(all_notes)

    def test_notes_for_author(self):
        self.client.force_login(self.author)
        response = self.client.get(reverse('notes:list'))
        # Код ответа не проверяем, его уже проверили в тестах маршрутов.
        # Получаем список объектов из словаря контекста.
        object_list = response.context['object_list']
        # Определяем количество записей в списке.
        notes_count = object_list.count()
        # Проверяем, что на странице именно 10 новостей.
        self.assertEqual(notes_count, notes_on_list_page + 1)

    def test_notes_for_other_author(self):
        self.client.force_login(self.other_author)
        response = self.client.get(reverse('notes:detail', args=(self.one_note.slug,)))
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)


class TestAddPage(TestCase):

    def test_authorized_client_has_form(self):
        # Авторизуем клиент при помощи ранее созданного пользователя.
        self.client.force_login(User.objects.create(username='Лев Толстой'))
        response = self.client.get(reverse("notes:add"))
        self.assertIn('form', response.context)
        # Проверим, что объект формы соответствует нужному классу формы.
        self.assertIsInstance(response.context['form'], NoteForm)
