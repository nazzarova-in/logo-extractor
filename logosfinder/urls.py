from rest_framework.routers import DefaultRouter
from .views import LogosViewSet

router = DefaultRouter()
router.register(r'logo', LogosViewSet, basename='logo')

urlpatterns = router.urls
