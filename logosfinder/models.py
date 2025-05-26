from django.db import models
from website.models import WebsiteURL


class Logo(models.Model):
  CLEARBIT = 'CLEARBIT'
  HTML_PARSER = 'HTML_PARSER'

  LOGO_SOURCE = (
        (CLEARBIT, 'Clearbit'),
        (HTML_PARSER, 'HTML parser')
    )

  title = models.CharField(max_length=255)
  path = models.CharField(max_length=255)
  original_url = models.CharField(max_length=255)
  source = models.CharField(choices=LOGO_SOURCE, max_length=25)
  website = models.ForeignKey(WebsiteURL, on_delete=models.CASCADE)
  version = models.IntegerField()
  created = models.DateTimeField(auto_now_add=True)
  image_base64 = models.TextField(blank=True, null=True)

  def __str__(self):
    return f"{self.website.url} - {self.source}"

