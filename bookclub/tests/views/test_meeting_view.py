"""Tests of the meeting view."""
from django.test import TestCase
from django.urls import reverse
from bookclub.models import User, Club, Meeting
from django.contrib import messages
from bookclub.forms import ScheduleMeetingForm
from datetime import timedelta, date, time, datetime


class MeetingViewTestCase(TestCase):
    """Tests of the application view."""

    fixtures = ['bookclub/tests/fixtures/default_users.json', 'bookclub/tests/fixtures/default_clubs.json']

    def setUp(self):
        self.url = reverse('schedule_meeting', kwargs={'pk':1})
        self.john = User.objects.get(pk=1)
        self.jane = User.objects.get(pk=2)
        self.bush_club = Club.objects.get(pk=1)
        self.somerset_club = Club.objects.get(pk=2)
        
        self.today = date.today()
        self.yesterday = self.today - timedelta(days=1)
        self.tomorrow = self.today + timedelta(days=1)
        last_hour_date_time = datetime.now() - timedelta(hours = 1)
        next_hour_date_time = datetime.now() + timedelta(hours = 1)
        self.past_time = time(last_hour_date_time.hour, 0)
        self.future_time = time(next_hour_date_time.hour, 0)

        self.online_form_input = {
            'date':self.tomorrow,
            'time':self.future_time,
            'address':'https://www.teams.com/thismeeting'
        }
        self.in_person_form_input = {
            'date':self.tomorrow,
            'time':self.future_time,
            'address':'123 Road London'
        }

    def test_schedule_meeting_url(self):
        self.assertEqual(self.url,'/club_profile/1/meeting/')

    def test_schedule_meeting_uses_correct_template(self):
        self.client.login(email=self.john.get_email(), password='Password123')
        response = self.client.get('/club_profile/1/meeting/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'schedule_meeting.html')
    
    def test_meeting_schedule_button_is_present_if_owner(self):
        self.client.login(email=self.john.get_email(), password='Password123')
        response = self.client.get('/club_profile/1/')
        html = response.content.decode('utf8')
        self.assertIn('Schedule meeting',  html)

    def test_meeting_schedule_button_not_present_if_not_owner(self):
        self.client.login(email=self.jane.get_email(), password='Password123')
        response = self.client.get('/club_profile/1/')
        html = response.content.decode('utf8')
        self.assertNotIn('Schedule meeting',  html)

    def test_get_meeting(self):
        self.client.login(email=self.john.get_email(), password='Password123')
        response = self.client.get('/club_profile/1/meeting/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'schedule_meeting.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ScheduleMeetingForm))

    def test_successful_online_meeting_scheduling(self):
        self.client.login(email=self.john.get_email(), password='Password123')
        beforeCount = Meeting.objects.all().count()
        response = self.client.post('/club_profile/1/meeting/', self.online_form_input, follow=True)       
        redirect_url = reverse('home')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        afterCount = Meeting.objects.all().count()
        self.assertEqual(beforeCount, afterCount-1)

    def test_successful_in_person_meeting_scheduling(self):
        self.client.login(email=self.john.get_email(), password='Password123')
        beforeCount = Meeting.objects.all().count()
        response = self.client.post('/club_profile/3/meeting/', self.in_person_form_input, follow=True)       
        redirect_url = reverse('home')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.SUCCESS)
        afterCount = Meeting.objects.all().count()
        self.assertEqual(beforeCount, afterCount-1)

    def test_unsuccessful_online_meeting_scheduling(self):
        self.client.login(email=self.john.get_email(), password='Password123')
        beforeCount = Meeting.objects.all().count()
        self.online_form_input['date'] = self.yesterday
        response = self.client.post('/club_profile/1/meeting/', self.online_form_input, follow=True)    
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'schedule_meeting.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ScheduleMeetingForm))
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        afterCount = Meeting.objects.all().count()
        self.assertEqual(beforeCount, afterCount)

    def test_unsuccessful_in_person_meeting_scheduling(self):
        self.client.login(email=self.john.get_email(), password='Password123')
        beforeCount = Meeting.objects.all().count()
        self.in_person_form_input['date'] = self.yesterday
        response = self.client.post('/club_profile/3/meeting/', self.in_person_form_input, follow=True)    
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'schedule_meeting.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, ScheduleMeetingForm))
        messages_list = list(response.context['messages'])
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
        afterCount = Meeting.objects.all().count()
        self.assertEqual(beforeCount, afterCount)
