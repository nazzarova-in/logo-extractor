from .models import Logo
from .serializers import LogoSerializer
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

class LogosViewSet(viewsets.ModelViewSet):
  queryset = Logo.objects.all()
  serializer_class = LogoSerializer

  def retrieve(self, request, pk=None):
    logo = Logo.objects.filter(website_id=pk).first()
    if logo and logo.image_base64:
      return Response({"image": logo.image_base64})
    else:
      return Response({"message": "Logo not found"})

  @action(detail=True, methods=['get'], url_path='file')
  def logo_file(self, request, pk=None):
    logo = Logo.objects.filter(website_id=pk).first()
    if logo and logo.image:
      serializer = LogoSerializer(logo, context={'request': request})
      return Response({"image_url": serializer.data.get("image_url")})
    return Response({"message": "Logo not found"})

