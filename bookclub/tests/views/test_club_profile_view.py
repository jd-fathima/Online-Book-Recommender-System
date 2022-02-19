from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User, Club
from bookclub.tests.helpers import reverse_with_next

"""Tests for Club Profile """

class ClubProfileTest(TestCase):

    fixtures = ['bookclub/tests/fixtures/default_users.json', 'bookclub/tests/fixtures/default_clubs.json']

    def setUp(self):
        self.url = reverse('club_profile')
        self.user = User.objects.get(pk=1)

    def test_club_profile_url(self):
        self.assertEqual(self.url, 'club_profile/<int:club_id>/')

    def test_correct_club_profile_template(self):
        self.client.login(email=self.user.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "club_profile.html")

    def test_get_club_profile_redirects_when_not_logged_in(self):
        redirect_url = reverse_with_next('log_in', self.url)
        response = self.client.get(self.url)
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def _is_logged_in(self):
        return '_auth_user_id' in self.client.session.keys()



