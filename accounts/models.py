from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import uuid


class UserManager(BaseUserManager):
    """Custom user model manager where email is the unique identifier"""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and save a user with the given email and password."""
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom User Model"""
    username = None
    email = models.EmailField(_('email address'), unique=True)
    phone_number = models.CharField(_('phone number'), max_length=20, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    date_of_birth = models.DateField(_('date of birth'), null=True, blank=True)
    address = models.TextField(_('address'), blank=True)
    city = models.CharField(_('city'), max_length=100, blank=True)
    country = models.CharField(_('country'), max_length=100, blank=True)
    postal_code = models.CharField(_('postal code'), max_length=20, blank=True)
    bio = models.TextField(_('bio'), blank=True)
    
    # Additional fields
    is_verified = models.BooleanField(_('verified'), default=False)
    verification_token = models.UUIDField(default=uuid.uuid4, editable=False)
    last_activity = models.DateTimeField(_('last activity'), default=timezone.now)
    
    # Override default fields
    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = UserManager()
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ('-date_joined',)
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name if full_name else self.email.split('@')[0]
    
    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name if self.first_name else self.email.split('@')[0]
    
    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)
    
    def is_online(self):
        """Check if the user is currently online."""
        if not self.last_activity:
            return False
        return timezone.now() - self.last_activity < timezone.timedelta(minutes=5)
    
    def get_role(self):
        """Get the primary role/group of the user."""
        if self.is_superuser:
            return "Super Admin"
        groups = self.groups.all()
        return groups[0].name if groups else "No Role"
    
    def save(self, *args, **kwargs):
        # Ensure email is always lowercase
        self.email = self.email.lower()
        super().save(*args, **kwargs)


class UserActivity(models.Model):
    """Model to track user activities"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    action = models.CharField(_('action'), max_length=255)
    ip_address = models.GenericIPAddressField(_('IP address'), null=True, blank=True)
    user_agent = models.TextField(_('user agent'), blank=True)
    timestamp = models.DateTimeField(_('timestamp'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('user activity')
        verbose_name_plural = _('user activities')
        ordering = ('-timestamp',)
    
    def __str__(self):
        return f"{self.user.email} - {self.action} at {self.timestamp}"
