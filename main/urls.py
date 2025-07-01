from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from . import views

app_name = 'main'

urlpatterns = [
    # Home
    path('', views.HomePageView.as_view(), name='home'),
    
    # About Us Section
    path('about/', views.AboutUsView.as_view(), name='about'),
    path('about/ministry-profile/', views.MinistryProfileView.as_view(), name='ministry_profile'),
    path('about/organizational-structure/', views.OrganizationalStructureView.as_view(), name='organizational_structure'),
    path('about/management-team/', views.ManagementTeamView.as_view(), name='management_team'),
    path('about/history/', views.HistoryView.as_view(), name='history'),
    
    # Departments
    path('departments/', views.DepartmentsView.as_view(), name='departments'),
    path('departments/<slug:slug>/', views.DepartmentDetailView.as_view(), name='department_detail'),
    
    # Projects
    path('projects/', views.ProjectsView.as_view(), name='projects'),
    path('projects/<slug:slug>/', views.ProjectDetailView.as_view(), name='project_detail'),
    
    # Resources
    path('resources/', views.ResourcesView.as_view(), name='resources'),
    path('resources/publications/', views.PublicationsView.as_view(), name='publications'),
    
    # Authentication
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('resources/documents/', views.DocumentsView.as_view(), name='documents'),
    path('resources/statistics/', views.StatisticsView.as_view(), name='statistics'),
    
    # News & Events
    path('news-events/', views.NewsAndEventsView.as_view(), name='news_events'),
    path('news/', views.NewsListView.as_view(), name='news_list'),
    path('news/<slug:slug>/', views.NewsDetailView.as_view(), name='news_detail'),
    
    # Programs
    path('programs/', views.ProgramListView.as_view(), name='program_list'),
    path('programs/<slug:slug>/', views.ProgramDetailView.as_view(), name='program_detail'),
    
    # Key Sectors
    path('key-sectors/<slug:slug>/', views.key_sector_detail, name='key_sector_detail'),
    
    # Contact
    path('contact/', views.ContactView.as_view(), name='contact'),
    
    # Authentication
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
