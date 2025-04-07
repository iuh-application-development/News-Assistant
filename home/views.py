from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test

#news rss
from django.shortcuts import render, redirect
import feedparser
from bs4 import BeautifulSoup
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib import messages
#news rss

from .models import Category, Article, Feed, Author, CategoryFeed, Contact # Import model Category, Article và Feed

# ajax load more news
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods
from django.utils import timezone
import json

from django.core.mail import send_mail
from django.http import HttpResponse

def is_admin(user):
    return user.is_staff

def home_view(request):
    selected_feed_slug = request.GET.get('feed', None)
    selected_category_slug = request.GET.get('category', None)
    default_rss_feed_url = 'https://vnexpress.net/rss/tin-moi-nhat.rss'
    rss_feed_url = default_rss_feed_url
    source_name = "VNExpress"  # Default source name

    # Luôn lấy tất cả categories đã publish
    categories = Category.objects.filter(status='published').order_by('ordering')
    feeds = Feed.objects.filter(status='published').order_by('ordering') if request.user.is_authenticated else None

    if selected_feed_slug:
        selected_feed = get_object_or_404(Feed, slug=selected_feed_slug, status='published')
        rss_feed_url = selected_feed.link
        source_name = selected_feed.name
    elif selected_category_slug:
        # Get the category and its feeds
        category = get_object_or_404(Category, slug=selected_category_slug, status='published')
        category_feeds = CategoryFeed.objects.filter(category=category, status='published')
        
        iteam_rss = []
        # Get items from all category feeds
        for cat_feed in category_feeds:
            feed = feedparser.parse(cat_feed.rss_url)
            
            for item in feed.entries[:5]:  # Limit to 5 items per feed
                title = item.get('title')
                pub_date = item.get('published')
                link = item.get('link')
                
                description = item.get('summary', '')
                description_soup = BeautifulSoup(description, 'html.parser')
                description_text = description_soup.get_text()
                
                img_tag = description_soup.find('img')
                img_src = "https://yt3.googleusercontent.com/BxWJ7TciIXwmJXFOKIpG9z-9WhjkYzuEw7_DX6gMsRvIEcYnxgPIfXQLzdZ4PkJMSt-YuIVRMcI=s900-c-k-c0x00ffffff-no-rj"
                if img_tag:
                    img_src = img_tag['src']
                
                feed_item = {
                    'title': title,
                    'pub_date': pub_date,
                    'link': link,
                    'description': description_text,
                    'image': img_src,
                    'source': cat_feed.name
                }
                iteam_rss.append(feed_item)
        
        articles = Article.objects.filter(status='published').order_by('-publish_date')[:5]
        
        context = {
            'iteam_rss': iteam_rss,
            'categories': categories,
            'feeds': feeds,
            'articles': articles,
            'selected_category_slug': selected_category_slug,
        }
        return render(request, 'home/home.html', context)
    
    # Original code for default and feed-specific views
    feed = feedparser.parse(rss_feed_url)
    iteam_rss = []
    for i in feed.entries:
        title = i.get('title')
        pub_date = i.get('published')
        link = i.get('link')

        description = i.get('summary')
        description_soup = BeautifulSoup(description, 'html.parser')
        description_text = description_soup.get_text()

        img_tag = description_soup.find('img')
        img_src = "https://yt3.googleusercontent.com/BxWJ7TciIXwmJXFOKIpG9z-9WhjkYzuEw7_DX6gMsRvIEcYnxgPIfXQLzdZ4PkJMSt-YuIVRMcI=s900-c-k-c0x00ffffff-no-rj"
        if img_tag:
            img_src = img_tag['src']

        iteam = {
            'title': title,
            'pub_date': pub_date,
            'link': link,
            'description': description_text,
            'image': img_src,
            'source': source_name
        }
        iteam_rss.append(iteam)

    articles = Article.objects.filter(status='published').order_by('-publish_date')[:5]

    context = {
        'iteam_rss': iteam_rss,
        'categories': categories,
        'feeds': feeds,
        'articles': articles,
    }
    return render(request, 'home/home.html', context)


