from django.urls import path

from . import views

app_name = 'pages'

urlpatterns = [
    path('about/', views.AboutPage.as_view(), name='about'),
    path('venue/', views.RulesPage.as_view(), name='venue'),
]
