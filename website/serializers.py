from rest_framework import serializers
from .models import WebsiteURL

class WebsiteSerializers(serializers.ModelSerializer):
  url = serializers.URLField()
  class Meta:
    model = WebsiteURL
    fields = ['id', 'url', 'tld', 'status', 'created']
    read_only_fields = ['tld', 'status', 'created']