def category_view(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug, status='published')
    articles = Article.objects.filter(category=category, status='published').order_by('-publish_date')

    context = {
        'category': category,
        'articles': articles,
    }
    return render(request, 'home/category_detail.html', context)


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        admin_login = request.POST.get('admin_login', False)

        user = authenticate(username=username, password=password)
        if user:
            if admin_login and not user.is_staff:
                messages.error(request, "This account is not an administrator account!")
                return render(request, 'home/login.html')
            auth_login(request, user)
            messages.success(request, "Successfully logged in!")
            if admin_login and user.is_staff:
                return redirect('/admin/')
            return redirect('home')
        messages.error(request, "Invalid credentials!")
    return render(request, 'home/login.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password1']
        confirm_password = request.POST['password2']

        if password != confirm_password:
            messages.error(request, "Passwords don't match!")
            return render(request, 'home/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return render(request, 'home/register.html')

        user = User.objects.create_user(username=username, email=email)
        user.set_password(password)
        user.save()
        messages.success(request, "Registration successful! Please login.")
        return redirect('login')
    return render(request, 'home/register.html')

def logout_view(request):
    auth_logout(request)
    messages.success(request, "Successfully logged out!")
    return redirect('home')

# ajax load more news
def load_more_news(request):
    page = int(request.GET.get('page', 1))
    selected_feed_slug = request.GET.get('feed', None)
    selected_category_slug = request.GET.get('category', None)
    items_per_page = 6  # Số lượng tin tức mỗi trang
    
    # Tính vị trí bắt đầu và kết thúc
    start = (page - 1) * items_per_page
    end = page * items_per_page
    
    item_rss = []
    
    if selected_category_slug:
        # Load more for category RSS feeds
        category = get_object_or_404(Category, slug=selected_category_slug, status='published')
        category_feeds = CategoryFeed.objects.filter(category=category, status='published')
        
        all_items = []
        for cat_feed in category_feeds:
            feed = feedparser.parse(cat_feed.rss_url)
            
            for item in feed.entries:
                title = item.get('title')
                pub_date = item.get('published')
                link = item.get('link')
                
                description = item.get('summary', '')
                description_soup = BeautifulSoup(description, 'html.parser')
                description_text = description_soup.get_text()
                
                img_tag = description_soup.find('img')
                img_src = "https://yt3.googleusercontent.com/BxWJ7TciIXwmJXFOKIpG9z-9WhjkYzuEw7_DX6gMsRvIEcYnxgPIfXQLzdZ4PkJMSt-YuIVRMcI=s900-c-k-c0x00ffffff-no-rj"
                if img_tag:
                    img_src = img_tag['src']
                
                feed_item = {
                    'title': title,
                    'pub_date': pub_date,
                    'link': link,
                    'description': description_text,
                    'image': img_src,
                    'source': cat_feed.name
                }
                all_items.append(feed_item)
        
        # Get items for current page
        item_rss = all_items[start:end]
        has_more = len(all_items) > end
        
    elif selected_feed_slug:
        # Load more for specific feed
        selected_feed = get_object_or_404(Feed, slug=selected_feed_slug, status='published')
        feed = feedparser.parse(selected_feed.link)
        all_items = feed.entries
        
        # Get items for current page
        page_items = all_items[start:end]
        
        for i in page_items:
            title = i.get('title')
            pub_date = i.get('published')
            link = i.get('link')
            
            description = i.get('summary')
            description_soup = BeautifulSoup(description, 'html.parser')
            description_text = description_soup.get_text()
            
            img_tag = description_soup.find('img')
            img_src = "https://yt3.googleusercontent.com/BxWJ7TciIXwmJXFOKIpG9z-9WhjkYzuEw7_DX6gMsRvIEcYnxgPIfXQLzdZ4PkJMSt-YuIVRMcI=s900-c-k-c0x00ffffff-no-rj"
            if img_tag:
                img_src = img_tag['src']
            
            item = {
                'title': title,
                'pub_date': pub_date,
                'link': link,
                'description': description_text,
                'image': img_src,
                'source': selected_feed.name
            }
            item_rss.append(item)
        
        has_more = len(all_items) > end
        
    else:
        # Load more for default feed (VnExpress)
        default_rss_feed_url = 'https://vnexpress.net/rss/tin-moi-nhat.rss'
        feed = feedparser.parse(default_rss_feed_url)
        all_items = feed.entries
        
        # Get items for current page
        page_items = all_items[start:end]
        
        for i in page_items:
            title = i.get('title')
            pub_date = i.get('published')
            link = i.get('link')
            
            description = i.get('summary')
            description_soup = BeautifulSoup(description, 'html.parser')
            description_text = description_soup.get_text()
            
            img_tag = description_soup.find('img')
            img_src = "https://yt3.googleusercontent.com/BxWJ7TciIXwmJXFOKIpG9z-9WhjkYzuEw7_DX6gMsRvIEcYnxgPIfXQLzdZ4PkJMSt-YuIVRMcI=s900-c-k-c0x00ffffff-no-rj"
            if img_tag:
                img_src = img_tag['src']
            
            item = {
                'title': title,
                'pub_date': pub_date,
                'link': link,
                'description': description_text,
                'image': img_src,
                'source': 'VNExpress'
            }
            item_rss.append(item)
        
        has_more = len(all_items) > end
    
    # Tạo HTML từ các items
    html = render_to_string('home/news_items.html', {'iteam_rss': item_rss})
    
    return JsonResponse({
        'html': html,
        'has_more': has_more
    })


def author_view(request, author_slug):
    # Lấy thông tin tác giả
    author = get_object_or_404(Author, slug=author_slug, status='published')
    
    # Lấy các bài viết của tác giả
    articles = Article.objects.filter(author=author, status='published').order_by('-publish_date')
    
    context = {
        'author': author,
        'articles': articles,
    }
    
    return render(request, 'home/author_detail.html', context)

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    articles = Article.objects.filter(category=category, status='published').order_by('-publish_date')
    
    # Get RSS feeds for this category
    category_feeds = CategoryFeed.objects.filter(category=category, status='published')
    feed_items = []
    
    # Process each RSS feed
    for cat_feed in category_feeds:
        feed = feedparser.parse(cat_feed.rss_url)
        
        for item in feed.entries[:5]:  # Limit to 5 items per feed
            title = item.get('title')
            pub_date = item.get('published')
            link = item.get('link')
            
            # Extract description and image
            description = item.get('summary', '')
            description_soup = BeautifulSoup(description, 'html.parser')
            description_text = description_soup.get_text()
            
            img_tag = description_soup.find('img')
            img_src = "https://yt3.googleusercontent.com/BxWJ7TciIXwmJXFOKIpG9z-9WhjkYzuEw7_DX6gMsRvIEcYnxgPIfXQLzdZ4PkJMSt-YuIVRMcI=s900-c-k-c0x00ffffff-no-rj"
            if img_tag:
                img_src = img_tag['src']
            
            feed_item = {
                'title': title,
                'pub_date': pub_date,
                'link': link,
                'description': description_text[:100] + '...' if len(description_text) > 100 else description_text,
                'image': img_src,
                'source': cat_feed.name
            }
            feed_items.append(feed_item)
    
    context = {
        'category': category,
        'articles': articles,
        'category_feeds': category_feeds,
        'feed_items': feed_items
    }
    
    return render(request, 'home/category_detail.html', context)

def about_view(request):
    return render(request, 'home/about.html')

@require_http_methods(["GET", "POST"])
def contact_view(request):
    if request.method == "POST":
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                data = json.loads(request.body)
                contact = Contact.objects.create(
                    name=data.get('name'),
                    email=data.get('email'),
                    subject=data.get('subject'),
                    message=data.get('message')
                )
                return JsonResponse({
                    'status': 'success',
                    'message': 'Cảm ơn bạn đã liên hệ. Chúng tôi sẽ phản hồi sớm nhất có thể.',
                    'contact_id': contact.id
                })
            except Exception as e:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Có lỗi xảy ra. Vui lòng thử lại sau.'
                })
    return render(request, 'home/contact.html')

@require_http_methods(["GET"])
def check_reply_status(request, contact_id):
    try:
        contact = Contact.objects.get(id=contact_id)
        data = {
            'status': contact.status,
            'has_reply': bool(contact.reply),
            'reply': contact.reply if contact.reply else None,
            'replied_at': contact.replied_at.strftime("%d/%m/%Y %H:%M") if contact.replied_at else None
        }
        return JsonResponse(data)
    except Contact.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Không tìm thấy tin nhắn'
        })

def test_email(request):
    try:
        result = send_mail(
            'Test Email',
            'This is a test email from Django',
            'RAUCON_VN News <phantonbasang@gmail.com>',
            ['phantonbasang@gmail.com'],
            fail_silently=False,
        )
        return HttpResponse(f"Email sent successfully! Result: {result}")
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return HttpResponse(f"Failed to send email. Error: {str(e)}\n\nDetails:\n{error_details}")