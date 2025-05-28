from rest_framework import serializers
from .models import Logo

class LogoSerializer(serializers.ModelSerializer):
    image_url = serializers.ImageField(source='image', use_url=True)

    class Meta:
        model = Logo
        fields = [
            'id',
            'title',
            'path',
            'original_url',
            'source',
            'website',
            'version',
            'created',
            'image_url'
        ]
        read_only_fields = ['id', 'created']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None
