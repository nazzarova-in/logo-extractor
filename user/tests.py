from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

class UserRegistrationAPITestCase(APITestCase):
  def test_registration(self):
    url = reverse('register')
    data = {
      'username': "user2",
      'email': "user2@gmail.com",
      'password': "password"
    }
    response = self.client.post(url, data)
    self.assertEqual(status.HTTP_200_OK, response.status_code)
