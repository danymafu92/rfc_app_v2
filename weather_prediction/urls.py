"""Root URL configuration for the Django project.

This module mounts the `api` app under `/api/` and the Django admin.
During local development (DEBUG=True) it also serves static/media files
from the frontend build output.
"""


from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
# from django.views.generic import RedirectView # Removed, as we're no longer redirecting
# To handle a proper homepage/dashboard, you'll need to define a view, e.g., in api/views.py.
# For now, we'll assume a generic view is needed. 
# from api.views import home_view # You would typically import your home view here


from django.views.generic import RedirectView # <--- NEW IMPORT

from django.views.generic import TemplateView # <--- NEW IMPORT for the placeholder view


    # **FIX:** Replaced the non-existent path('', include('web.urls')) 
    # with a direct path to a TemplateView. This allows the server to load 
    # without the 'web' app dependency, and serves as your main entry point.
   
urlpatterns = [
    # **FIX:** Changed the root path to point to a future UI endpoint instead of redirecting to /api/.
    # You will need to define a view (e.g., 'home_view' in 'api/views.py' or a separate app)
    # that renders your HTML/SPA dashboard/login page.
    #path('', RedirectView.as_view(url='api/', permanent=True)), # Original redirect
    #path('', include('web.urls')), # Assuming a 'web' app handles the UI, or use:
    # path('', home_view, name='home'), 
     path(
        '',
        TemplateView.as_view(template_name='api/index.html'), 
        name='home'
    ),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)



