from django.contrib import admin
from django.urls import path

from tests.views import DownloadUsers

admin.autodiscover()

urlpatterns = [
    path("admin/", admin.site.urls),
    path("downloads/users.csv", DownloadUsers.as_view()),
]
