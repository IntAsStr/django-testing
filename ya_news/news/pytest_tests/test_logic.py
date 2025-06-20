import pytest
from http import HTTPStatus

from django.urls import reverse

from news.forms import WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_cant_add_comment(client, news, form_comment_data):
    url = reverse('news:detail', args=(news.pk,))
    initial_count = Comment.objects.count()
    login_url = reverse('users:login')
    redirect_url = f'{login_url}?next={url}'
    response = client.post(url, data=form_comment_data)
    assert response.url == redirect_url
    assert Comment.objects.count() == initial_count


def test_author_can_add_comment(author_client, news, form_comment_data):
    url = reverse('news:detail', args=(news.pk,))
    initial_count = Comment.objects.count()
    response = author_client.post(url, data=form_comment_data)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == initial_count + 1


def test_comment_with_bad_words_not_accepted(author_client, news):
    url = reverse('news:detail', args=(news.pk,))
    initial_count = Comment.objects.count()
    bad_comment_data = {
        'text': 'Какой-то негодяй оставил этот комментарий'
    }
    response = author_client.post(url, data=bad_comment_data)
    form = response.context['form']
    assert 'form' in response.context
    assert WARNING in form.errors['text'][0]
    assert Comment.objects.count() == initial_count


@pytest.mark.django_db
def test_author_can_edit_comment(author_client, comment):
    # Arrange
    edit_url = reverse('news:edit', args=(comment.pk,))
    new_text = 'Обновлённый текст комментария'
    original_text = comment.text

    # Act
    response = author_client.post(edit_url, data={'text': new_text})

    # Assert
    comment.refresh_from_db()
    assert response.status_code == HTTPStatus.FOUND
    assert comment.text == new_text
    assert comment.text != original_text


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, comment):
    # Arrange
    delete_url = reverse('news:delete', args=(comment.pk,))
    initial_count = Comment.objects.count()

    # Act
    response = author_client.post(delete_url)

    # Assert
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == initial_count - 1


@pytest.mark.django_db
def test_reader_cant_edit_comment(reader_client, comment):
    # Arrange
    edit_url = reverse('news:edit', args=(comment.pk,))

    # Act
    response = reader_client.get(edit_url)

    # Assert
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.django_db
def test_reader_cant_delete_comment(reader_client, comment):
    # Arrange - подготовка данных
    delete_url = reverse('news:delete', args=(comment.pk,))
    initial_count = Comment.objects.count()
    # Act - выполнение действия
    response = reader_client.post(delete_url)

    # Assert - проверки
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == initial_count
