from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import PermissionDenied
import os
from datetime import datetime

from .models import MediaFile, SiteSettings

# Custom decorator to check if user is admin
def admin_required(view_func):
    decorated_view = user_passes_test(
        lambda u: u.is_authenticated and u.is_staff,
        login_url='admin:login'
    )(view_func)
    return decorated_view

# Dashboard
@admin_required
def dashboard(request):
    from django.db import connection
    import sys
    from django.conf import settings
    from django.contrib.auth import get_user_model
    from core.models import News, Event  # Using core app's models
    from main.models import Project, Activity  # Keep other models from main app
    from django.utils import timezone
    
    # Get counts for dashboard cards
    User = get_user_model()
    
    try:
        # Get total published news count from core app
        news_count = News.objects.filter(status='published').count()
        
        # Get upcoming events from core app (events that haven't ended yet)
        now = timezone.now()
        events_count = Event.objects.filter(
            end_date__gte=now
        ).exclude(
            status='completed'
        ).count()
        
        # Get active projects count
        projects_count = Project.objects.filter(
            is_active=True,
            status__in=['ongoing', 'planned']
        ).count()
        
        # Get active users count
        users_count = User.objects.filter(is_active=True).count()
        
        # Get recent activities
        recent_activities = Activity.objects.select_related('user').order_by('-timestamp')[:10]  # Get 10 most recent activities
    except Exception as e:
        # Log the error for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in dashboard counts: {str(e)}")
        
        # Set default values
        news_count = 0
        events_count = 0
        projects_count = 0
        users_count = 0
        recent_activities = []
    
    # Get system information
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    django_version = ""  # Will be set in the context
    
    # Get database info
    db_conn = connection.cursor()
    db_vendor = connection.vendor
    db_version = ""
    
    if db_vendor == 'sqlite':
        db_conn.execute("SELECT sqlite_version()")
        db_version = db_conn.fetchone()[0]
    elif db_vendor == 'postgresql':
        db_conn.execute("SELECT version()")
        db_version = db_conn.fetchone()[0].split()[1]
    elif db_vendor == 'mysql':
        db_conn.execute("SELECT VERSION()")
        db_version = db_conn.fetchone()[0]
    
    db_conn.close()
    
    context = {
        'page_title': 'Dashboard',
        'news_count': news_count,
        'events_count': events_count,
        'projects_count': projects_count,
        'users_count': users_count,
        'recent_activities': recent_activities[:5],  # Show only the 5 most recent activities
        'python_version': python_version,
        'django_version': django_version,
        'database_info': {
            'name': db_vendor.capitalize(),
            'version': db_version,
        },
        'environment': 'Development' if settings.DEBUG else 'Production',
        'debug': settings.DEBUG,
    }
    
    return render(request, 'admin/dashboard.html', context)

# Category Views
@admin_required
def category_list(request):
    from core.models import Category
    from django.db.models import Count
    
    categories = Category.objects.annotate(
        news_count=Count('news_posts')
    ).order_by('name')
    
    context = {
        'title': 'News Categories',
        'categories': categories,
    }
    return render(request, 'admin/categories/list.html', context)

