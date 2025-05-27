from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('add-to-favorites/', views.add_to_favorites, name='add_to_favorites'),
    path('remove-from-favorites/', views.remove_from_favorites, name='remove_from_favorites'),
    path('favorites/', views.favorites, name='favorites'),
    path('search/', views.search_rss, name='search_rss'),
    path('search/tech/', views.search_tech, name='search_tech'),
] 