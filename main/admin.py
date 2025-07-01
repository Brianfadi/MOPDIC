from django.contrib import admin
from .models import Program, Project, KeySector, QuickLink, Minister, News, Event

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'is_active')
    list_filter = ('start_date', 'is_active')
    search_fields = ('title', 'description')
    date_hierarchy = 'start_date'

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'status', 'budget')
    list_filter = ('status', 'start_date')
    search_fields = ('title', 'description')
    date_hierarchy = 'start_date'

@admin.register(KeySector)
class KeySectorAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    list_editable = ('order',)
    search_fields = ('name', 'description')

@admin.register(QuickLink)
class QuickLinkAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'order')
    list_editable = ('order',)
    search_fields = ('title', 'url')

@admin.register(Minister)
class MinisterAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'created_at')
    search_fields = ('name', 'position', 'message')
    readonly_fields = ('created_at',)

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'publish_date', 'status', 'is_featured')
    list_filter = ('status', 'is_featured', 'publish_date')
    search_fields = ('title', 'content', 'short_description')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'publish_date'
    list_editable = ('status', 'is_featured')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'status', 'is_featured', 'location')
    list_filter = ('status', 'is_featured', 'start_date')
    search_fields = ('title', 'description', 'location')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'start_date'
    list_editable = ('status', 'is_featured')
    readonly_fields = ('created_at', 'updated_at')
    
    # Explicitly define fields to exclude any category-related fields
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