@admin_required
def category_add(request):
    from core.models import Category
    from django import forms
    
    class CategoryForm(forms.ModelForm):
        class Meta:
            model = Category
            fields = ['name', 'description']
            widgets = {
                'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            }
    
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.slug = category.name.lower().replace(' ', '-')
            category.save()
            messages.success(request, 'Category added successfully!')
            return redirect('admin:category_list')
    else:
        form = CategoryForm()
    
    context = {
        'title': 'Add New Category',
        'form': form,
        'edit_mode': False
    }
    return render(request, 'admin/categories/form.html', context)

@admin_required
def category_edit(request, pk):
    from core.models import Category
    from django import forms
    
    category = get_object_or_404(Category, pk=pk)
    
    class CategoryForm(forms.ModelForm):
        class Meta:
            model = Category
            fields = ['name', 'description']
            widgets = {
                'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            }
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category = form.save(commit=False)
            category.slug = category.name.lower().replace(' ', '-')
            category.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('admin:category_list')
    else:
        form = CategoryForm(instance=category)
    
    context = {
        'title': 'Edit Category',
        'form': form,
        'category': category,
        'edit_mode': True
    }
    return render(request, 'admin/categories/form.html', context)

@admin_required
def category_delete(request, pk):
    from core.models import Category
    
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        category_name = category.name
        category.delete()
        messages.success(request, f'Category "{category_name}" has been deleted.')
        return redirect('admin:category_list')
    
    context = {
        'title': 'Delete Category',
        'category': category,
    }
    return render(request, 'admin/categories/delete.html', context)

# News Views
@admin_required
def news_list(request):
    # Using core app's News model instead of main app's
    from core.models import News
    
    # Get search query if any
    search_query = request.GET.get('q', '')
    
    # Get all news articles, ordered by publish date (newest first)
    news_list = News.objects.all().order_by('-publish_date')
    
    # Apply search filter if query exists
    if search_query:
        news_list = news_list.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(author__username__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(news_list, 10)  # Show 10 news per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'title': 'News Management',
        'active_menu': 'news',
        'news_list': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'search_query': search_query,
    }
    return render(request, 'admin/news/list.html', context)

@admin_required
def news_add(request):
    from core.models import News, Category
    from django import forms
    from django.contrib.auth import get_user_model
    from django.utils.text import slugify
    
    User = get_user_model()
    
    class NewsForm(forms.ModelForm):
        class Meta:
            model = News
            fields = ['title', 'excerpt', 'content', 'feature_image', 
                     'status', 'is_featured', 'author', 'categories']
            widgets = {
                'excerpt': forms.Textarea(attrs={'rows': 3, 'maxlength': 300}),
                'content': forms.Textarea(attrs={'rows': 10, 'class': 'form-control'}),
                'categories': forms.SelectMultiple(attrs={'class': 'form-control'}),
            }
    
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES)
        if form.is_valid():
            news = form.save(commit=False)
            # Set the slug from the title
            news.slug = slugify(news.title)
            # Set the author to the current user if not specified
            if not news.author:
                news.author = request.user
            news.save()
            form.save_m2m()  # Save many-to-many data for categories
            messages.success(request, 'News article was added successfully!')
            return redirect('admin:news_list')
    else:
        form = NewsForm(initial={'author': request.user, 'status': 'draft'})
    
    context = {
        'title': 'Add News Article',
        'form': form,
        'users': User.objects.filter(is_active=True).order_by('first_name', 'last_name'),
        'categories': Category.objects.all(),
        'edit_mode': False
    }
    return render(request, 'admin/news/form.html', context)

@admin_required
def news_edit(request, pk):
    from core.models import News, Category
    from django import forms
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    news = get_object_or_404(News, pk=pk)
    
    class NewsForm(forms.ModelForm):
        class Meta:
            model = News
            fields = ['title', 'excerpt', 'content', 'feature_image', 
                     'status', 'is_featured', 'author', 'categories']
            widgets = {
                'excerpt': forms.Textarea(attrs={'rows': 3, 'maxlength': 300}),
                'content': forms.Textarea(attrs={'rows': 10, 'class': 'form-control'}),
                'categories': forms.SelectMultiple(attrs={'class': 'form-control'}),
            }
    
    if request.method == 'POST':
        # Handle file deletion if needed
        if 'feature_image-clear' in request.POST:
            news.feature_image.delete(save=False)
        
        form = NewsForm(request.POST, request.FILES, instance=news)
        if form.is_valid():
            news = form.save(commit=False)
            # Update the slug if title changed
            if 'title' in form.changed_data:
                from django.utils.text import slugify
                news.slug = slugify(news.title)
            news.save()
            form.save_m2m()  # Save many-to-many data for categories
            messages.success(request, 'News article was updated successfully!')
            return redirect('admin:news_list')
    else:
        form = NewsForm(instance=news)
    
    context = {
        'title': 'Edit News Article',
        'form': form,
        'news': news,
        'users': User.objects.filter(is_active=True).order_by('first_name', 'last_name'),
        'categories': Category.objects.all(),
        'edit_mode': True
    }
    return render(request, 'admin/news/form.html', context)

@admin_required
def news_delete(request, pk):
    from core.models import News
    
    news = get_object_or_404(News, pk=pk)
    if request.method == 'POST':
        news.delete()
        messages.success(request, 'The news article was deleted successfully.')
        return redirect('admin:news_list')
    
    # If not a POST request, show confirmation page
    context = {
        'title': 'Delete News Article',
        'news': news,
    }
    return render(request, 'admin/news/confirm_delete.html', context)

# Events Views
@admin_required
def events_list(request):
    # Using core app's Event model instead of main app's
    from core.models import Event
    
    # Get search query if any
    search_query = request.GET.get('q', '')
    
    # Get all events, ordered by start date (upcoming first)
    events_list = Event.objects.all().order_by('start_date')
    
    # Apply search filter if query exists
    if search_query:
        events_list = events_list.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(location__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(events_list, 10)  # Show 10 events per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Update status for ongoing events only if not manually set to 'completed' or 'cancelled'
    now = timezone.now()
    for event in page_obj:
        # Skip if status is manually set to 'completed' or 'cancelled'
        if event.status in ['completed', 'cancelled']:
            continue
            
        # Only update status for 'upcoming' or 'ongoing' events
        if event.end_date < now:
            event.status = 'completed'
            event.save(update_fields=['status'])  # Save the status to the database
        elif event.start_date <= now <= event.end_date and event.status != 'ongoing':
            event.status = 'ongoing'
            event.save(update_fields=['status'])  # Save the status to the database
    
    context = {
        'title': 'Events Management',
        'events': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'search_query': search_query,
    }
    return render(request, 'admin/events/list.html', context)

@admin_required
def event_add(request):
    from core.models import Event
    from django import forms
    from django.contrib.auth import get_user_model
    from django.utils.text import slugify
    
    class EventForm(forms.ModelForm):
        class Meta:
            model = Event
            fields = ['title', 'description', 'start_date', 'end_date', 
                     'location', 'status', 'feature_image']
            widgets = {
                'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
                'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
                'description': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
            }
    
    User = get_user_model()
    
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            # Set the slug from the title
            event.slug = slugify(event.title)
            event.save()
            messages.success(request, 'Event was added successfully!')
            return redirect('admin:events_list')
    else:
        # Set default start time to next hour, end time to 2 hours later
        next_hour = timezone.now().replace(minute=0, second=0, microsecond=0) + timezone.timedelta(hours=1)
        initial = {
            'start_date': next_hour,
            'end_date': next_hour + timezone.timedelta(hours=2),
            'status': 'upcoming'
        }
        form = EventForm(initial=initial)
    
    context = {
        'title': 'Add New Event',
        'form': form,
        'edit_mode': False
    }
    return render(request, 'admin/events/form.html', context)

@admin_required
def event_edit(request, pk):
    from core.models import Event
    from django import forms
    from django.contrib.auth import get_user_model
    from django.utils.text import slugify
    import logging
    
    logger = logging.getLogger(__name__)
    User = get_user_model()
    
    try:
        event = get_object_or_404(Event, pk=pk)
        logger.info(f"Editing event: {event.title} (ID: {event.id})")
        
        class EventForm(forms.ModelForm):
            class Meta:
                model = Event
                fields = ['title', 'description', 'start_date', 'end_date', 
                         'location', 'status', 'feature_image']
                widgets = {
                    'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
                    'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
                    'description': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}),
                }
        
        if request.method == 'POST':
            logger.info("Processing POST request")
            logger.info(f"POST data: {request.POST}")
            logger.info(f"FILES data: {request.FILES}")
            
            # Handle file deletion if needed
            if 'feature_image-clear' in request.POST:
                logger.info("Clearing feature image")
                if event.feature_image:
                    event.feature_image.delete(save=False)
            
            form = EventForm(request.POST, request.FILES, instance=event)
            
            if form.is_valid():
                logger.info("Form is valid")
                event = form.save(commit=False)
                # Update the slug if title changed
                if 'title' in form.changed_data:
                    event.slug = slugify(event.title)
                
                try:
                    event.save()
                    logger.info(f"Successfully updated event: {event.title}")
                    messages.success(request, 'Event was updated successfully!')
                    return redirect('admin:events_list')
                except Exception as e:
                    logger.error(f"Error saving event: {str(e)}")
                    messages.error(request, f'Error saving event: {str(e)}')
            else:
                logger.warning(f"Form errors: {form.errors}")
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
        else:
            form = EventForm(instance=event)
        
        context = {
            'title': 'Edit Event',
            'form': form,
            'event': event,
            'edit_mode': True
        }
        return render(request, 'admin/events/form.html', context)
        
    except Exception as e:
        logger.error(f"Error in event_edit view: {str(e)}")
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('admin:events_list')

