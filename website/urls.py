from rest_framework.routers import DefaultRouter
from .views import WebSiteURLViewSet

router = DefaultRouter()
router.register(r'website', WebSiteURLViewSet, basename='website')

urlpatterns = router.urls
