from django.db import models
from django.contrib.auth import get_user_model
from ckeditor.fields import RichTextField
from django.utils.text import slugify
from django.urls import reverse
from django.utils import timezone

User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class News(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique_for_date='publish_date')
    content = RichTextField()
    excerpt = models.TextField(blank=True)
    feature_image = models.ImageField(upload_to='news/%Y/%m/%d/', blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    publish_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='news_posts'
    )
    categories = models.ManyToManyField(Category, related_name='news_posts')
    is_featured = models.BooleanField(default=False)
    
    class Meta:
        verbose_name_plural = "News"
        ordering = ['-publish_date']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('main:news_detail', kwargs={'slug': self.slug})

class Event(models.Model):
    STATUS_CHOICES = (
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
    )
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = RichTextField()
    location = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='upcoming')
    feature_image = models.ImageField(upload_to='events/%Y/%m/%d/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['start_date']
        verbose_name_plural = 'Events'
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            # Ensure slug is unique
            count = 1
            original_slug = self.slug
            while Event.objects.filter(slug=self.slug).exclude(id=self.id).exists():
                self.slug = f"{original_slug}-{count}"
                count += 1
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('main:event_detail', kwargs={'slug': self.slug})
    
    @property
    def is_upcoming(self):
        return self.status == 'upcoming' and self.start_date > timezone.now()
    
    @property
    def is_ongoing(self):
        now = timezone.now()
        return (self.status == 'ongoing' or 
               (self.start_date <= now <= self.end_date if self.end_date else self.start_date.date() == now.date()))
    
    def update_status(self):
        now = timezone.now()
        # If end_date is None, consider the event as single-day
        if self.end_date is None:
            if now.date() > self.start_date.date():
                self.status = 'completed'
            elif now.date() == self.start_date.date():
                self.status = 'ongoing'
            else:
                self.status = 'upcoming'
        else:
            if self.end_date < now:
                self.status = 'completed'
            elif self.start_date <= now <= self.end_date:
                self.status = 'ongoing'
            else:
                self.status = 'upcoming'
        self.save(update_fields=['status'])

class Project(models.Model):
    STATUS_CHOICES = (
        ('planning', 'Planning'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
    )
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = RichTextField()
    budget = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    implementer = models.CharField(max_length=200)
    donor = models.CharField(max_length=200, blank=True)
    feature_image = models.ImageField(upload_to='projects/%Y/%m/%d/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    categories = models.ManyToManyField(Category, related_name='projects')
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

class Activity(models.Model):
    title = models.CharField(max_length=200)
    description = RichTextField()
    activity_date = models.DateField()
    location = models.CharField(max_length=200, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    categories = models.ManyToManyField(Category, related_name='activities')
    
    class Meta:
        verbose_name_plural = "Activities"
        ordering = ['-activity_date']
    
    def __str__(self):
        return self.title

class MediaItem(models.Model):
    MEDIA_TYPES = (
        ('image', 'Image'),
        ('video', 'Video'),
        ('document', 'Document'),
    )
    
    title = models.CharField(max_length=200)
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES)
    file = models.FileField(upload_to='media/%Y/%m/%d/')
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    categories = models.ManyToManyField(Category, related_name='media_items', blank=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return self.title

class Menu(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class MenuItem(models.Model):
    TARGET_CHOICES = (
        ('_self', 'Same Window'),
        ('_blank', 'New Window'),
    )
    
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name='items')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children')
    title = models.CharField(max_length=100)
    url = models.CharField(max_length=255, blank=True)
    named_url = models.CharField(max_length=100, blank=True)
    order = models.PositiveIntegerField(default=0)
    target = models.CharField(max_length=10, choices=TARGET_CHOICES, default='_self')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return self.title
