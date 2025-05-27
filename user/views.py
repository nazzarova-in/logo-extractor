from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken


from .serializers import RegistrationSerializer


class RegistrationAPIView(APIView):
  def post(self, request):
    serializer = RegistrationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    refresh = RefreshToken.for_user(user)
    user_data = RegistrationSerializer(user)
    return Response ({'message': user_data.data,
                      'access': str(refresh.access_token),
                      'refresh': str(refresh),
                      })
