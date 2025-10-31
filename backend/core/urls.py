from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from apps.api.views import HiddenTokenObtainPairView, HiddenTokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

from apps.api.router import route

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('api/', include(route.urls)),
    path('api/', include('apps.api.urls')),

    path('api/token/', HiddenTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', HiddenTokenRefreshView.as_view(), name='token_refresh'),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
] 

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
