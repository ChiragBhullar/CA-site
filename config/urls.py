from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "KARS & Co — site administration"
admin.site.site_title = "KARS & Co admin"
admin.site.index_title = "Website content and enquiries"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("profile_site.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
