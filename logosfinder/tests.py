from unittest import mock

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import User

from logosfinder.models import Logo
from logosfinder.tasks import search_logo_for_site, update_old_logos
from logosfinder.utils import download_image_from_url, resize_image, encode_image_to_base64
from website.models import WebsiteURL, TLD
from django.core.files.uploadedfile import SimpleUploadedFile
import base64

from django.utils import timezone
from datetime import timedelta

import unittest
from PIL import Image
from io import BytesIO


class LogosViewSetTestCase(APITestCase):
  def setUp(self):
    self.user = User.objects.create_superuser(username='user2', password='22222')
    self.client = APIClient()

    url = reverse('token_obtain_pair')
    response = self.client.post(url, {'username': 'user2', 'password':'22222'})

    self.assertEqual(response.status_code, 200)
    self.token = response.data['access']
    self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

    self.tld = TLD.objects.create(name='.com')
    self.site = WebsiteURL.objects.create(url='https://example.com', tld=self.tld)
    self.base64_logo = base64.b64encode(b"testdata").decode('utf-8')
    self.file_logo = SimpleUploadedFile("test.png", b"filedata", content_type="image/png")

  def test_retrieve_logo_base64_success(self):
    Logo.objects.create(website=self.site, image_base64=self.base64_logo, version=1)

    url = reverse('logo-detail', args=[self.site.id])
    response = self.client.get(url)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.data['image'], self.base64_logo)

  def test_retrieve_logo_file_success(self):
    Logo.objects.create(website=self.site, image=self.file_logo, version=1)

    url = reverse('logo-logo-file', args=[self.site.id])
    response = self.client.get(url)
    self.assertEqual(response.status_code, 200)
    self.assertIn('image_url', response.data)

  @mock.patch('logosfinder.tasks.find_logo_clearbit')
  @mock.patch('logosfinder.tasks.find_logo_from_html')
  @mock.patch('logosfinder.tasks.download_image_from_url')
  @mock.patch('logosfinder.tasks.resize_image')
  @mock.patch('logosfinder.tasks.encode_image_to_base64')
  def test_search_logo_for_site_creates_logo(self, mock_encode, mock_resize, mock_download, mock_find_html,
                                             mock_find_clearbit):

    mock_find_clearbit.return_value = 'http://logo-url.com/logo.png'
    mock_find_html.return_value = None
    mock_download.return_value = b'imagebytes'
    mock_resize.return_value = b'resizedbytes'
    mock_encode.return_value = 'base64string'

    result = search_logo_for_site(self.site.id)

    self.assertIn('Logo saved', result)
    self.assertTrue(Logo.objects.filter(website=self.site).exists())

  def test_search_logo_for_site_site_not_found(self):
    result = search_logo_for_site(999999)
    self.assertEqual(result, 'Site 999999 not found!')

  def test_search_logo_for_site_logo_recent_exists(self):

    Logo.objects.create(
      website=self.site,
      created=timezone.now(),
      version=1,
      image_base64='base64',
      path='path',
      original_url='url',
      source=Logo.CLEARBIT,
      title='title',
    )

    result = search_logo_for_site(self.site.id)
    self.assertIn('Logo already exists', result)

  class UpdateOldLogosTaskTestCase(TestCase):
    @mock.patch('logosfinder.tasks.search_logo_for_site.delay')
    def test_update_old_logos_calls_task(self, mock_delay):
      tld = TLD.objects.create(name='.com')
      site_old = WebsiteURL.objects.create(url='https://oldsite.com', tld=tld)

      Logo.objects.create(
        website=site_old,
        created=timezone.now() - timedelta(days=100),
        version=1,
        image_base64='base64',
        path='path',
        original_url='url',
        source=Logo.CLEARBIT,
        title='title',
      )

      result = update_old_logos()

      mock_delay.assert_called_once_with(site_old.id)
      self.assertIn('Updated', result)



class ImageUtilsTestCase(unittest.TestCase):

  @mock.patch('logosfinder.utils.requests.get')
  def test_download_image_from_url_success(self, mock_get):
    mock_response = mock.Mock()
    mock_response.content = b'test image bytes'
    mock_response.raise_for_status = mock.Mock()
    mock_get.return_value = mock_response

    result = download_image_from_url('http://example.com/logo.png')

    self.assertIsInstance(result, bytes)
    self.assertEqual(result, b'test image bytes')

  @mock.patch('logosfinder.utils.requests.get')
  def test_download_image_from_url_failure(self, mock_get):
    mock_response = mock.Mock()
    mock_response.raise_for_status.side_effect = Exception("404 Not Found")
    mock_get.return_value = mock_response

    result = download_image_from_url('http://example.com/logo.png')

    self.assertIsNone(result)


  def test_resize_image_with_bytes(self):
      img = Image.new("RGB", (100, 100), color="red")
      buffer = BytesIO()
      img.save(buffer, format="PNG")
      img_bytes = buffer.getvalue()

      resized_bytes = resize_image(img_bytes, size=(64, 64))
      self.assertIsInstance(resized_bytes, bytes)


      resized_img = Image.open(BytesIO(resized_bytes))
      self.assertEqual(resized_img.size, (64, 64))

  def test_resize_image_with_PIL_Image(self):
      img = Image.new("RGB", (100, 100), color="blue")
      resized_bytes = resize_image(img, size=(32, 32))
      self.assertIsInstance(resized_bytes, bytes)
      resized_img = Image.open(BytesIO(resized_bytes))
      self.assertEqual(resized_img.size, (32, 32))

  def test_encode_image_to_base64(self):
      data = b"test bytes"
      encoded = encode_image_to_base64(data)
      self.assertIsInstance(encoded, str)
      self.assertTrue(encoded.startswith(base64.b64encode(b"test").decode("utf-8")[:3]))


if __name__ == "__main__":
    unittest.main()


