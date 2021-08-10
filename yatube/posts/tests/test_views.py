from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.models import Post, Group, User, Follow
from .test_urls import (test_data,
                        templates_url_names,
                        templates_url_names_login_required)


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group_1 = Group.objects.create(
            title=test_data['an_gr_tit'],
            slug=test_data['an_gr_sl'],
            description=test_data['an_gr_desc'],
        )
        cls.user = User.objects.create_user(
            username=test_data['user'])
        cls.follow_user = User.objects.create_user(
            username=test_data['user_not_author'])
        cls.follow_user_2 = User.objects.create_user(
            username='another_follower')
        cls.group = Group.objects.create(
            title=test_data['group_title'],
            slug=test_data['group_slug'],
            description=test_data['group_description'],
        )
        cls.post_author = Post.objects.create(
            text=test_data['post_text'],
            author=cls.user,
            group=cls.group,
        )
        templates_url_names['posts/post.html'] = (
            reverse('post',
                    kwargs={
                        'username': test_data['user'],
                        'post_id': cls.post_author.id,
                    }))
        cls.edit_post_url = {
            'posts/new_post.html': (
                reverse('edit_post',
                        kwargs={
                            'username': test_data['user'],
                            'post_id': cls.post_author.id,
                        }))
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_pages_uses_correct_templates(self):
        """Test templates used by pages"""
        for template, reverse_name in templates_url_names.items():
            with self.subTest(template=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
        for template, reverse_name in (
                templates_url_names_login_required.items()):
            with self.subTest(template=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
        for template, reverse_name in self.edit_post_url.items():
            with self.subTest(template=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_available_at_main_page(self):
        """Test main page context"""
        response = self.client.get(templates_url_names['posts/index.html'])
        self.assertEqual(len(response.context.get('page').object_list), 1)

    def test_post_available_at_group_page(self):
        """Group post visibility test"""
        response = self.client.get(templates_url_names['posts/group.html'])
        self.assertEqual(len(response.context.get('page').object_list), 1)

    def test_post_not_available_at_wrong_group(self):
        """Group post not visible at wrong group page"""
        response = self.client.get(reverse('group',
                                           kwargs={'slug': self.group_1.slug}))
        self.assertEqual(len(response.context.get('page').object_list), 0)

    def test_post_group_page_fields(self):
        """Test group post fields"""
        # Правильно ли я понимаю, что данный тест повторяется с тестом
        # в test_forms и его можно убрать?
        response = self.client.get(templates_url_names['posts/group.html'])
        first_object = response.context.get('page').object_list[0]
        post_text_0 = first_object.text
        post_group_0 = first_object.group.slug
        post_author_0 = first_object.author.username
        self.assertEqual(post_text_0, test_data['post_text'])
        self.assertEqual(post_group_0, test_data['group_slug'])
        self.assertEqual(post_author_0, test_data['user'])

    def test_home_page_show_correct_context(self):
        """Test home page context"""
        response = self.client.get(templates_url_names['posts/index.html'])
        context = response.context
        self.assertIn('page', context)

    def test_group_page_show_correct_context(self):
        """Test group post page context"""
        response = self.client.get(templates_url_names['posts/group.html'])
        context = response.context
        context_fields = ('group', 'page')
        for field in context_fields:
            with self.subTest(field=field):
                self.assertIn(field, context)

    def test_new_post_page_show_correct_context(self):
        """Test new post page context"""
        response = self.authorized_client.get(
            templates_url_names_login_required['posts/new_post.html'])
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for field, expected in form_fields.items():
            with self.subTest(field=field):
                context_field = response.context['form'].fields[field]
                self.assertIsInstance(context_field, expected)

    def test_profile_page_show_correct_context(self):
        """Test profile page context"""
        response = self.client.get(templates_url_names['posts/profile.html'])
        context = response.context
        context_fields = ('author', 'page')
        for field in context_fields:
            with self.subTest(field=field):
                self.assertIn(field, context)

    def test_edit_post_page_show_correct_context(self):
        """Test edit post page context"""
        response = self.authorized_client.get(
            self.edit_post_url['posts/new_post.html'])
        context = response.context
        context_fields = ('form', 'post', 'edit')
        for field in context_fields:
            with self.subTest(field=field):
                self.assertIn(field, context)

    def test_show_post_for_follow_user(self):
        """Test posts for followers"""
        self.authorized_client.force_login(self.follow_user)
        Follow.objects.create(user=self.follow_user, author=self.user)
        response = self.authorized_client.get(
            templates_url_names_login_required['posts/follow.html'])
        self.assertEqual(len(response.context.get('page').object_list), 1)
        self.authorized_client.force_login(self.follow_user_2)
        response = self.authorized_client.get(
            templates_url_names_login_required['posts/follow.html'])
        self.assertEqual(len(response.context.get('page').object_list), 0)

    def test_follow_and_unfollow_function(self):
        """Test function of class Follow"""
        self.authorized_client.force_login(self.follow_user)
        Follow.objects.create(user=self.follow_user, author=self.user)
        response = Follow.objects.filter(user=self.follow_user).count()
        self.assertEqual(response, 1)
        Follow.objects.filter(user=self.follow_user, author=self.user).delete()
        response = Follow.objects.filter(user=self.follow_user).count()
        self.assertEqual(response, 0)
