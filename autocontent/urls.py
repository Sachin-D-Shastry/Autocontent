from django.urls import path, include
from accounts import views as accounts_views
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponseNotFound

urlpatterns = [
    path('admin/', lambda request: HttpResponseNotFound("Page not found")),  # Disable default Django admin
    path('', accounts_views.landing_page_view, name='main_home'),
    path('', include('accounts.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
