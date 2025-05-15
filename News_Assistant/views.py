from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
from .models import FavoriteArticle
import feedparser
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import re

@login_required
@require_POST
def remove_from_favorites(request):
    if not request.is_ajax():
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
    try:
        data = json.loads(request.body)
        article_link = data.get('link')
        
        if not article_link:
            return JsonResponse({'error': 'Link is required'}, status=400)
        
        # Tìm và xóa bài viết khỏi favorites
        FavoriteArticle.objects.filter(user=request.user, link=article_link).delete()
        
        return JsonResponse({
            'message': 'Article removed from favorites successfully',
            'status': 'success'
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500) 