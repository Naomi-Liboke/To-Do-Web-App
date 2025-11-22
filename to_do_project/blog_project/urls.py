from django.contrib import admin
from django.urls import path, include
# Import settings and static for media handling
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # Include your app's URLs
    path('', include('to_do_app.urls')), 
]

# **Add this block at the end of your project's urls.py**
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)