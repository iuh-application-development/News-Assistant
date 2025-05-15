from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required
from collections import Counter
from unidecode import unidecode
import feedparser
from bs4 import BeautifulSoup
from rapidfuzz import fuzz

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
from django.views.decorators.csrf import ensure_csrf_cookie

from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .models import Favorite

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
                link = item.get('link') or item.get('guid') or item.get('url')
                if link and not link.startswith('http'):
                    link = 'https://vnexpress.net' + link
                
                description = item.get('summary', '')
                description_soup = BeautifulSoup(description, 'html.parser')
                description_text = description_soup.get_text()
                
                img_tag = description_soup.find('img')
                if img_tag and img_tag.get('src'):
                    img_src = img_tag['src']
                else:
                    img_src = "https://via.placeholder.com/300x200?text=No+Image"
                
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
        link = i.get('link') or i.get('guid') or i.get('url')
        if link and not link.startswith('http'):
            link = 'https://vnexpress.net' + link

        description = i.get('summary')
        description_soup = BeautifulSoup(description, 'html.parser')
        description_text = description_soup.get_text()

        img_tag = description_soup.find('img')
        if img_tag and img_tag.get('src'):
            img_src = img_tag['src']
        else:
            img_src = "https://via.placeholder.com/300x200?text=No+Image"

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
                link = item.get('link') or item.get('guid') or item.get('url')
                if link and not link.startswith('http'):
                    link = 'https://vnexpress.net' + link
                
                description = item.get('summary', '')
                description_soup = BeautifulSoup(description, 'html.parser')
                description_text = description_soup.get_text()
                
                img_tag = description_soup.find('img')
                if img_tag and img_tag.get('src'):
                    img_src = img_tag['src']
                else:
                    img_src = "https://via.placeholder.com/300x200?text=No+Image"
                
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
            link = i.get('link') or i.get('guid') or i.get('url')
            if link and not link.startswith('http'):
                link = 'https://vnexpress.net' + link
            
            description = i.get('summary')
            description_soup = BeautifulSoup(description, 'html.parser')
            description_text = description_soup.get_text()
            
            img_tag = description_soup.find('img')
            if img_tag and img_tag.get('src'):
                img_src = img_tag['src']
            else:
                img_src = "https://via.placeholder.com/300x200?text=No+Image"
            
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
            link = i.get('link') or i.get('guid') or i.get('url')
            if link and not link.startswith('http'):
                link = 'https://vnexpress.net' + link
            
            description = i.get('summary')
            description_soup = BeautifulSoup(description, 'html.parser')
            description_text = description_soup.get_text()
            
            img_tag = description_soup.find('img')
            if img_tag and img_tag.get('src'):
                img_src = img_tag['src']
            else:
                img_src = "https://via.placeholder.com/300x200?text=No+Image"
            
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
    html = render_to_string('home/news_items.html', {'iteam_rss': item_rss}, request=request)
    
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
            link = item.get('link') or item.get('guid') or item.get('url')
            if link and not link.startswith('http'):
                link = 'https://vnexpress.net' + link
            
            # Extract description and image
            description = item.get('summary', '')
            description_soup = BeautifulSoup(description, 'html.parser')
            description_text = description_soup.get_text()
            
            img_tag = description_soup.find('img')
            if img_tag and img_tag.get('src'):
                img_src = img_tag['src']
            else:
                img_src = "https://via.placeholder.com/300x200?text=No+Image"
            
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
    
from datetime import datetime
import feedparser
from bs4 import BeautifulSoup
from django.shortcuts import render
from unidecode import unidecode
from rapidfuzz import fuzz

