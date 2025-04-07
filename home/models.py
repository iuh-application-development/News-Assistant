from django.db import models
from tinymce.models import HTMLField

from .helpers import *
from .custom_field import *
from .define import * 
from django.contrib.auth.models import User

# Model Author mới
class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    bio = HTMLField(blank=True, null=True)
    avatar = models.ImageField(upload_to='news_app/image/author/', blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    facebook = models.URLField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=APP_VALUE_STATUS_CHOICES, default=APP_VALUE_STATUS_DEFAULT)
    
    class Meta:
        verbose_name_plural = "Authors"
    
    def __str__(self):
        return self.name

class Category (models.Model):
    
    # Tạo các trường
    name = models.CharField(unique=True, max_length=100)
    slug = models.CharField(unique=True, max_length=100)
    is_homepage = CustomBooleanField()
    layout = models.CharField(max_length=10, choices=APP_VALUE_LAYOUT_CHOICES, default=APP_VALUE_LAYOUT_DEFAULT) #define.py
    status = models.CharField(max_length=10, choices=APP_VALUE_STATUS_CHOICES, default=APP_VALUE_STATUS_DEFAULT) # nháp #define.py
    ordering = models.IntegerField(default=0)
    
    
    # chỉnh tên của các models
    class Meta:
        verbose_name_plural = TABLE_CATEGORY_SHOW #define.py

    def __str__(self):
        return self.name
    
# RSS_DANH_MUC models.py
class CategoryFeed(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='category_feeds')
    name = models.CharField(max_length=100)
    slug = models.CharField (unique=True, max_length= 100)
    rss_url = models.URLField()
    status = models.CharField(max_length=10, choices=APP_VALUE_STATUS_CHOICES, default=APP_VALUE_STATUS_DEFAULT)
    ordering = models.IntegerField(default=0)
    
    class Meta:
        verbose_name_plural = "Category Feeds"
    
    def __str__(self):
        return f"{self.category.name} - {self.name}"
    

class Article(models.Model):
    # Các trường hiện có
    name = models.CharField(unique=True, max_length=100)
    slug = models.CharField(unique=True, max_length=100)
    status = models.CharField(max_length=10, choices=APP_VALUE_STATUS_CHOICES, default=APP_VALUE_STATUS_DEFAULT)
    ordering = models.IntegerField(default=0)
    special = CustomBooleanField()
    publish_date = models.DateTimeField()
    content = HTMLField()
    image = models.ImageField(upload_to='images/', null=False, default='default.jpg')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='articles')
    
    # Thêm trường author
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True, blank=True, related_name='articles')
    
    class Meta:
        verbose_name_plural = TABLE_ARTICLE_SHOW

    def __str__(self):
        return self.name


class Feed (models.Model):
   
    # Tạo các trường
    name = models.CharField (unique=True, max_length= 100)
    slug = models.CharField (unique=True, max_length= 100)
    status = models.CharField (max_length=10, choices=APP_VALUE_STATUS_CHOICES, default=APP_VALUE_STATUS_DEFAULT) # nháp
    ordering =models.IntegerField (default=0)
    link = models.CharField (max_length=250)

    

class Meta:
    verbose_name_plural = TABLE_FEED_SHOW #define.py

def __str__(self):
    return self.name
    

class Contact(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Đang chờ'),
        ('replied', 'Đã phản hồi'),
    ]
    
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reply = models.TextField(blank=True, null=True)
    replied_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Liên hệ'
        verbose_name_plural = 'Liên hệ'

    def __str__(self):
        return f"{self.name} - {self.subject}"

class Meta:
    verbose_name_plural = TABLE_FEED_SHOW #define.py

def __str__(self):
    return self.name
    
