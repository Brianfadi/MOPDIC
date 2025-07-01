from django.db import models
from solo.models import SingletonModel
from django.utils.translation import gettext_lazy as _

class SiteSettings(SingletonModel):
    """
    Site settings model using django-solo to store global settings.
    """
    # Site Information
    site_name = models.CharField(_('Site Name'), max_length=255, default='MOPDIC')
    site_description = models.TextField(_('Site Description'), blank=True)
    site_logo = models.ImageField(
        _('Site Logo'), 
        upload_to='site/', 
        blank=True, 
        null=True,
        help_text=_('Recommended size: 200x50 pixels')
    )
    
    # Contact Information
    contact_email = models.EmailField(_('Contact Email'), blank=True)
    contact_phone = models.CharField(_('Contact Phone'), max_length=20, blank=True)
    contact_address = models.TextField(_('Contact Address'), blank=True)
    
    # Social Media
    facebook_url = models.URLField(_('Facebook URL'), blank=True)
    twitter_url = models.URLField(_('Twitter URL'), blank=True)
    instagram_url = models.URLField(_('Instagram URL'), blank=True)
    linkedin_url = models.URLField(_('LinkedIn URL'), blank=True)
    
    # Additional Settings
    maintenance_mode = models.BooleanField(_('Maintenance Mode'), default=False)
    google_analytics_id = models.CharField(
        _('Google Analytics ID'), 
        max_length=50, 
        blank=True,
        help_text=_('Format: UA-XXXXXXXXX-X or G-XXXXXXXXXX')
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Site Settings')
        verbose_name_plural = _('Site Settings')
    
    def __str__(self):
        return 'Site Settings'
    
    def delete(self, *args, **kwargs):
        """Prevent deletion of the singleton instance."""
        pass
