from django.contrib import admin
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from .define import *

from .models import Category, Article, Feed, Author, CategoryFeed, Contact

class CategoryAdmin (admin.ModelAdmin):
    list_display = ('name', 'status', 'is_homepage', 'layout', 'ordering')
    #prepopulated_fields = {'slug':('name',)} #tạo  ra mối quan hệ giữa 2 cái này để nó chạy tự động
    list_filter = ["is_homepage","status","layout"]
    search_fields = ['name']
    
    class Media:
        js = ADMIN_SRC_JS
        css = ADMIN_SRC_CSS

class ArticleAdmin (admin.ModelAdmin):
    list_display = ('name', 'author', 'category', 'status', 'ordering')
    #prepopulated_fields = {'slug':('name',)} #tạo  ra mối quan hệ giữa 2 cái này để nó chạy tự động
    list_filter = ["status", "special", "category", "author"]
    search_fields = ['name', 'content']

    class Media:
        js = ADMIN_SRC_JS
        css = ADMIN_SRC_CSS

class FeedAdmin (admin.ModelAdmin):
    list_display = ('name', 'status', 'ordering')
    #prepopulated_fields = {'slug':('name',)} #tạo  ra mối quan hệ giữa 2 cái này để nó chạy tự động
    list_filter = ["status"]
    search_fields = ['name']

    class Media:
        js = ADMIN_SRC_JS

# Thêm AuthorAdmin mới
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'status')
    list_filter = ["status"]
    search_fields = ['name', 'email']
    
    class Media:
        js = ADMIN_SRC_JS
        css = ADMIN_SRC_CSS
# thêm CategoryFeed cho RSS_Danh_Muc
class CategoryFeedAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'status', 'ordering')
    list_filter = ('status', 'category')
    search_fields = ('name',)

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at', 'status')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Thông tin người gửi', {
            'fields': ('name', 'email', 'created_at')
        }),
        ('Nội dung tin nhắn', {
            'fields': ('subject', 'message')
        }),
        ('Phản hồi', {
            'fields': ('status', 'reply', 'replied_at')
        }),
    )

    def save_model(self, request, obj, form, change):
        if change and 'reply' in form.changed_data:  # Nếu phản hồi được thay đổi
            obj.status = 'replied'
            obj.replied_at = timezone.now()
            
            # Gửi email phản hồi
            email_subject = f'[RAUCON_VN] Phản hồi cho tin nhắn: {obj.subject}'
            email_message = f"""
Xin chào {obj.name},

Cảm ơn bạn đã liên hệ với RAUCON_VN. Dưới đây là phản hồi cho tin nhắn của bạn:

Tin nhắn của bạn:
{obj.message}

Phản hồi của chúng tôi:
{obj.reply}

Trân trọng,
Đội ngũ RAUCON_VN
            """
            
            try:
                send_mail(
                    subject=email_subject,
                    message=email_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[obj.email],
                    fail_silently=False,
                )
            except Exception as e:
                self.message_user(request, f"Không thể gửi email: {str(e)}", level='ERROR')
            else:
                self.message_user(request, "Phản hồi đã được gửi qua email thành công!", level='SUCCESS')
        
        super().save_model(request, obj, form, change)

admin.site.register(Category, CategoryAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Feed, FeedAdmin)
admin.site.register(Author, AuthorAdmin)  
admin.site.register(CategoryFeed, CategoryFeedAdmin)
# chỉnh tên trang admin thay vì để mặt định là Django
admin.site.site_header = ADMIN_HEADER_NAME
admin.site.site_title = ADMIN_HEADER_NAME
admin.site.index_title = 'Dashboard'