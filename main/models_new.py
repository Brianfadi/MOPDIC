from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

class Department(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    head = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    location = models.CharField(max_length=200, blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text='Font Awesome icon class')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('main:department_detail', kwargs={'slug': self.slug})


class TeamMember(models.Model):
    POSITION_CHOICES = [
        ('minister', 'Minister'),
        ('state_minister', 'State Minister'),
        ('director_general', 'Director General'),
        ('deputy_director', 'Deputy Director'),
        ('director', 'Director'),
        ('manager', 'Manager'),
        ('officer', 'Officer'),
        ('advisor', 'Advisor'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=200)
    position = models.CharField(max_length=50, choices=POSITION_CHOICES)
    position_title = models.CharField(max_length=200, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='team_members')
    bio = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    photo = models.ImageField(upload_to='team_photos/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Team Member'
        verbose_name_plural = 'Team Members'

    def __str__(self):
        return f"{self.name} - {self.get_position_display()}"

    def get_position_display_name(self):
        if self.position_title:
            return self.position_title
        return self.get_position_display()


class Publication(models.Model):
    PUBLICATION_TYPES = [
        ('report', 'Report'),
        ('policy', 'Policy Document'),
        ('strategy', 'Strategy Document'),
        ('guideline', 'Guideline'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    publication_type = models.CharField(max_length=50, choices=PUBLICATION_TYPES)
    file = models.FileField(upload_to='publications/')
    thumbnail = models.ImageField(upload_to='publication_thumbnails/', blank=True, null=True)
    publish_date = models.DateField()
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-publish_date', 'title']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('main:publication_detail', kwargs={'pk': self.pk})


class Document(models.Model):
    DOCUMENT_TYPES = [
        ('form', 'Form'),
        ('template', 'Template'),
        ('manual', 'Manual'),
        ('report', 'Report'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to='documents/')
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_file_extension(self):
        import os
        name, extension = os.path.splitext(self.file.name)
        return extension[1:].upper() if extension else ''
