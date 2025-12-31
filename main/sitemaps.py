from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from billing.models import BlogPost

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'weekly'

    def items(self):
        return ['landing', 'pricing', 'features', 'about', 'contact', 'blog_home', 'user_manual', 'terms_of_service', 'privacy_policy']

    def location(self, item):
        return reverse(item)

class BlogSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return BlogPost.objects.filter(status='published').order_by('-published_at')

    def lastmod(self, obj):
        return obj.updated_at
