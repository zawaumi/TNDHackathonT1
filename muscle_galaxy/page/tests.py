from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import Workout


class PageAuthTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='member',
            password='password123',
            height=170,
            weight=70,
        )

    def test_dashboard_requires_login(self):
        response = self.client.get('/home/')

        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response['Location'])

    def test_welcome_is_public(self):
        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Muscle Galaxy')

    def test_timer_completion_endpoint_starts_workout_record(self):
        self.client.login(username='member', password='password123')

        response = self.client.post('/timer/record/start/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Workout.objects.filter(user=self.user).count(), 1)
        self.assertGreater(Workout.objects.get(user=self.user).sets.count(), 0)

    def test_register_redirects_to_initial_info(self):
        response = self.client.post('/register/', {
            'username': 'new_member',
            'email': 'new@example.com',
            'password1': 'StrongPass12345',
            'password2': 'StrongPass12345',
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/initial-info/')
        self.assertTrue(get_user_model().objects.filter(username='new_member').exists())
        self.assertIn('_auth_user_id', self.client.session)

    def test_login_redirects_to_initial_info_when_profile_is_missing(self):
        get_user_model().objects.create_user(username='missing_info', password='password123')

        response = self.client.post('/login/', {
            'username': 'missing_info',
            'password': 'password123',
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/initial-info/')

    def test_initial_info_page_does_not_logout_user(self):
        get_user_model().objects.create_user(username='profile_pending', password='password123')
        self.client.login(username='profile_pending', password='password123')

        response = self.client.get('/initial-info/')

        self.assertEqual(response.status_code, 200)
        self.assertIn('_auth_user_id', self.client.session)

    def test_initial_info_requires_height_and_weight(self):
        user = get_user_model().objects.create_user(username='profile_empty', password='password123')
        self.client.login(username='profile_empty', password='password123')

        response = self.client.post('/initial-info/', {'gender': 'other'})
        user.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(user.height)
        self.assertIsNone(user.weight)

    def test_initial_info_redirects_to_dashboard_after_profile_saved(self):
        user = get_user_model().objects.create_user(username='profile_ready', password='password123')
        self.client.login(username='profile_ready', password='password123')

        response = self.client.post('/initial-info/', {
            'height': '170',
            'weight': '70',
            'gender': 'other',
            'birth_date': '1990-01-01',
            'bio': '週3回で継続したい',
        })
        user.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/home/')
        self.assertEqual(user.height, 170)
        self.assertEqual(user.weight, 70)
