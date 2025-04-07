# urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('category/<slug:category_slug>/', views.category_view, name='category_detail'), # URL cho trang danh mục
    # Thêm URL pattern mới cho Ajax Load More
    path('load-more-news/', views.load_more_news, name='load_more_news'),
    # URL pattern mới cho trang tác giả
    path('author/<slug:author_slug>/', views.author_view, name='author_detail'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('check-reply-status/<int:contact_id>/', views.check_reply_status, name='check_reply_status'),
    path('test-email/', views.test_email, name='test_email'),
]
