import pytest

from django.urls import reverse


@pytest.mark.django_db
def test_available_news_nomore_ten(client, bulk_news):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    assert len(object_list) == 10


@pytest.mark.django_db
def test_news_order_on_home_page(client, bulk_news):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    assert all_dates == sorted(all_dates, reverse=True)


@pytest.mark.django_db
def test_comments_order(client, news_with_comments):
    url = reverse('news:detail', args=(news_with_comments.pk,))
    response = client.get(url)

    news_object = response.context['news']
    comments = news_object.comment_set.all()
    all_timestamps = [comment.created for comment in comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.django_db
def test_anonymous_user_no_comment_form(client, news):
    url = reverse('news:detail', args=(news.pk,))
    response = client.get(url)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_user_has_comment_form(author_client, news, form_comment_data):
    url = reverse('news:detail', args=(news.pk,))
    response = author_client.get(url)
    assert 'form' in response.context