def search_tech_news(request):
    query = request.GET.get('q', '').strip()
    normalized_query = unidecode(query.lower())

    rss_feeds = [
        ("VnExpress Công nghệ", "https://vnexpress.net/rss/cong-nghe.rss"),
        ("VNExpress Kinh doanh", "https://vnexpress.net/rss/kinh-doanh.rss"),
        ("VNExpress Thể Thao", "https://vnexpress.net/rss/the-thao.rss"),
        ("VNExpress Thế giới", "https://vnexpress.net/rss/the-gioi.rss"),
        ("VNExpress Thời sự", "https://vnexpress.net/rss/thoi-su.rss"),
        ("VNExpress Giải Trí", "https://vnexpress.net/rss/giai-tri.rss"),
        ("VNExpress Pháp Luật", "https://vnexpress.net/rss/phap-luat.rss"),
        ("VNExpress Giáo Dục", "https://vnexpress.net/rss/giao-duc.rss"),
        ("VNExpress Tin mới", "https://vnexpress.net/rss/tin-moi-nhat.rss"),
        ("VNExpress Sức Khỏe", "https://vnexpress.net/rss/suc-khoe.rss"),
        ("VNExpress Gia Đình", "https://vnexpress.net/rss/gia-dinh.rss"),
        ("VNExpress Xe", "https://vnexpress.net/rss/oto-xe-may.rss"),
        ("VNExpress Ý kiến", "https://vnexpress.net/rss/y-kien.rss"),
        ("VNExpress Du Lịch", "https://vnexpress.net/rss/du-lich.rss"),
        ("VNExpress Cười", "https://vnexpress.net/rss/cuoi.rss"),
        ("Báo Tin Tức Thế Giới", "https://baotintuc.vn/the-gioi.rss"),
        ("Báo Tin Tức Thời Sự", "https://baotintuc.vn/thoi-su.rss"),
        ("Báo Tin Tức Kinh Tế", "https://baotintuc.vn/kinh-te.rss"),
        ("Báo Tin Tức Xã Hội", "https://baotintuc.vn/xa-hoi.rss"),
        ("Báo Tin Tức Pháp Luật", "https://baotintuc.vn/phap-luat.rss"),
        ("Báo Tin Tức Văn Hóa", "https://baotintuc.vn/van-hoa.rss"),
        ("Báo Tin Tức Thể Thao", "https://baotintuc.vn/the-thao.rss"),
        ("Báo Tin Tức Quân Sự", "https://baotintuc.vn/quan-su.rss"),
        ("Báo Tin Tức KH-CN", "https://baotintuc.vn/khoa-hoc-cong-nghe.rss"),
        ("Báo Tin Tức Y Tế", "https://baotintuc.vn/suc-khoe.rss"),
    ]

    results = []

    if query:
        keywords = normalized_query.split()

        for source_name, feed_url in rss_feeds:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries:
                    title = entry.get('title', '')
                    description = entry.get('description', '')
                    link = entry.get('link') or entry.get('guid') or entry.get('url')
                    if link and not link.startswith('http'):
                        link = 'https://vnexpress.net' + link
                    pub_date = entry.get('published', '')

                    try:
                        pub_date = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %z').strftime('%d/%m/%Y %H:%M')
                    except:
                        pub_date = ''

                    # Chuẩn hóa để so sánh không dấu
                    norm_title = unidecode(title.lower())
                    norm_description = unidecode(description.lower())

                    # Điểm khớp
                    score = 0
                    if normalized_query in norm_title:
                        score += 20
                    elif normalized_query in norm_description:
                        score += 10

                    # Tìm kiếm từng từ
                    for word in keywords:
                        if word in norm_title:
                            score += 5
                        if word in norm_description:
                            score += 2

                    # Fuzzy match
                    score += fuzz.partial_ratio(normalized_query, norm_title) // 10
                    score += fuzz.partial_ratio(normalized_query, norm_description) // 15

                    if score >= 20:  # Ngưỡng lọc kết quả
                        soup = BeautifulSoup(description, 'html.parser')
                        img_tag = soup.find('img')
                        img_src = "https://via.placeholder.com/150"
                        if img_tag and img_tag.get('src'):
                            img_src = img_tag['src']

                        text_content = soup.get_text().strip()

                        results.append({
                            'title': title,
                            'link': link,
                            'pub_date': pub_date,
                            'description': text_content,
                            'image': img_src,
                            'source': source_name,
                            'score': score,
                        })

            except Exception as e:
                print(f"Lỗi khi đọc RSS từ {feed_url}: {str(e)}")

        # Sắp xếp theo điểm giảm dần
        results.sort(key=lambda x: x['score'], reverse=True)

    context = {
        'query': query,
        'results': results,
        'results_count': len(results),
    }
    return render(request, 'search_rss/tech_results.html', context)

import json
from .models import Favorite
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse

@require_http_methods(["POST"])
@ensure_csrf_cookie
def add_to_favorites(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Vui lòng đăng nhập để thêm vào yêu thích'}, status=401)

    if request.headers.get('x-requested-with') != 'XMLHttpRequest':
        return JsonResponse({'error': 'Yêu cầu không hợp lệ'}, status=400)

    try:
        data = json.loads(request.body)
        title = data.get('title')
        link = data.get('link')

        if not title or not link:
            return JsonResponse({'error': 'Thiếu thông tin bắt buộc'}, status=400)

        # Check if article already exists in favorites
        if Favorite.objects.filter(user=request.user, link=link).exists():
            return JsonResponse({'message': 'Mục này đã có trong yêu thích của bạn'}, status=200)

        # Create new favorite
        favorite = Favorite.objects.create(
            user=request.user,
            title=title,
            link=link,
            image=data.get('image', ''),
            description=data.get('description', ''),
            source=data.get('source', 'Unknown'),
            pub_date=data.get('pub_date', '')
        )
        return JsonResponse({
            'message': 'Đã thêm vào mục yêu thích thành công',
            'favorite_id': favorite.id
        }, status=201)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Dữ liệu không hợp lệ'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Lỗi hệ thống: {str(e)}'}, status=500)

@login_required
def favorites_view(request):
    favorites = Favorite.objects.filter(user=request.user).order_by('-id')
    return render(request, 'favourite/favorites.html', {'favorites': favorites})