@admin_required
def event_delete(request, pk):
    from core.models import Event
    
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        event.delete()
        messages.success(request, 'The event was deleted successfully.')
        return redirect('admin:events_list')
    
    # If not a POST request, show confirmation page
    context = {
        'title': 'Delete Event',
        'event': event,
    }
    return render(request, 'admin/events/confirm_delete.html', context)

# Projects Views
@admin_required
def projects_list(request):
    from main.models import Project, Category
    
    # Get search query if any
    search_query = request.GET.get('q', '')
    
    # Get all projects, ordered by start date (newest first)
    projects_list = Project.objects.all().order_by('-start_date')
    
    # Apply search filter if query exists
    if search_query:
        projects_list = projects_list.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(location__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(projects_list, 10)  # Show 10 projects per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'title': 'Projects Management',
        'projects': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'search_query': search_query,
    }
    return render(request, 'admin/projects/list.html', context)

@admin_required
def project_add(request):
    from main.models import Project, Category
    from django import forms
    from django.conf import settings
    
    class ProjectForm(forms.ModelForm):
        categories = forms.ModelMultipleChoiceField(
            queryset=Category.objects.all(),
            required=False,
            widget=forms.SelectMultiple(attrs={'class': 'form-control select2'})
        )
        
        class Meta:
            model = Project
            fields = [
                'title', 'slug', 'short_description', 'description', 'status',
                'start_date', 'end_date', 'budget', 'location', 'image',
                'is_featured', 'is_active', 'categories'
            ]
            widgets = {
                'start_date': forms.DateInput(attrs={'class': 'form-control datepicker'}, format='%Y-%m-%d'),
                'end_date': forms.DateInput(attrs={'class': 'form-control datepicker'}, format='%Y-%m-%d'),
                'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 8}),
                'short_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'maxlength': 300}),
            }
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.save()
            form.save_m2m()  # Save many-to-many relationships (categories)
            messages.success(request, 'Project was added successfully!')
            return redirect('admin:projects_list')
    else:
        form = ProjectForm()
    
    context = {
        'title': 'Add New Project',
        'form': form,
        'categories': Category.objects.all(),
        'CURRENCY_SYMBOL': getattr(settings, 'CURRENCY_SYMBOL', '$'),
        'edit_mode': False
    }
    return render(request, 'admin/projects/form.html', context)

