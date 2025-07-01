from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView, DetailView, View
from django.utils import timezone
from django.db.models import Count, Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse_lazy
from core.models import News, Category, Event
from .models import Program, Project, KeySector, QuickLink, Minister, Department, TeamMember, Publication, Document

# Create your views here.

class HomePageView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Home'
        context['active_page'] = 'home'
        
        # Latest news - get all published news for the carousel
        context['latest_news'] = News.objects.filter(
            status='published',
            publish_date__lte=timezone.now()
        ).order_by('-publish_date')
        
        # Featured news
        context['featured_news'] = News.objects.filter(
            is_featured=True,
            status='published',
            publish_date__lte=timezone.now()
        ).first()
        
        # Upcoming events (with status 'upcoming')
        today = timezone.now().date()
        context['upcoming_events'] = Event.objects.filter(
            status='upcoming',
            start_date__gte=today
        ).order_by('start_date')[:4]  # Show next 4 upcoming events
        
        # All other events (not marked as 'upcoming')
        context['past_events'] = Event.objects.exclude(
            status='upcoming'
        ).order_by('-start_date')[:6]  # Show 6 most recent past events
        
        # Other context data
        context['programs'] = Program.objects.filter(is_active=True).order_by('-start_date')[:3]
        context['projects'] = Project.objects.all().order_by('-start_date')[:3]
        
        # Get featured projects
        featured_projects = Project.objects.filter(
            is_active=True,
            is_featured=True
        ).order_by('-start_date')[:6]  # Get up to 6 featured projects
        
        # Debug output
        print("\n=== DEBUG: Featured Projects ===")
        print(f"Found {featured_projects.count()} featured projects")
        
        # If no featured projects, create some sample data
        if not featured_projects.exists():
            print("No featured projects found. Creating sample data...")
            from datetime import datetime, timedelta
            from django.core.files import File
            from django.core.files.temp import NamedTemporaryFile
            import urllib.request
            import os
            
            sample_projects = [
                {
                    'title': 'Community Water Project',
                    'excerpt': 'Providing clean water to rural communities',
                    'category': 'Water',
                    'days_ago': 30
                },
                {
                    'title': 'Education for All',
                    'excerpt': 'Building schools and providing educational materials',
                    'category': 'Education',
                    'days_ago': 45
                },
                {
                    'title': 'Healthcare Initiative',
                    'excerpt': 'Mobile clinics for remote areas',
                    'category': 'Health',
                    'days_ago': 60
                },
                {
                    'title': 'Sustainable Farming',
                    'excerpt': 'Training farmers in sustainable agricultural practices',
                    'category': 'Agriculture',
                    'days_ago': 75
                },
                {
                    'title': 'Women Empowerment',
                    'excerpt': 'Vocational training and microfinance programs',
                    'category': 'Empowerment',
                    'days_ago': 90
                },
                {
                    'title': 'Renewable Energy',
                    'excerpt': 'Solar power installations in off-grid communities',
                    'category': 'Energy',
                    'days_ago': 105
                },
            ]
            
            # Create sample projects
            for i, project_data in enumerate(sample_projects, 1):
                project = Project(
                    title=project_data['title'],
                    description=f"Detailed information about {project_data['title']}. This is a sample project description.",
                    short_description=project_data['excerpt'],
                    is_active=True,
                    is_featured=True,
                    start_date=datetime.now() - timedelta(days=project_data['days_ago']),
                    status='ongoing',
                    slug=f'sample-project-{i}'
                )
                project.save()
                print(f"Created sample project: {project.title}")
            
            # Refresh the queryset
            featured_projects = Project.objects.filter(is_active=True, is_featured=True).order_by('-start_date')[:6]
        
        # Log the final project list
        for project in featured_projects:
            print(f"- {project.title} (ID: {project.id}, Active: {project.is_active}, "
                  f"Featured: {project.is_featured}, Image: {'Exists' if hasattr(project, 'image') and project.image else 'None'}, "
                  f"Slug: {project.slug}")
        print("============================\n")
            
        context['featured_projects'] = featured_projects
        context['key_sectors'] = KeySector.objects.all()
        context['quick_links'] = QuickLink.objects.all()
        context['minister'] = Minister.objects.first()
        return context

class NewsListView(ListView):
    model = News
    template_name = 'news_list.html'
    context_object_name = 'news_list'
    paginate_by = 10
    ordering = ['-publish_date']
    
    def get_queryset(self):
        return News.objects.filter(status='published')

