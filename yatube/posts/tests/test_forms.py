import shutil
import tempfile

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Post, Group, User
from .test_urls import (test_data,
                        templates_url_names,
                        templates_url_names_login_required)


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.user = User.objects.create_user(username=test_data['user'])
        cls.group = Group.objects.create(
            title=test_data['group_title'],
            slug=test_data['group_slug'],
            description=test_data['group_description'],
        )
        cls.form = PostForm

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_redirect_with_create_post(self):
        """Test redirection after create new post and check database"""
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': test_data['post_text'],
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            templates_url_names_login_required['posts/new_post.html'],
            data=form_data,
            follow=True,
        )
        last_post = Post.objects.first()
        self.assertRedirects(response,
                             templates_url_names['posts/index.html'])
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(last_post.text, test_data['post_text'])
        self.assertEqual(last_post.author, self.user)
        self.assertEqual(last_post.group, self.group)
        self.assertEqual(last_post.image.name, f'posts/{uploaded.name}')

    def test_changing_post_with_edit(self):
        """Test redirection after edit post and check database"""
        posts_count = Post.objects.count()
        post = Post.objects.create(
            text=test_data['post_text'],
            author=self.user,
            group=self.group,
        )
        form_data = {
            'text': 'edited_' + test_data['post_text'],
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('edit_post',
                    kwargs={
                        'username': self.user,
                        'post_id': post.id,
                    }),
            data=form_data,
            follow=True,
        )
        last_post = Post.objects.first()
        self.assertRedirects(response,
                             reverse('post',
                                     kwargs={
                                         'username': self.user,
                                         'post_id': post.id,
                                     }))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(last_post.text, 'edited_' + test_data['post_text'])
        self.assertEqual(last_post.author, self.user)
        self.assertEqual(last_post.group, self.group)

    def test_cache(self):
        """Test cache"""
        posts_count = Post.objects.count()
        self.assertEqual(Post.objects.count(), 0)
        form_data = {
            'text': test_data['post_text'],
            'group': self.group.id,
        }
        self.authorized_client.post(
            templates_url_names_login_required['posts/new_post.html'],
            data=form_data,
            follow=True,
        )
        response_cache = self.authorized_client.get(
            templates_url_names['posts/index.html']
        )
        self.assertEqual(
            len(response_cache.context.get('page').object_list),
            posts_count + 1
        )
        self.authorized_client.post(
            templates_url_names_login_required['posts/new_post.html'],
            data=form_data,
            follow=True,
        )
        response_cache_1 = self.authorized_client.get(
            templates_url_names['posts/index.html']
        )
        self.assertEqual(
            len(response_cache_1.context.get('page').object_list),
            posts_count + 1)
        cache.clear()
        response_final = self.authorized_client.get(
            templates_url_names['posts/index.html'])
        self.assertEqual(
            len(response_final.context.get('page').object_list),
            posts_count + 2)
