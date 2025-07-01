import os
import mimetypes
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.core.files.storage import default_storage
from django.core.files import File
from PIL import Image
from io import BytesIO
from django.urls import reverse
from django.urls import reverse


def get_upload_path(instance, filename):
    """
    Returns the upload path for media files
    Format: media/{file_type}/{year}/{month}/{filename}
    """
    file_ext = os.path.splitext(filename)[1].lower()
    file_type = instance.get_file_type_display().lower()
    return f'media/{file_type}/{timezone.now().year}/{timezone.now().month:02d}/{filename}'


class MediaFile(models.Model):
    """
    Model for storing and managing uploaded media files
    """
    FILE_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('document', 'Document'),
        ('audio', 'Audio'),
        ('archive', 'Archive'),
        ('other', 'Other')
    ]
    
    title = models.CharField(max_length=255, blank=True, help_text="A descriptive title for the file")
    file = models.FileField(upload_to=get_upload_path, help_text="The actual file to upload")
    file_type = models.CharField(
        max_length=20, 
        choices=FILE_TYPE_CHOICES, 
        default='other',
        help_text="Type of the file (auto-detected on save)"
    )
    description = models.TextField(blank=True, help_text="Optional description of the file")
    alt_text = models.CharField(max_length=255, blank=True, help_text="Alternative text for accessibility")
    width = models.PositiveIntegerField(blank=True, null=True, help_text="Image/video width in pixels")
    height = models.PositiveIntegerField(blank=True, null=True, help_text="Image/video height in pixels")
    duration = models.DurationField(blank=True, null=True, help_text="Duration for audio/video files")
    file_size = models.PositiveIntegerField(blank=True, null=True, help_text="File size in bytes")
    mime_type = models.CharField(max_length=100, blank=True, help_text="Detected MIME type")
    is_public = models.BooleanField(default=True, help_text="Whether the file is publicly accessible")
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_files',
        help_text="User who uploaded the file"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Media File')
        verbose_name_plural = _('Media Files')
        ordering = ['-created_at']
        permissions = [
            ('can_manage_media', 'Can manage media files'),
        ]

    def __str__(self):
        return self.title or os.path.basename(self.file.name)

    def save(self, *args, **kwargs):
        # Set title to filename if not provided
        if not self.title:
            self.title = os.path.basename(self.file.name)
        
        # Get file info
        if self.file:
            self.file_size = self.file.size
            self.mime_type = mimetypes.guess_type(self.file.name)[0] or 'application/octet-stream'
            
            # Determine file type based on MIME type
            if self.mime_type.startswith('image/'):
                self.file_type = 'image'
                # Get image dimensions
                try:
                    with Image.open(self.file) as img:
                        self.width, self.height = img.size
                except:
                    pass
            elif self.mime_type.startswith('video/'):
                self.file_type = 'video'
            elif self.mime_type.startswith('audio/'):
                self.file_type = 'audio'
            elif self.mime_type in ['application/zip', 'application/x-rar-compressed', 'application/x-tar', 'application/x-gzip']:
                self.file_type = 'archive'
            elif self.mime_type in ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                                  'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                                  'application/vnd.ms-powerpoint', 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                                  'text/plain']:
                self.file_type = 'document'
            else:
                self.file_type = 'other'
        
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return self.file.url if self.file else ''

    def get_file_extension(self):
        """Returns the file extension in lowercase"""
        return os.path.splitext(self.file.name)[1].lower().lstrip('.')

    def get_file_type_icon(self):
        """Returns the appropriate icon class based on file type"""
        icons = {
            'image': 'fa-image',
            'video': 'fa-video',
            'audio': 'fa-music',
            'document': 'fa-file-alt',
            'archive': 'fa-file-archive',
            'pdf': 'fa-file-pdf',
            'word': 'fa-file-word',
            'excel': 'fa-file-excel',
            'powerpoint': 'fa-file-powerpoint',
        }
        
        if self.file_type == 'document':
            ext = self.get_file_extension()
            if ext == 'pdf':
                return icons['pdf']
            elif ext in ['doc', 'docx']:
                return icons['word']
            elif ext in ['xls', 'xlsx', 'csv']:
                return icons['excel']
            elif ext in ['ppt', 'pptx']:
                return icons['powerpoint']
        
        return icons.get(self.file_type, 'fa-file')

    def get_thumbnail_url(self, width=200, height=200):
        """Returns a thumbnail URL for the file if it's an image"""
        if self.file_type != 'image' or not self.file:
            return None
            
        # This is a placeholder - in a real app, you'd want to use something like sorl-thumbnail or easy-thumbnails
        # to generate and serve thumbnails on demand
        return self.file.url


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('main:news_by_category', kwargs={'slug': self.slug})


