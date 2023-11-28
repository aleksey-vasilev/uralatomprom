from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

from blog.views import ProfileCreateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls', namespace='blog')),
    path('pages/', include('pages.urls', namespace='pages')),
    path('auth/', include('django.contrib.auth.urls')),
    path('auth/registration/',
         ProfileCreateView.as_view(),
         name='registration',),
    path('captcha/', include('captcha.urls')),
]

settings.DEBUG = True
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
settings.DEBUG = False

handler404 = 'pages.views.page_not_found'
handler500 = 'pages.views.internal_server_error'
