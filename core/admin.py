from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Category, News, Event, Project, 
    Activity, MediaItem, Menu, MenuItem
)

User = get_user_model()

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

class CategoryFilter(admin.SimpleListFilter):
    title = 'category'
    parameter_name = 'category'

    def lookups(self, request, model_admin):
        return [(c.id, c.name) for c in Category.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(categories__id=self.value())
        return queryset

class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'author' in self.fields:
            # Order users by first name then last name
            self.fields['author'].queryset = User.objects.filter(is_active=True).order_by('first_name', 'last_name')
            # Set the current user as the default author
            if not self.instance.pk and 'author' not in self.data:
                self.initial['author'] = self.current_user.id if hasattr(self, 'current_user') else None

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    form = NewsForm
    list_display = ('title', 'status', 'publish_date', 'is_featured', 'author_display', 'display_categories')
    list_filter = ('status', 'publish_date', 'is_featured', CategoryFilter)
    search_fields = ('title', 'content', 'excerpt', 'author__username', 'author__first_name', 'author__last_name')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'publish_date'
    filter_horizontal = ('categories',)
    autocomplete_fields = ('author',)
    raw_id_fields = ('author',)
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.current_user = request.user
        return form
    raw_id_fields = ('author',)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'author':
            kwargs['queryset'] = get_user_model().objects.filter(is_staff=True).order_by('email')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def author_display(self, obj):
        if obj.author:
            name = obj.author.get_full_name() or obj.author.email.split('@')[0]
            return f"{name} ({obj.author.email})"
        return "-"
    author_display.short_description = 'Author'
    author_display.admin_order_field = 'author__email'
    
    def display_categories(self, obj):
        return ", ".join([c.name for c in obj.categories.all()])
    display_categories.short_description = 'Categories'

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add any custom form initialization here

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    form = EventForm
    list_display = ('title', 'start_date', 'end_date', 'status', 'status_badge', 'location', 'is_upcoming', 'is_ongoing')
    list_filter = ('status', 'start_date', 'end_date')
    search_fields = ('title', 'description', 'location')
    date_hierarchy = 'start_date'
    list_editable = ('status',)
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = [
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'content', 'featured_image')
        }),
        ('Event Details', {
            'fields': ('start_date', 'end_date', 'location', 'registration_url')
        }),
        ('Status', {
            'fields': ('status', 'is_featured')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    ]
    
    def status_badge(self, obj):
        status_colors = {
            'upcoming': 'info',
            'ongoing': 'success',
            'completed': 'secondary'
        }
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            status_colors.get(obj.status, 'secondary'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def is_upcoming(self, obj):
        return obj.is_upcoming
    is_upcoming.boolean = True
    is_upcoming.short_description = 'Upcoming?'
    
    def is_ongoing(self, obj):
        return obj.is_ongoing
    is_ongoing.boolean = True
    is_ongoing.short_description = 'Ongoing?'
    
    def save_model(self, request, obj, form, change):
        # First save the object to get a primary key
        super().save_model(request, obj, form, change)
        # Then update the status if needed
        obj.update_status()

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'start_date', 'end_date', 'budget', 'implementer', 'donor', 'display_categories')
    list_filter = ('status', 'start_date', 'implementer', 'donor', CategoryFilter)
    search_fields = ('title', 'description', 'implementer', 'donor')
    date_hierarchy = 'start_date'
    filter_horizontal = ('categories',)
    
    def display_categories(self, obj):
        return ", ".join([c.name for c in obj.categories.all()])
    display_categories.short_description = 'Categories'

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('title', 'activity_date', 'location', 'created_by', 'display_categories')
    list_filter = ('activity_date', 'location', CategoryFilter)
    search_fields = ('title', 'description', 'location')
    date_hierarchy = 'activity_date'
    filter_horizontal = ('categories',)
    
    def display_categories(self, obj):
        return ", ".join([c.name for c in obj.categories.all()])
    display_categories.short_description = 'Categories'

@admin.register(MediaItem)
class MediaItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'media_type', 'uploaded_at', 'file_preview')
    list_filter = ('media_type', 'uploaded_at')
    search_fields = ('title', 'description')
    date_hierarchy = 'uploaded_at'
    filter_horizontal = ('categories',)
    
    def file_preview(self, obj):
        if obj.file:
            if obj.media_type == 'image':
                return format_html('<img src="{}" style="max-height: 50px;" />', obj.file.url)
            return obj.file.name
        return "No file"
    file_preview.short_description = 'Preview'

class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 1
    ordering = ('order',)
    fields = ('title', 'url', 'named_url', 'parent', 'order', 'is_active')

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [MenuItemInline]

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'menu', 'parent', 'order', 'is_active')
    list_filter = ('menu', 'is_active')
    search_fields = ('title', 'url', 'named_url')
    list_editable = ('order', 'is_active')
    ordering = ('menu', 'order')
