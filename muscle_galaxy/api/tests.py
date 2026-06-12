import json

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from .models import AIPlan


@override_settings(AI_PLANNER_MOCK_MODE=True, OPENAI_ENABLE_IMAGE_GENERATION=False)
class AIPlanAPITests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='tester', password='password123')
        self.client.login(username='tester', password='password123')

    def test_generate_plan_creates_monthly_mock_plan(self):
        response = self.client.post(
            '/api/ai/plans/generate/',
            data=json.dumps({
                'goal': 'muscle_gain',
                'height_cm': 170,
                'weight_kg': 70,
                'age': 30,
                'gender': 'other',
                'experience_level': 'beginner',
                'training_days_per_week': 4,
                'request_text': '朝食は短時間で作りたい',
                'generate_images': True,
            }),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['provider'], 'mock')
        self.assertTrue(data['mock_mode'])
        self.assertEqual(data['plan']['weeks'], 4)
        self.assertEqual(len(data['plan']['days']), 28)
        self.assertEqual(AIPlan.objects.count(), 1)

    def test_adjust_plan_keeps_crud_contract(self):
        create_response = self.client.post(
            '/api/ai/plans/generate/',
            data=json.dumps({
                'goal': 'fat_loss',
                'height_cm': 165,
                'weight_kg': 68,
                'age': 28,
                'training_days_per_week': 3,
            }),
            content_type='application/json',
        )
        plan_id = create_response.json()['id']

        adjust_response = self.client.post(
            f'/api/ai/plans/{plan_id}/adjust/',
            data=json.dumps({'request_text': '脚の日を軽めにしてほしい'}),
            content_type='application/json',
        )

        self.assertEqual(adjust_response.status_code, 200)
        data = adjust_response.json()
        self.assertEqual(data['id'], plan_id)
        self.assertEqual(data['revisions_count'], 1)
        self.assertIn('脚の日を軽め', data['plan']['adjustment_notes'][-1])

    def test_openapi_schema_is_available(self):
        response = self.client.get('/api/schema/')

        self.assertEqual(response.status_code, 200)

    def test_health_endpoint_requires_login(self):
        self.client.logout()

        response = self.client.get('/api/health/')

        self.assertEqual(response.status_code, 403)
