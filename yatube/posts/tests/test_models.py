from django.test import TestCase

from posts.models import Post, Group, User
from .test_urls import test_data


class PostModelTest(TestCase):
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
        cls.post = Post.objects.create(
            text=test_data['post_text'],
            author=cls.user,
            group=cls.group,
        )

    def test_post_object_name_is_title_field(self):
        """Test post text method"""
        post = PostModelTest.post
        expected_object_name = post.text[:15]
        self.assertIn(expected_object_name, str(post))

    def test_group_object_name_is_title_field(self):
        """Test group title method"""
        group = PostModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))
