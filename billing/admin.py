from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import (
    Plan, Subscription, Payment, PricingPlan, PlanFeature, FAQ, 
    PaymentGatewayConfig, LegalDocument, BlogCategory, BlogTag, BlogPost,
    FeatureCategory, FeatureItem, LeadershipMember
)

@admin.register(Plan)
class PlanAdmin(ModelAdmin):
    list_display = ('name', 'price', 'max_branches', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)

@admin.register(Subscription)
class SubscriptionAdmin(ModelAdmin):
    list_display = ('tenant', 'plan', 'status', 'current_period_end')
    list_filter = ('status', 'plan')
    search_fields = ('tenant__name', 'stripe_subscription_id')

@admin.register(Payment)
class PaymentAdmin(ModelAdmin):
    list_display = ('subscription', 'amount', 'status', 'date')
    list_filter = ('status',)
    date_hierarchy = 'date'

class PlanFeatureInline(TabularInline):
    model = PlanFeature
    extra = 3

@admin.register(PricingPlan)
class PricingPlanAdmin(ModelAdmin):
    list_display = ('name', 'price_monthly', 'price_yearly', 'is_popular', 'order')
    list_editable = ('order', 'is_popular', 'price_monthly', 'price_yearly')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [PlanFeatureInline]

@admin.register(FAQ)
class FAQAdmin(ModelAdmin):
    list_display = ('question', 'order', 'is_published')
    list_editable = ('order', 'is_published')
    search_fields = ('question', 'answer')

@admin.register(PaymentGatewayConfig)
class PaymentGatewayConfigAdmin(ModelAdmin):
    list_display = ('name', 'slug', 'is_active')
    list_editable = ('is_active',)
    search_fields = ('name', 'slug')

@admin.register(LegalDocument)
class LegalDocumentAdmin(ModelAdmin):
    list_display = ('title', 'slug', 'is_published', 'last_updated')
    list_editable = ('is_published',)
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'content')

@admin.register(BlogCategory)
class BlogCategoryAdmin(ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(BlogTag)
class BlogTagAdmin(ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(BlogPost)
class BlogPostAdmin(ModelAdmin):
    list_display = ('title', 'author', 'category', 'status', 'is_featured', 'published_at')
    list_filter = ('status', 'category', 'is_featured', 'published_at')
    list_editable = ('status', 'is_featured')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'content', 'excerpt')
    filter_horizontal = ('tags',)
    date_hierarchy = 'published_at'

@admin.register(FeatureCategory)
class FeatureCategoryAdmin(ModelAdmin):
    list_display = ('name', 'icon', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    search_fields = ('name',)

@admin.register(FeatureItem)
class FeatureItemAdmin(ModelAdmin):
    list_display = ('title', 'category', 'icon', 'order', 'is_active')
    list_filter = ('category', 'is_active')
    list_editable = ('order', 'is_active')
    search_fields = ('title', 'desc')
@admin.register(LeadershipMember)
class LeadershipMemberAdmin(ModelAdmin):
    list_display = ('name', 'role', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    search_fields = ('name', 'role', 'bio')