class NewsDetailView(DetailView):
    model = News
    template_name = 'news_detail.html'
    context_object_name = 'news'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return News.objects.filter(status='published')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add title for the page
        context['title'] = f"{self.object.title} - News"
        # Add latest news for sidebar
        context['latest_news'] = News.objects.filter(
            status='published',
            publish_date__lte=timezone.now()
        ).exclude(id=self.object.id).order_by('-publish_date')[:5]
        # Add categories for sidebar
        context['categories'] = Category.objects.annotate(
            news_count=Count('news_posts')
        ).filter(news_count__gt=0)
        # Add related news based on categories
        if self.object.categories.exists():
            context['related_news'] = News.objects.filter(
                categories__in=self.object.categories.all(),
                status='published'
            ).exclude(id=self.object.id).distinct().order_by('-publish_date')[:3]
            
        return context

class ProgramListView(ListView):
    model = Program
    template_name = 'program_list.html'
    context_object_name = 'program_list'
    paginate_by = 10
    ordering = ['-start_date']

class ProgramDetailView(DetailView):
    model = Program
    template_name = 'program_detail.html'
    context_object_name = 'program'

class ProjectListView(ListView):
    model = Project
    template_name = 'project_list.html'
    context_object_name = 'project_list'
    paginate_by = 10
    ordering = ['-start_date']

class ProjectDetailView(DetailView):
    model = Project
    template_name = 'project_detail.html'
    context_object_name = 'project'

def key_sector_detail(request, slug):
    sector = get_object_or_404(KeySector, slug=slug)
    return render(request, 'key_sector_detail.html', {'sector': sector})

class AboutUsView(TemplateView):
    template_name = 'about_us.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'About Us'
        context['active_page'] = 'about'
        return context

class MinistryProfileView(TemplateView):
    template_name = 'about/ministry_profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ministry Profile'
        context['active_page'] = 'about'
        return context

class OrganizationalStructureView(TemplateView):
    template_name = 'about/organizational_structure.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Organizational Structure'
        context['active_page'] = 'about'
        return context

class ManagementTeamView(ListView):
    model = TeamMember
    template_name = 'about/management_team.html'
    context_object_name = 'team_members'
    
    def get_queryset(self):
        return TeamMember.objects.filter(is_active=True).order_by('order')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Management Team'
        context['active_page'] = 'about'
        return context

class HistoryView(TemplateView):
    template_name = 'about/history.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Our History'
        context['active_page'] = 'about'
        return context

class DepartmentsView(ListView):
    model = Department
    template_name = 'departments/list.html'
    context_object_name = 'departments'
    
    def get_queryset(self):
        return Department.objects.filter(is_active=True).order_by('order')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Our Departments'
        context['active_page'] = 'departments'
        return context

class DepartmentDetailView(DetailView):
    model = Department
    template_name = 'departments/detail.html'
    context_object_name = 'department'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.name
        context['active_page'] = 'departments'
        return context

class ProjectsView(ListView):
    model = Project
    template_name = 'projects/list.html'
    context_object_name = 'projects'
    paginate_by = 9
    
    def get_queryset(self):
        queryset = Project.objects.filter(is_active=True).order_by('-start_date')
        
        # Apply filters
        status = self.request.GET.get('status')
        year = self.request.GET.get('year')
        
        if status:
            queryset = queryset.filter(status=status)
            
        if year:
            queryset = queryset.filter(
                Q(start_date__year=year) | Q(end_date__year=year)
            ).distinct()
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all unique years from project start and end dates
        years = Project.objects.filter(is_active=True).dates('start_date', 'year', order='DESC')
        
        context.update({
            'title': 'Our Projects',
            'active_page': 'projects',
            'years': years,
            'status_filter': self.request.GET.get('status', ''),
            'year_filter': self.request.GET.get('year', ''),
        })
        
        return context

