from django.urls import path

from . import site_views

# Mounted at the site root by core_platform/urls.py.
# The REST API stays at /api/ and the admin site at /admin/.
urlpatterns = [
    path('', site_views.home, name='home'),
    path('book/', site_views.book, name='book'),
    path('book/confirmed/<int:booking_id>/', site_views.booking_confirmed,
         name='booking_confirmed'),
]
