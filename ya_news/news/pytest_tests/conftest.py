import pytest

from django.test.client import Client
from django.utils import timezone
from datetime import timedelta

from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def reader(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader):
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def news():
    return News.objects.create(
        title='Тестовая новость',
        text='Текст новости',
    )


@pytest.fixture
def news_id_for_args(news):
    return (news.pk,)


@pytest.fixture
def form_data():
    return {
        'title': 'Новый заголовок',
        'text': 'Новый текст',
    }


@pytest.fixture
def comment(author, news):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Тестовый комментарий'
    )


@pytest.fixture
def comment_id_for_args(comment):
    return (comment.pk,)


@pytest.fixture
def bulk_news():
    today = timezone.now()
    return News.objects.bulk_create(
        News(
            title=f'Новость {index}',
            text='Текст новости',
            date=today - timedelta(days=index)
        )
        for index in range(15)
    )


@pytest.fixture
def news_with_comments(news, author):
    now = timezone.now()
    comments = [
        Comment.objects.create(
            news=news,
            author=author,
            text=f'Комментарий {index}',
            created=now + timedelta(hours=index)
        )
        for index in range(5)
    ]
    return comments


@pytest.fixture
def form_comment_data():
    return {
        'text': 'Новый текст',
    }
