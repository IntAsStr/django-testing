import pytest
from pytest_lazy_fixtures import lf
from http import HTTPStatus

from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',  # Имя параметра функции.
    # Значения, которые будут передаваться в name.
    ('news:home', 'users:login', 'users:logout', 'users:signup')
)
def test_home_availability_for_anonymous_user(client, name):
    url = reverse(name)
    if name == 'users:logout':
        response = client.post(url)
    else:
        response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_news_detail_available(client, news):
    url = reverse('news:detail', args=(news.pk,))
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


def test_comment_edit_availability(author_client, comment):
    url = reverse('news:edit', args=(comment.pk,))
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


def test_comment_delete_availability(author_client, comment):
    url = reverse('news:delete', args=(comment.pk,))
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_comment_edit_not_available_for_reader(reader_client, comment):
    url = reverse('news:edit', args=(comment.pk,))
    response = reader_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.django_db
def test_comment_delete_not_available_for_reader(reader_client, comment):
    url = reverse('news:delete', args=(comment.pk,))
    response = reader_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize(
    'name, args',
    [
        ('news:edit', lf('comment_id_for_args')),
        ('news:delete', lf('comment_id_for_args')),
    ]
)
def test_redirect_anonymous_to_login(client, name, args):
    login_url = reverse('users:login')
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == expected_url
