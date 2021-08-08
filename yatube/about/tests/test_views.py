from django.test import TestCase, Client
from django.urls import reverse


class AboutViewsTests(TestCase):
    template_url_names = (
        ('about/author.html', reverse('about:author')),
        ('about/tech.html', reverse('about:tech')),
    )

    def setUp(self):
        self.guest_client = Client()

    def test_about_page_uses_correct_template(self):
        for template, address in self.template_url_names:
            response = self.guest_client.get(address)
            self.assertTemplateUsed(response, template)
