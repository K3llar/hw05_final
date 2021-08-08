from django.test import TestCase, Client
from django.urls import reverse


class AboutURLTests(TestCase):
    template_url_names = (
        ('about/author.html', reverse('about:author')),
        ('about/tech.html', reverse('about:tech')),
    )

    def setUp(self):
        self.guest_client = Client()

    def test_about_urls_exist(self):
        for template, address in self.template_url_names:
            with self.subTest(adress=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, 200)

    def test_about_urls_uses_correct_template(self):
        for template, address in self.template_url_names:
            with self.subTest(adress=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)
