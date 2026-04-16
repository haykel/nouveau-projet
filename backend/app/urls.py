from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from app.views import hello, health

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/hello/", hello),
    path("api/", include("app.stocks.urls")),
    path("health/", health),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
