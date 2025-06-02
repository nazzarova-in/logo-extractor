from django.db import models
from .utils import tld_extractor


class TLDManager(models.Manager):
  def get_or_create_from_url(self, url):
    name = tld_extractor(url)
    tld, _ = self.get_or_create(name=name)
    return tld


class TLD(models.Model):
  name = models.CharField(max_length=10, unique=True)

  objects = TLDManager()

  def __str__(self):
    return self.name


class URLStatus(models.TextChoices):
  NEW = 'NEW', 'new'
  RENEW = 'RENEW', 'renew'
  FAILED = 'FAILED', 'failed'
  FINISHED = 'FINISHED', 'finished'


class WebsiteURL(models.Model):
  url = models.CharField(max_length=255, unique=True)
  tld = models.ForeignKey(TLD, on_delete=models.PROTECT)
  status = models.CharField(
    choices=URLStatus.choices,
    max_length=10,
    default=URLStatus.NEW
  )
  created = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return self.url