@login_required
@require_POST
def remove_from_favorites(request):
    if request.headers.get('x-requested-with') != 'XMLHttpRequest':
        return JsonResponse({'error': 'Yêu cầu không hợp lệ'}, status=400)
    
    try:
        data = json.loads(request.body)
        link = data.get('link')
        
        if not link:
            return JsonResponse({'error': 'Thiếu thông tin bắt buộc'}, status=400)
        
        # Find and delete the favorite
        result = Favorite.objects.filter(user=request.user, link=link).delete()
        
        if result[0] == 0:  # No records were deleted
            return JsonResponse({'error': 'Không tìm thấy mục yêu thích'}, status=404)
            
        return JsonResponse({
            'message': 'Đã xóa khỏi yêu thích thành công',
            'status': 'success'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Dữ liệu không hợp lệ'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Lỗi hệ thống: {str(e)}'}, status=500)

@login_required
def recommended_news_view(request):
    # Get user's favorites
    user_favorites = Favorite.objects.filter(user=request.user)
    
    if not user_favorites:
        return render(request, 'home/recommended_news.html', {
            'recommended_news': [],
            'message': 'Hãy thêm một số tin tức vào mục yêu thích để nhận đề xuất!'
        })
    
    # Extract keywords from favorite titles and descriptions
    keywords = []
    sources = []
    for favorite in user_favorites:
        # Add source to track user's preferred news sources
        sources.append(favorite.source)
        
        # Extract keywords from title and description
        title_words = unidecode(favorite.title.lower()).split()
        desc_words = unidecode(favorite.description.lower()).split() if favorite.description else []
        
        # Add important words (excluding common words)
        common_words = {'và', 'của', 'có', 'là', 'để', 'trong', 'với', 'các', 'những', 'được', 'về', 'từ', 'theo', 'tại', 'đã'}
        keywords.extend([word for word in title_words if len(word) > 3 and word not in common_words])
        keywords.extend([word for word in desc_words if len(word) > 3 and word not in common_words])
    
    # Get most common keywords and sources
    keyword_freq = Counter(keywords)
    top_keywords = [k for k, v in keyword_freq.most_common(10)]
    preferred_sources = Counter(sources).most_common(3)
    
    # RSS feeds from preferred sources
    rss_feeds = [
        ("VnExpress Công nghệ", "https://vnexpress.net/rss/cong-nghe.rss"),
        ("VnExpress Kinh doanh", "https://vnexpress.net/rss/kinh-doanh.rss"),
        ("VnExpress Thể Thao", "https://vnexpress.net/rss/the-thao.rss"),
        ("VnExpress Thế giới", "https://vnexpress.net/rss/the-gioi.rss"),
        ("VnExpress Thời sự", "https://vnexpress.net/rss/thoi-su.rss"),
        ("Báo Tin Tức Thế Giới", "https://baotintuc.vn/the-gioi.rss"),
        ("Báo Tin Tức Thời Sự", "https://baotintuc.vn/thoi-su.rss"),
        ("Báo Tin Tức Kinh Tế", "https://baotintuc.vn/kinh-te.rss"),
    ]
    
    recommended_news = []
    existing_links = {fav.link for fav in user_favorites}
    
    for source_name, feed_url in rss_feeds:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                title = entry.get('title', '')
                description = entry.get('description', '')
                link = entry.get('link') or entry.get('guid') or entry.get('url')
                if link and not link.startswith('http'):
                    link = 'https://vnexpress.net' + link
                
                # Skip if already in favorites
                if link in existing_links:
                    continue
                
                # Calculate relevance score
                score = 0
                norm_title = unidecode(title.lower())
                norm_description = unidecode(description.lower())
                
                # Score based on keywords
                for keyword in top_keywords:
                    if keyword in norm_title:
                        score += 10
                    if keyword in norm_description:
                        score += 5
                
                # Bonus score for preferred sources
                for preferred_source, _ in preferred_sources:
                    if source_name == preferred_source:
                        score += 15
                        break
                
                if score > 0:
                    soup = BeautifulSoup(description, 'html.parser')
                    img_tag = soup.find('img')
                    img_src = img_tag['src'] if img_tag and img_tag.get('src') else "https://via.placeholder.com/150"
                    text_content = soup.get_text().strip()
                    
                    pub_date = entry.get('published', '')
                    try:
                        from datetime import datetime
                        pub_date = datetime.strptime(pub_date, '%a, %d %b %Y %H:%M:%S %z').strftime('%d/%m/%Y %H:%M')
                    except:
                        pub_date = ''
                    
                    recommended_news.append({
                        'title': title,
                        'link': link,
                        'description': text_content[:200] + '...' if len(text_content) > 200 else text_content,
                        'image': img_src,
                        'source': source_name,
                        'pub_date': pub_date,
                        'score': score
                    })
        
        except Exception as e:
            print(f"Error fetching RSS from {feed_url}: {str(e)}")
    
    # Sort by relevance score and limit to top 20
    recommended_news.sort(key=lambda x: x['score'], reverse=True)
    recommended_news = recommended_news[:20]
    
    return render(request, 'home/recommended_news.html', {
        'recommended_news': recommended_news,
        'top_keywords': top_keywords[:5]  # Show top 5 keywords for transparency
    })
