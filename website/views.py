from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import WebsiteURL, TLD
from .serializers import WebsiteSerializers
from logosfinder.tasks import search_logo_for_site


class WebSiteURLViewSet(viewsets.ModelViewSet):
  queryset = WebsiteURL.objects.all()
  serializer_class = WebsiteSerializers

  def create(self, request, *args, **kwargs):
    if isinstance(request.data, dict) and 'urls' in request.data:
      results = []
      for url in request.data['urls']:
        if not url.startswith("http://") and not url.startswith("https://"):
          url = "https://" + url

        serializer = WebsiteSerializers(data={'url': url})
        if serializer.is_valid():
          tld = TLD.objects.get_or_create_from_url(url)
          obj, created_flag = WebsiteURL.objects.get_or_create(
            url=url, defaults={'tld': tld}
          )
          status_str = 'created' if created_flag else 'already exists'

          search_logo_for_site.delay(obj.id)

          results.append({'url': url, 'status': status_str})
        else:
          results.append({'url': url, 'status': 'invalid'})

      return Response(results, status=status.HTTP_201_CREATED)

    return super().create(request, *args, **kwargs)

  def perform_create(self, serializer):
    url = serializer.validated_data['url']
    if not url.startswith("http://") and not url.startswith("https://"):
      url = "https://" + url
    tld = TLD.objects.get_or_create_from_url(url)
    site = serializer.save(tld=tld, url=url)

    search_logo_for_site.delay(site.id)


