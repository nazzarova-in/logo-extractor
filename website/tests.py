from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient, APIRequestFactory

from .models import WebsiteURL, TLD
from .serializers import WebsiteSerializers
from django.contrib.auth.models import User


class WebsiteURLViewSetTestCase(APITestCase):
  def setUp(self):
    self.user = User.objects.create_superuser(username='user', password='11111')
    self.client = APIClient()

    url = reverse('token_obtain_pair')
    response = self.client.post(url, {'username': 'user', 'password':'11111'})

    self.assertEqual(response.status_code, 200)
    self.token = response.data['access']
    self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)


  def test_get_websites(self):
    tld1 = TLD.objects.create(name='.md')
    tld2 = TLD.objects.create(name= '.com')
    website1 = WebsiteURL.objects.create(url='https://livrareflori.md/', tld=tld1)
    website2 = WebsiteURL.objects.create(url='https://flowwow.com/', tld=tld2)

    url = reverse('website-list')
    response = self.client.get(url)
    serializer_data = WebsiteSerializers([website1, website2], many=True).data

    self.assertEqual(status.HTTP_200_OK, response.status_code)
    self.assertEqual(serializer_data, response.data)

class WebsiteCreateTest(TestCase):
  def setUp(self):
    self.client = APIClient()

  def test_create_urls(self):
    url = reverse('website-list')
    data = {
      "urls": ["example.com"]

    }

    response = self.client.post(url, data, format='json')
    self.assertEqual(response.status_code, status.HTTP_201_CREATED)

  def test_create_invali_url(self):
    url = reverse('website-list')
    data = {
      "urls": ['']
    }

    response = self.client.post(url, data, format='json')
    self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    self.assertEqual(response.data[0]['status'], 'invalid')

  def test_create_url_already_exists(self):
    WebsiteURL.objects.create(url="https://example.com", tld=TLD.objects.create(name="com"))

    url = reverse('website-list')
    data = {"urls": ["example.com"]}

    response = self.client.post(url, data, format='json')
    self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    self.assertEqual(response.data[0]['status'], 'already exists')
