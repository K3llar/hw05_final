from django.core.cache import cache
from django.test import TestCase

from posts.models import Post, Group, User
from .test_urls import test_data, templates_url_names


class PaginatorTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username=test_data['user'])
        cls.group = Group.objects.create(
            title=test_data['group_title'],
            slug=test_data['group_slug'],
            description=test_data['group_description'],
        )
        Post.objects.bulk_create((Post
                                  (text=test_data['post_text'],
                                   author=cls.user)
                                  for _ in range(15)),
                                 batch_size=14)
        cache.clear()

    def test_pagination_is_ten_at_first_page(self):
        """Pagination test. First page must contain 10 objects"""
        response = self.client.get(templates_url_names['posts/index.html'])
        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_pagination_is_five_at_second_page(self):
        """Pagination test. Second page must contain 5 objects"""
        response = self.client.get('/?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 5)