class Program(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='program_images/', blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Program')
        verbose_name_plural = _('Programs')
        ordering = ['-start_date']

    def __str__(self):
        return self.title




class KeySector(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, help_text='Font Awesome icon class')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = _('Key Sector')
        verbose_name_plural = _('Key Sectors')
        ordering = ['order']

    def __str__(self):
        return self.name


class QuickLink(models.Model):
    title = models.CharField(max_length=100)
    url = models.URLField()
    icon = models.CharField(max_length=50, help_text='Font Awesome icon class')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = _('Quick Link')
        verbose_name_plural = _('Quick Links')
        ordering = ['order']

    def __str__(self):
        return self.title


class Minister(models.Model):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='ministers/', blank=True, null=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Minister')
        verbose_name_plural = _('Ministers')

    def __str__(self):
        return self.name


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

    # ... (rest of the code remains the same)

class Project(models.Model):
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
        ('cancelled', 'Cancelled'),
    ]
    
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField()
    short_description = models.TextField(max_length=300, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='ongoing')
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    budget = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to='projects/images/', blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    categories = models.ManyToManyField(
        'Category',
        through='ProjectCategory',
        related_name='projects',
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'

    def __str__(self):
        return self.title
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.short_description and self.description:
            self.short_description = self.description[:297] + '...' if len(self.description) > 300 else self.description
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('main:project_detail', kwargs={'slug': self.slug})
    
    def is_ongoing(self):
        today = timezone.now().date()
        if self.end_date:
            return self.start_date <= today <= self.end_date
        return self.start_date <= today


class ProjectCategory(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Project Categories'
        unique_together = ('project', 'category')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.project.title} - {self.category.name}"


class Event(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    content = models.TextField(blank=True)
    featured_image = models.ImageField(upload_to='events/images/%Y/%m/%d/', blank=True, null=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=255, blank=True)
    registration_url = models.URLField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['start_date']
        verbose_name = 'Event'
        verbose_name_plural = 'Events'
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            # Ensure slug is unique
            counter = 1
            original_slug = self.slug
            while Event.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        
        # Auto-update status based on dates
        now = timezone.now()
        if self.status != 'cancelled':
            if self.end_date < now:
                self.status = 'completed'
            elif self.start_date <= now <= self.end_date:
                self.status = 'ongoing'
            else:
                self.status = 'upcoming'
                
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('event_detail', kwargs={'slug': self.slug})
    
    @property
    def is_upcoming(self):
        return self.status == 'upcoming'
    
    @property
    def is_ongoing(self):
        return self.status == 'ongoing'
    
    @property
    def is_completed(self):
        return self.status == 'completed'


class News(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique_for_date='publish_date')
    short_description = models.TextField(max_length=300, blank=True)
    content = models.TextField()
    featured_image = models.ImageField(upload_to='news/images/%Y/%m/%d/', blank=True, null=True)
    publish_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(default=False)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name_plural = 'News'
        ordering = ['-publish_date']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('main:news_detail', kwargs={
            'year': self.publish_date.year,
            'month': self.publish_date.month,
            'day': self.publish_date.day,
            'slug': self.slug
        })
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    @property
    def reading_time(self):
        # Average reading speed: 200 words per minute
        words = len(self.content.split())
        return max(1, round(words / 200))  # At least 1 minute


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
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_file_extension(self):
        import os
        name, extension = os.path.splitext(self.file.name)
        return extension


class Activity(models.Model):
    """
    Model to track user activities in the system
    """
    ACTION_CHOICES = [
        ('login', 'User Login'),
        ('logout', 'User Logout'),
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('publish', 'Publish'),
        ('upload', 'File Upload'),
        ('download', 'File Download'),
        ('other', 'Other')
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='activity_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    content_type = models.CharField(max_length=50, blank=True, help_text="Model name of the affected object")
    object_id = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    object_repr = models.CharField(max_length=200, blank=True, help_text="String representation of the object")
    changes = models.TextField(blank=True, help_text="Detailed description of changes")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Activities'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.get_action_display()} - {self.object_repr or 'System'}"
        return extension[1:].upper() if extension else ''