@admin_required
def project_edit(request, pk):
    from main.models import Project, Category
    from django import forms
    from django.conf import settings
    
    project = get_object_or_404(Project, pk=pk)
    
    class ProjectForm(forms.ModelForm):
        categories = forms.ModelMultipleChoiceField(
            queryset=Category.objects.all(),
            required=False,
            widget=forms.SelectMultiple(attrs={'class': 'form-control select2'})
        )
        
        class Meta:
            model = Project
            fields = [
                'title', 'slug', 'short_description', 'description', 'status',
                'start_date', 'end_date', 'budget', 'location', 'image',
                'is_featured', 'is_active', 'categories'
            ]
            widgets = {
                'start_date': forms.DateInput(attrs={'class': 'form-control datepicker'}, format='%Y-%m-%d'),
                'end_date': forms.DateInput(attrs={'class': 'form-control datepicker'}, format='%Y-%m-%d'),
                'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 8}),
                'short_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'maxlength': 300}),
            }
    
    if request.method == 'POST':
        # Handle file deletion if needed
        if 'image-clear' in request.POST:
            project.image.delete(save=False)
        
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Project was updated successfully!')
            return redirect('admin:projects_list')
    else:
        form = ProjectForm(instance=project)
        # Set initial categories for the form
        form.fields['categories'].initial = project.categories.all()
    
    context = {
        'title': 'Edit Project',
        'form': form,
        'project': project,
        'categories': Category.objects.all(),
        'CURRENCY_SYMBOL': getattr(settings, 'CURRENCY_SYMBOL', '$'),
        'edit_mode': True
    }
    return render(request, 'admin/projects/form.html', context)

@admin_required
def project_delete(request, pk):
    from main.models import Project
    
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        project.delete()
        messages.success(request, 'The project was deleted successfully.')
        return redirect('admin:projects_list')
    
    # If not a POST request, show confirmation page
    context = {
        'title': 'Delete Project',
        'project': project,
    }
    return render(request, 'admin/projects/confirm_delete.html', context)

