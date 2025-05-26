from .models import Logo, WebsiteURL
from .serializers import LogoSerializer
from rest_framework import viewsets, status
from rest_framework.response import Response

class LogosViewSet(viewsets.ModelViewSet):
  queryset = Logo.objects.all()
  serializer_class = LogoSerializer

  def retrieve(self, request, pk=None):
    logo = Logo.objects.filter(website_id=pk).first()
    if logo and logo.image_base64:
      return Response({"image": logo.image_base64})
    else:
      return Response({"message": "Logo not found"})