class ProjectDetailView(DetailView):
    model = Project
    template_name = 'projects/detail.html'
    context_object_name = 'project'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return Project.objects.filter(is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_object()
        
        # Get related projects (same categories, excluding current project)
        related_projects = Project.objects.filter(
            categories__in=project.categories.all(),
            is_active=True
        ).exclude(id=project.id).distinct()[:3]
        
        # Get gallery images if any
        gallery_images = []
        if hasattr(project, 'gallery'):
            gallery_images = project.gallery.images.all()
        
        context.update({
            'title': project.title,
            'active_page': 'projects',
            'related_projects': related_projects,
            'gallery_images': gallery_images,
        })
        
        return context

class ResourcesView(TemplateView):
    template_name = 'resources/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Resources'
        context['active_page'] = 'resources'
        context['publications'] = Publication.objects.filter(is_published=True).order_by('-publish_date')[:5]
        context['documents'] = Document.objects.filter(is_active=True).order_by('-upload_date')[:5]
        return context

class PublicationsView(ListView):
    model = Publication
    template_name = 'resources/publications.html'
    context_object_name = 'publications'
    paginate_by = 10
    
    def get_queryset(self):
        return Publication.objects.filter(is_published=True).order_by('-publish_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Publications'
        context['active_page'] = 'resources'
        return context

class DocumentsView(ListView):
    model = Document
    template_name = 'resources/documents.html'
    context_object_name = 'documents'
    paginate_by = 20
    
    def get_queryset(self):
        return Document.objects.filter(is_active=True).order_by('-upload_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Documents & Downloads'
        context['active_page'] = 'resources'
        return context

class StatisticsView(TemplateView):
    template_name = 'resources/statistics.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Statistics'
        context['active_page'] = 'resources'
        return context

class ContactView(TemplateView):
    template_name = 'contact.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Contact Us'
        context['active_page'] = 'contact'
        return context
    
    def post(self, request, *args, **kwargs):
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        # Send email
        email_message = f"""
        New contact form submission:
        
        Name: {name}
        Email: {email}
        Subject: {subject}
        
        Message:
        {message}
        """
        
        send_mail(
            f'Contact Form: {subject}',
            email_message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.CONTACT_EMAIL],
            fail_silently=False,
        )
        
        messages.success(request, 'Thank you for your message. We will get back to you soon!')
        return redirect('main:contact')

class LoginView(View):
    template_name = 'auth/login.html'
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_staff or request.user.is_superuser:
                return redirect('admin:dashboard')  # This is correct as we have app_name='admin' in customadmin/urls.py
            return redirect('main:home')
            
        context = {
            'title': 'Login',
            'next': request.GET.get('next', '')
        }
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')
        next_url = request.POST.get('next', '')
        
        user = auth.authenticate(request, username=username, password=password)
        
        if user is not None:
            auth.login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            
            # Redirect to the next URL if it exists and is safe
            if next_url and next_url.startswith('/'):
                return redirect(next_url)
            
            # Redirect admin users to the admin dashboard and regular users to home
            if user.is_staff or user.is_superuser:
                return redirect('admin:dashboard')  # This is correct as we have app_name='admin' in customadmin/urls.py
            return redirect('main:home')
        else:
            messages.error(request, 'Invalid username or password.')
            return render(request, self.template_name, {
                'title': 'Login',
                'next': next_url,
                'form_errors': True
            })

@login_required
def logout_view(request):
    """
    Custom logout view that handles both GET and POST requests.
    Logs out the user and redirects to the login page.
    """
    if request.user.is_authenticated:
        auth.logout(request)
        messages.info(request, 'You have been successfully logged out.')
    return redirect('main:login')

class NewsAndEventsView(TemplateView):
    template_name = 'news_events.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'News & Events'
        context['active_page'] = 'news_events'
        content_type = self.request.GET.get('type', 'all')
        category_slug = self.request.GET.get('category')
        today = timezone.now().date()
        
        # Base querysets
        news_queryset = News.objects.filter(
            status='published',
            publish_date__lte=timezone.now()
        ).order_by('-publish_date')
        
        # Events querysets
        upcoming_events = Event.objects.filter(
            status='upcoming',
            start_date__gte=today
        ).order_by('start_date')
        
        past_events = Event.objects.exclude(
            status='upcoming'
        ).order_by('-start_date')
        
        # Apply category filter if specified
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            news_queryset = news_queryset.filter(categories=category)
            upcoming_events = upcoming_events.filter(categories=category)
            past_events = past_events.filter(categories=category)
            context['current_category'] = category
        
        # Get featured content
        context['featured_news'] = news_queryset.filter(is_featured=True).first()
        
        # Get content based on filter
        if content_type == 'news':
            context['news_items'] = news_queryset.exclude(id=context['featured_news'].id if context['featured_news'] else None)[:8]
            context['upcoming_events'] = upcoming_events[:3]  # Still show some upcoming events in news view
            context['show_news'] = True
            context['show_events'] = False
        elif content_type == 'events':
            context['upcoming_events'] = upcoming_events
            context['past_events'] = past_events
            context['show_news'] = False
            context['show_events'] = True
        else:
            # Show both news and events
            context['news_items'] = news_queryset.exclude(id=context['featured_news'].id if context['featured_news'] else None)[:4]
            context['upcoming_events'] = upcoming_events[:4]
            context['past_events'] = past_events[:4]
            context['show_news'] = True
            context['show_events'] = True
        
        # Get categories for filter
        context['categories'] = Category.objects.annotate(
            news_count=Count('news_posts', distinct=True) + Count('events', distinct=True)
        ).filter(news_count__gt=0).order_by('name')
        
        context['content_type'] = content_type
        return context