# Media Views
@admin_required
def media_list(request):
    media_files = MediaFile.objects.all().order_by('-uploaded_at')
    
    context = {
        'page_title': 'Media Library',
        'media_files': media_files,
    }
    return render(request, 'admin/media/list.html', context)

@admin_required
def media_upload(request):
    
    if request.method == 'POST' and request.FILES.getlist('file'):
        uploaded_files = request.FILES.getlist('file')
        success_count = 0
        
        for file in uploaded_files:
            try:
                # Check file size (10MB limit)
                if file.size > 10 * 1024 * 1024:  # 10MB
                    messages.warning(request, f'File {file.name} is too large. Maximum size is 10MB.')
                    continue
                
                # Check file extension
                allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.pdf', 
                                    '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt']
                if not any(file.name.lower().endswith(ext) for ext in allowed_extensions):
                    messages.warning(request, f'File type not allowed for {file.name}.')
                    continue
                
                # Save the file
                media_file = MediaFile(
                    file=file,
                    uploaded_by=request.user
                )
                media_file.save()
                success_count += 1
                
            except Exception as e:
                messages.error(request, f'Error uploading {file.name}: {str(e)}')
        
        if success_count > 0:
            messages.success(request, f'Successfully uploaded {success_count} file(s).')
        
        return redirect('admin:media_list')
    
    return redirect('admin:media_list')

@admin_required
def media_delete(request, pk):
    
    try:
        media_file = MediaFile.objects.get(pk=pk)
        
        # Only allow deletion by superusers or the user who uploaded the file
        if not request.user.is_superuser and media_file.uploaded_by != request.user:
            raise PermissionDenied("You don't have permission to delete this file.")
        
        # Delete the file from storage
        media_file.file.delete(save=False)
        # Delete the database record
        media_file.delete()
        
        messages.success(request, 'File deleted successfully.')
    except MediaFile.DoesNotExist:
        messages.error(request, 'File not found.')
    except Exception as e:
        messages.error(request, f'Error deleting file: {str(e)}')
    
    return redirect('admin:media_list')

# Users Views
@admin_required
def users_list(request):
    from django.contrib.auth import get_user_model
    from django.db.models import Q
    from django.core.paginator import Paginator
    
    User = get_user_model()
    
    # Get search query if any
    search_query = request.GET.get('q', '')
    
    # Get all users, excluding the current user if not superuser
    if request.user.is_superuser:
        users_list = User.objects.all()
    else:
        users_list = User.objects.exclude(is_superuser=True)
    
    # No need to create profiles as we're using the User model directly
    
    # Apply search filter if query exists
    if search_query:
        users_list = users_list.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    # Order by most recent first
    users_list = users_list.order_by('-date_joined')
    
    # Pagination
    paginator = Paginator(users_list, 10)  # Show 10 users per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'title': 'Users Management',
        'users': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'search_query': search_query,
    }
    return render(request, 'admin/users/list.html', context)

