from django.utils.encoding import force_bytes
from django.test import (
    TestCase, 
)
from django.contrib.auth.models import User
from stakeholder.models import (
    UserProfile
)
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.contrib.messages import get_messages
from django.utils.http import (
    urlsafe_base64_encode
)
from sawps.email_verification_token import email_verification_token

class ActivateAccountTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        self.uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = email_verification_token.make_token(self.user)
        

    def test_activate_account_valid(self):
        url = reverse(
            'activate',
            kwargs={'uidb64': self.uidb64, 'token': self.token}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        # Check for a success message
        messages = [str(msg) for msg in get_messages(response.wsgi_request)]
        self.assertEqual(
            'Your account have been confirmed.',
            messages[0]
        )

        # Check if a UserProfile is created
        self.assertTrue(UserProfile.objects.filter(user=self.user).exists())

    def test_activate_account_invalid_user(self):
        # Test with an invalid user ID
        uidb64 = urlsafe_base64_encode(force_bytes(5))
        url = reverse(
            'activate',
            kwargs={'uidb64': uidb64, 'token': self.token}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        # Check for a warning message
        messages = [str(msg) for msg in get_messages(response.wsgi_request)]
        self.assertEqual(
            'The confirmation link was invalid,possibly because it has already been used.',
            messages[0]
        )