from django.urls import path, include
from django.views.generic import RedirectView
from django.contrib import admin
from django.contrib.auth import views as auth_views
from . import views

app_name = 'admin'

urlpatterns = [
    # Authentication - Redirect to main login page
    path('login/', RedirectView.as_view(pattern_name='main:login', permanent=False), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='main:login'), name='logout'),
    
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Include the default admin site under /admin/old/
    path('old/', admin.site.urls),
    
    # News
    path('news/', views.news_list, name='news_list'),
    path('news/add/', views.news_add, name='news_add'),
    path('news/edit/<int:pk>/', views.news_edit, name='news_edit'),
    path('news/delete/<int:pk>/', views.news_delete, name='news_delete'),
    
    # News Categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.category_add, name='category_add'),
    path('categories/edit/<int:pk>/', views.category_edit, name='category_edit'),
    path('categories/delete/<int:pk>/', views.category_delete, name='category_delete'),
    
    # Events
    path('events/', views.events_list, name='events_list'),
    path('events/add/', views.event_add, name='event_add'),
    path('events/edit/<int:pk>/', views.event_edit, name='event_edit'),
    path('events/delete/<int:pk>/', views.event_delete, name='event_delete'),
    
    # Projects URLs
    path('projects/', views.projects_list, name='projects_list'),
    path('projects/add/', views.project_add, name='project_add'),
    path('projects/<int:pk>/edit/', views.project_edit, name='project_edit'),
    path('projects/<int:pk>/delete/', views.project_delete, name='project_delete'),
    
    # Media
    path('media/', views.media_list, name='media_list'),
    path('media/upload/', views.media_upload, name='media_upload'),
    path('media/delete/<int:pk>/', views.media_delete, name='media_delete'),
    
    # Users
    path('users/', views.users_list, name='users_list'),
    path('users/add/', views.user_add, name='user_add'),
    path('users/edit/<int:pk>/', views.user_edit, name='user_edit'),
    path('users/delete/<int:pk>/', views.user_delete, name='user_delete'),
    
    # Settings
    path('settings/menu/', views.menu_management, name='menu_management'),
    path('settings/homepage/', views.homepage_settings, name='homepage_settings'),
    path('settings/general/', views.general_settings, name='general_settings'),
    
    # Profile
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.profile_update, name='profile_update'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('profile/picture/', views.profile_picture_upload, name='profile_picture_upload'),
]