@admin_required
def user_add(request):
    from django.contrib.auth import get_user_model
    from django.contrib.auth.forms import UserCreationForm, UserChangeForm
    from django import forms
    
    User = get_user_model()
    
    class CustomUserCreationForm(UserCreationForm):
        class Meta:
            model = User
            fields = ('email', 'first_name', 'last_name', 'password1', 'password2', 
                     'is_active', 'is_staff', 'is_superuser', 'groups')
            
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields['password1'].required = True
            self.fields['password2'].required = True
            self.fields['email'].required = True
    
    class CustomUserChangeForm(UserChangeForm):
        password = None  # Remove the password field
        
        class Meta:
            model = User
            fields = ('email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
    
    # Get all available groups for the form
    from django.contrib.auth.models import Group
    available_groups = Group.objects.all()
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            form.save_m2m()  # Save many-to-many relationships (groups, permissions)
            
            # Handle profile picture update
            if 'profile_picture' in request.FILES:
                user.profile_picture = request.FILES['profile_picture']
                user.save()
            
            messages.success(request, f'User "{user.email}" was created successfully.')
            return redirect('admin:users_list')
    else:
        form = CustomUserCreationForm()
    
    context = {
        'title': 'Add New User',
        'form': form,
        'edit_mode': False,
        'groups': available_groups  # Add groups to context
    }
    return render(request, 'admin/users/form.html', context)

@admin_required
def user_edit(request, pk):
    from django.contrib.auth import get_user_model
    from django.contrib.auth.forms import UserChangeForm
    from django import forms
    from django.core.exceptions import PermissionDenied
    
    User = get_user_model()
    user_obj = get_object_or_404(User, pk=pk)
    
    # Prevent non-superusers from editing superusers
    if user_obj.is_superuser and not request.user.is_superuser:
        raise PermissionDenied("You don't have permission to edit this user.")
    
    class CustomUserChangeForm(UserChangeForm):
        password = None  # Remove the password field
        
        class Meta:
            model = User
            fields = ('email', 'first_name', 'last_name', 'is_active', 'is_staff', 'groups')
            
            if request.user.is_superuser:
                fields += ('is_superuser', 'user_permissions')
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Make email required and ensure it's in lowercase
            self.fields['email'].required = True
    
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=user_obj)
        
        # Handle password change if provided
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        change_password = bool(password1 and password2)
        
        if form.is_valid() and (not change_password or password1 == password2):
            user = form.save(commit=False)
            
            # Update password if provided
            if change_password:
                user.set_password(password1)
            
            user.save()
            form.save_m2m()  # Save many-to-many relationships
            
            # Handle profile picture update
            if 'profile_picture' in request.FILES:
                user.profile_picture = request.FILES['profile_picture']
            
            if 'profile_picture-clear' in request.POST and user.profile_picture:
                user.profile_picture.delete(save=False)
                user.profile_picture = None
            
            user.save()
            
            messages.success(request, f'User "{user.email}" was updated successfully.')
            return redirect('admin:users_list')
        elif change_password and password1 != password2:
            form.add_error('password2', 'The two password fields didn\'t match.')
    else:
        form = CustomUserChangeForm(instance=user_obj)
    
    # Get all available groups
    from django.contrib.auth.models import Group
    available_groups = Group.objects.all()
    
    context = {
        'title': f'Edit User: {user_obj.get_full_name() or user_obj.email}',
        'form': form,
        'user_obj': user_obj,
        'groups': available_groups,
        'edit_mode': True
    }
    return render(request, 'admin/users/form.html', context)

@admin_required
def user_delete(request, pk):
    from django.contrib.auth import get_user_model
    from django.contrib import messages
    from django.core.exceptions import PermissionDenied
    
    User = get_user_model()
    user = get_object_or_404(User, pk=pk)
    
    # Prevent deleting yourself
    if user == request.user:
        messages.error(request, 'You cannot delete your own account while logged in.')
        return redirect('admin:users_list')
    
    # Prevent non-superusers from deleting superusers
    if user.is_superuser and not request.user.is_superuser:
        raise PermissionDenied("You don't have permission to delete this user.")
    
    if request.method == 'POST':
        # Verify confirmation
        if request.POST.get('confirm_text', '').strip().upper() != 'DELETE':
            messages.error(request, 'Please type DELETE in all caps to confirm deletion.')
            return redirect('admin:user_delete', pk=user.pk)
        
        username = user.username
        user.delete()
        messages.success(request, f'User "{username}" was deleted successfully.')
        return redirect('admin:users_list')
    
    # If not a POST request, show confirmation page
    context = {
        'title': 'Delete User',
        'user_obj': user,
    }
    return render(request, 'admin/users/confirm_delete.html', context)

# Settings Views
@admin_required
def menu_management(request):
    context = {
        'page_title': 'Menu Management',
    }
    return render(request, 'admin/settings/menu.html', context)

@admin_required
def homepage_settings(request):
    context = {
        'page_title': 'Homepage Settings',
    }
    return render(request, 'admin/settings/homepage.html', context)

