from django.test import TestCase, Client
from django.urls import reverse
from http import HTTPStatus

from posts.models import Post, Group, User

test_data = {
    'user': 'user',
    'user_not_author': 'not_author',
    'post_text': 'test text is testing post',
    'post_text_not_author': 'test text not author',
    'group_title': 'test_title',
    'group_slug': 'test_slug',
    'group_description': 'test_description',
    'an_gr_tit': 'an_title',
    'an_gr_sl': 'an_slug',
    'an_gr_desc': 'an_description',
    'wrong_group': 'wrong_slug',
}
templates_url_names = {
    'posts/index.html': reverse('index'),
    'posts/group.html': reverse('group',
                                kwargs={'slug': test_data['group_slug']}),
    'posts/profile.html': reverse('profile',
                                  kwargs={'username': test_data['user']}),
}
templates_url_names_login_required = {
    'posts/new_post.html': reverse('new_post'),
    'posts/follow.html': reverse('follow_index'),
}


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            username=test_data['user'])
        cls.user_not_author = User.objects.create_user(
            username=test_data['user_not_author'])
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
        cls.post_not_author = Post.objects.create(
            text=test_data['post_text_not_author'],
            author=cls.user_not_author,
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
        cls.comment_post_url = {
            'posts/comments.html': (
                reverse('comment',
                        kwargs={
                            'username': test_data['user'],
                            'post_id': cls.post_author.id,
                        })
            )
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.second_authorized_client = Client()

    def test_urls_available_for_guest_client(self):
        """Test guest client access for common urls"""
        for template, address in templates_url_names.items():
            with self.subTest(adress=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_non_available_for_guest_client(self):
        """Test guest client redirection for login-required urls"""
        for template, address in templates_url_names_login_required.items():
            with self.subTest(adress=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)
        for template, address in self.edit_post_url.items():
            with self.subTest(adress=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)
        for template, address in self.comment_post_url.items():
            with self.subTest(adress=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_urls_available_only_for_authorized_client(self):
        """Test authorized client access for login-required urls"""
        for template, address in templates_url_names_login_required.items():
            with self.subTest(adress=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
        for template, address in self.edit_post_url.items():
            with self.subTest(adress=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_from_edit_post_for_none_author(self):
        """Test redirection from edit post page for none-author client"""
        response = self.authorized_client.get(
            reverse('edit_post',
                    kwargs={
                        'username': self.user_not_author,
                        'post_id': self.post_not_author.id,
                    },
                    ), follow=True)
        self.assertRedirects(response,
                             reverse('post',
                                     kwargs={
                                         'username': self.user_not_author,
                                         'post_id': self.post_not_author.id,
                                     }, ))

    def test_wrong_page_get_404(self):
        """Test receiving 404 code from wrong page"""
        response = self.guest_client.get(
            reverse('group',
                    kwargs={'slug': test_data['wrong_group']})
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
