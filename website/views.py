from datetime import timedelta
from django.utils import timezone
from rest_framework import status, viewsets, filters
from rest_framework.response import Response
from .models import WebsiteURL, TLD
from .serializers import WebsiteSerializers
from logosfinder.tasks import search_logo_for_site
from logosfinder.models import Logo

class WebSiteURLViewSet(viewsets.ModelViewSet):
  queryset = WebsiteURL.objects.all()
  serializer_class = WebsiteSerializers
  filter_backends = [filters.SearchFilter]
  search_fields = ['url']

  def create(self, request, *args, **kwargs):
    urls = []

    if isinstance(request.data, dict):
      if 'urls' in request.data and isinstance(request.data['urls'], list):
        urls = request.data['urls']
      elif 'url' in request.data:
        urls = [request.data['url']]

    if urls:
      results = []

      for url in urls:
        if not url.startswith("http://") and not url.startswith("https://"):
          url = "https://" + url

        serializer = WebsiteSerializers(data={'url': url})
        if serializer.is_valid():
          tld = TLD.objects.get_or_create_from_url(url)
          obj, created_flag = WebsiteURL.objects.get_or_create(
            url=url, defaults={'tld': tld}
          )
          status_str = 'created' if created_flag else 'already exists'

          if created_flag:
            search_logo_for_site.delay(obj.id)
          else:
            last_logo = Logo.objects.filter(website=obj).order_by('-created').first()
            if last_logo:
              three_months_ago = timezone.now() - timedelta(days=90)
              if last_logo.created < three_months_ago:
                search_logo_for_site.apply_async(args=[obj.id], countdown=300)
            else:
              search_logo_for_site.delay(obj.id)

          results.append({'url': url, 'status': status_str})
        else:
          results.append({'url': url, 'status': 'invalid'})

      return Response(results, status=status.HTTP_201_CREATED)

    return super().create(request, *args, **kwargs)