@admin_required
def general_settings(request):
    site_settings = SiteSettings.get_solo()
    
    if request.method == 'POST':
        try:
            # Handle logo removal if checkbox is checked
            if 'remove_logo' in request.POST and request.POST['remove_logo'] == 'on':
                if site_settings.site_logo:
                    # Delete the old logo file if it exists
                    if os.path.isfile(site_settings.site_logo.path):
                        os.remove(site_settings.site_logo.path)
                    site_settings.site_logo = None
            
            # Handle new logo upload
            if 'site_logo' in request.FILES and request.FILES['site_logo']:
                # Delete old logo if it exists
                if site_settings.site_logo:
                    if os.path.isfile(site_settings.site_logo.path):
                        os.remove(site_settings.site_logo.path)
                site_settings.site_logo = request.FILES['site_logo']
            
            # Update text fields
            text_fields = [
                'site_name', 'site_description', 'contact_email',
                'contact_phone', 'contact_address', 'facebook_url',
                'twitter_url', 'instagram_url', 'linkedin_url'
            ]
            
            for field in text_fields:
                if field in request.POST:
                    setattr(site_settings, field, request.POST.get(field, ''))
            
            # Save all changes
            site_settings.save()
            
            messages.success(request, 'Settings saved successfully!')
            return redirect('admin:general_settings')
            
        except Exception as e:
            messages.error(
                request,
                f'An error occurred while saving settings: {str(e)}. Please try again.'
            )
            # Log the error for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Error saving site settings: {str(e)}', exc_info=True)
    
    context = {
        'page_title': 'General Settings',
        'settings': site_settings,
    }
    return render(request, 'admin/settings/general.html', context)

# Profile
@admin_required
def profile(request):
    user = request.user
    context = {
        'page_title': 'My Profile',
        'user': user,
    }
    return render(request, 'admin/profile.html', context)

@login_required
def profile_update(request):
    if request.method == 'POST':
        try:
            user = request.user
            user.first_name = request.POST.get('first_name', '')
            user.last_name = request.POST.get('last_name', '')
            
            # Only update email if it's changed and not used by another user
            new_email = request.POST.get('email', '')
            if new_email and new_email != user.email:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                if not User.objects.filter(email=new_email).exists():
                    user.email = new_email
                else:
                    messages.error(request, 'This email is already in use by another account.')
            
            # Update additional fields if they exist on your user model
            if hasattr(user, 'phone'):
                user.phone = request.POST.get('phone', '')
            if hasattr(user, 'bio'):
                user.bio = request.POST.get('bio', '')
            
            user.save()
            messages.success(request, 'Profile updated successfully!')
            
        except Exception as e:
            messages.error(request, f'Error updating profile: {str(e)}')
    
    return redirect('admin:profile')

@login_required
def change_password(request):
    if request.method == 'POST':
        user = request.user
        current_password = request.POST.get('current_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')
        
        # Validate current password
        if not user.check_password(current_password):
            messages.error(request, 'Your current password was entered incorrectly.')
            return redirect('admin:profile')
        
        # Validate new password
        if new_password1 != new_password2:
            messages.error(request, 'The two password fields didn\'t match.')
            return redirect('admin:profile')
        
        if len(new_password1) < 8:
            messages.error(request, 'Password must be at least 8 characters long.')
            return redirect('admin:profile')
        
        # Set new password
        user.set_password(new_password1)
        user.save()
        
        # Update session to prevent logout
        from django.contrib.auth import update_session_auth_hash
        update_session_auth_hash(request, user)
        
        messages.success(request, 'Your password was successfully updated!')
    
    return redirect('admin:profile')

@login_required
def profile_picture_upload(request):
    if request.method == 'POST' and request.FILES.get('profile_picture'):
        try:
            user = request.user
            profile_picture = request.FILES['profile_picture']
            
            # Validate file size (max 2MB)
            if profile_picture.size > 2 * 1024 * 1024:
                messages.error(request, 'File size should not exceed 2MB.')
                return redirect('admin:profile')
            
            # Validate file type
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif']
            if not any(profile_picture.name.lower().endswith(ext) for ext in valid_extensions):
                messages.error(request, 'Please upload a valid image file (JPG, PNG, GIF).')
                return redirect('admin:profile')
            
            # Save the file
            if hasattr(user, 'profile_picture'):
                # Delete old profile picture if exists
                if user.profile_picture:
                    user.profile_picture.delete(save=False)
                
                # Save new profile picture
                user.profile_picture = profile_picture
                user.save()
                messages.success(request, 'Profile picture updated successfully!')
            else:
                messages.error(request, 'Your user model does not support profile pictures.')
        
        except Exception as e:
            messages.error(request, f'Error updating profile picture: {str(e)}')
    
    return redirect('admin:profile')
