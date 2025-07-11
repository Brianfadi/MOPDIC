from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

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

class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='project_images/', blank=True, null=True)
    budget = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=[
        ('planning', 'Planning'),
        ('implementation', 'Implementation'),
        ('completed', 'Completed'),
        ('delayed', 'Delayed')
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Project')
        verbose_name_plural = _('Projects')
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
f r o m   d j a n g o . d b   i m p o r t   m o d e l s  
 f r o m   d j a n g o . c o n f   i m p o r t   s e t t i n g s  
 f r o m   d j a n g o . u t i l s   i m p o r t   t i m e z o n e  
 f r o m   d j a n g o . u t i l s . t e x t   i m p o r t   s l u g i f y  
 f r o m   d j a n g o . u t i l s . t r a n s l a t i o n   i m p o r t   g e t t e x t _ l a z y   a s   _  
  
 c l a s s   D e p a r t m e n t ( m o d e l s . M o d e l ) :  
         n a m e   =   m o d e l s . C h a r F i e l d ( m a x _ l e n g t h = 2 0 0 )  
         s l u g   =   m o d e l s . S l u g F i e l d ( m a x _ l e n g t h = 2 0 0 ,   u n i q u e = T r u e )  
         d e s c r i p t i o n   =   m o d e l s . T e x t F i e l d ( b l a n k = T r u e )  
         h e a d   =   m o d e l s . C h a r F i e l d ( m a x _ l e n g t h = 2 0 0 ,   b l a n k = T r u e )  
         e m a i l   =   m o d e l s . E m a i l F i e l d ( b l a n k = T r u e )  
         p h o n e   =   m o d e l s . C h a r F i e l d ( m a x _ l e n g t h = 5 0 ,   b l a n k = T r u e )  
         l o c a t i o n   =   m o d e l s . C h a r F i e l d ( m a x _ l e n g t h = 2 0 0 ,   b l a n k = T r u e )  
         i c o n   =   m o d e l s . C h a r F i e l d ( m a x _ l e n g t h = 5 0 ,   b l a n k = T r u e ,   h e l p _ t e x t = ' F o n t   A w e s o m e   i c o n   c l a s s ' )  
         o r d e r   =   m o d e l s . P o s i t i v e I n t e g e r F i e l d ( d e f a u l t = 0 )  
         i s _ a c t i v e   =   m o d e l s . B o o l e a n F i e l d ( d e f a u l t = T r u e )  
         c r e a t e d _ a t   =   m o d e l s . D a t e T i m e F i e l d ( a u t o _ n o w _ a d d = T r u e )  
         u p d a t e d _ a t   =   m o d e l s . D a t e T i m e F i e l d ( a u t o _ n o w = T r u e )  
  
         c l a s s   M e t a :  
                 o r d e r i n g   =   [ ' o r d e r ' ,   ' n a m e ' ]  
                 v e r b o s e _ n a m e   =   ' D e p a r t m e n t '  
                 v e r b o s e _ n a m e _ p l u r a l   =   ' D e p a r t m e n t s '  
  
         d e f   _ _ s t r _ _ ( s e l f ) :  
                 r e t u r n   s e l f . n a m e  
  
         d e f   s a v e ( s e l f ,   * a r g s ,   * * k w a r g s ) :  
                 i f   n o t   s e l f . s l u g :  
                         s e l f . s l u g   =   s l u g i f y ( s e l f . n a m e )  
                 s u p e r ( ) . s a v e ( * a r g s ,   * * k w a r g s )  
  
         d e f   g e t _ a b s o l u t e _ u r l ( s e l f ) :  
                 f r o m   d j a n g o . u r l s   i m p o r t   r e v e r s e  
                 r e t u r n   r e v e r s e ( ' m a i n : d e p a r t m e n t _ d e t a i l ' ,   k w a r g s = { ' s l u g ' :   s e l f . s l u g } )  
  
  
 c l a s s   T e a m M e m b e r ( m o d e l s . M o d e l ) :  
         P O S I T I O N _ C H O I C E S   =   [  
                 ( ' m i n i s t e r ' ,   ' M i n i s t e r ' ) ,  
                 ( ' s t a t e _ m i n i s t e r ' ,   ' S t a t e   M i n i s t e r ' ) ,  
                 ( ' d i r e c t o r _ g e n e r a l ' ,   ' D i r e c t o r   G e n e r a l ' ) ,  
                 ( ' d e p u t y _ d i r e c t o r ' ,   ' D e p u t y   D i r e c t o r ' ) ,  
                 ( ' d i r e c t o r ' ,   ' D i r e c t o r ' ) ,  
                 ( ' m a n a g e r ' ,   ' M a n a g e r ' ) ,  
                 ( ' o f f i c e r ' ,   ' O f f i c e r ' ) ,  
                 ( ' a d v i s o r ' ,   ' A d v i s o r ' ) ,  
                 ( ' o t h e r ' ,   ' O t h e r ' ) ,  
         ]  
          
         n a m e   =   m o d e l s . C h a r F i e l d ( m a x _ l e n g t h = 2 0 0 )  
         p o s i t i o n   =   m o d e l s . C h a r F i e l d ( m a x _ l e n g t h = 5 0 ,   c h o i c e s = P O S I T I O N _ C H O I C E S )  
         p o s i t i o n _ t i t l e   =   m o d e l s . C h a r F i e l d ( m a x _ l e n g t h = 2 0 0 ,   b l a n k = T r u e )  
         d e p a r t m e n t   =   m o d e l s . F o r e i g n K e y ( D e p a r t m e n t ,   o n _ d e l e t e = m o d e l s . S E T _ N U L L ,   n u l l = T r u e ,   b l a n k = T r u e ,   r e l a t e d _ n a m e = ' t e a m _ m e m b e r s ' )  
         b i o   =   m o d e l s . T e x t F i e l d ( b l a n k = T r u e )  
         e m a i l   =   m o d e l s . E m a i l F i e l d ( b l a n k = T r u e )  
         p h o n e   =   m o d e l s . C h a r F i e l d ( m a x _ l e n g t h = 5 0 ,   b l a n k = T r u e )  
         p h o t o   =   m o d e l s . I m a g e F i e l d ( u p l o a d _ t o = ' t e a m _ p h o t o s / ' ,   b l a n k = T r u e ,   n u l l = T r u e )  
         o r d e r   =   m o d e l s . P o s i t i v e I n t e g e r F i e l d ( d e f a u l t = 0 )  
         i s _ a c t i v e   =   m o d e l s . B o o l e a n F i e l d ( d e f a u l t = T r u e )  
         c r e a t e d _ a t   =   m o d e l s . D a t e T i m e F i e l d ( a u t o _ n o w _ a d d = T r u e )  
         u p d a t e d _ a t   =   m o d e l s . D a t e T i m e F i e l d ( a u t o _ n o w = T r u e )  
  
         c l a s s   M e t a :  
                 o r d e r i n g   =   [ ' o r d e r ' ,   ' n a m e ' ]  
                 v e r b o s e _ n a m e   =   ' T e a m   M e m b e r '  
                 v e r b o s e _ n a m e _ p l u r a l   =   ' T e a m   M e m b e r s '  
  
         d e f   _ _ s t r _ _ ( s e l f ) :  
                 r e t u r n   f " { s e l f . n a m e }   -   { s e l f . g e t _ p o s i t i o n _ d i s p l a y ( ) } "  
  
         d e f   g e t _ p o s i t i o n _ d i s p l a y _ n a m e ( s e l f ) :  
                 i f   s e l f . p o s i t i o n _ t i t l e :  
                         r e t u r n   s e l f . p o s i t i o n _ t i t l e  
                 r e t u r n   s e l f . g e t _ p o s i t i o n _ d i s p l a y ( )  
  
  
 c l a s s   P u b l i c a t i o n ( m o d e l s . M o d e l ) :  
         P U B L I C A T I O N _ T Y P E S   =   [  
                 ( ' r e p o r t ' ,   ' R e p o r t ' ) ,  
                 ( ' p o l i c y ' ,   ' P o l i c y   D o c u m e n t ' ) ,  
                 ( ' s t r a t e g y ' ,   ' S t r a t e g y   D o c u m e n t ' ) ,  
                 ( ' g u i d e l i n e ' ,   ' G u i d e l i n e ' ) ,  
                 ( ' o t h e r ' ,   ' O t h e r ' ) ,  
         ]  
          
         t i t l e   =   m o d e l s . C h a r F i e l d ( m a x _ l e n g t h = 2 5 5 )  
         s l u g   =   m o d e l s . S l u g F i e l d ( m a x _ l e n g t h = 2 5 5 ,   u n i q u e = T r u e )  
         d e s c r i p t i o n   =   m o d e l s . T e x t F i e l d ( b l a n k = T r u e )  
         p u b l i c a t i o n _ t y p e   =   m o d e l s . C h a r F i e l d ( m a x _ l e n g t h = 5 0 ,   c h o i c e s = P U B L I C A T I O N _ T Y P E S )  
         f i l e   =   m o d e l s . F i l e F i e l d ( u p l o a d _ t o = ' p u b l i c a t i o n s / ' )  
         t h u m b n a i l   =   m o d e l s . I m a g e F i e l d ( u p l o a d _ t o = ' p u b l i c a t i o n _ t h u m b n a i l s / ' ,   b l a n k = T r u e ,   n u l l = T r u e )  
         p u b l i s h _ d a t e   =   m o d e l s . D a t e F i e l d ( )  
         i s _ f e a t u r e d   =   m o d e l s . B o o l e a n F i e l d ( d e f a u l t = F a l s e )  
         c r e a t e d _ a t   =   m o d e l s . D a t e T i m e F i e l d ( a u t o _ n o w _ a d d = T r u e )  
         u p d a t e d _ a t   =   m o d e l s . D a t e T i m e F i e l d ( a u t o _ n o w = T r u e )  
  
         c l a s s   M e t a :  
                 o r d e r i n g   =   [ ' - p u b l i s h _ d a t e ' ,   ' t i t l e ' ]  
  
         d e f   _ _ s t r _ _ ( s e l f ) :  
                 r e t u r n   s e l f . t i t l e  
  
         d e f   s a v e ( s e l f ,   * a r g s ,   * * k w a r g s ) :  
                 i f   n o t   s e l f . s l u g :  
                         s e l f . s l u g   =   s l u g i f y ( s e l f . t i t l e )  
                 s u p e r ( ) . s a v e ( * a r g s ,   * * k w a r g s )  
  
         d e f   g e t _ a b s o l u t e _ u r l ( s e l f ) :  
                 f r o m   d j a n g o . u r l s   i m p o r t   r e v e r s e  
                 r e t u r n   r e v e r s e ( ' m a i n : p u b l i c a t i o n _ d e t a i l ' ,   k w a r g s = { ' p k ' :   s e l f . p k } )  
  
  
 c l a s s   D o c u m e n t ( m o d e l s . M o d e l ) :  
         D O C U M E N T _ T Y P E S   =   [  
                 ( ' f o r m ' ,   ' F o r m ' ) ,  
                 ( ' t e m p l a t e ' ,   ' T e m p l a t e ' ) ,  
                 ( ' m a n u a l ' ,   ' M a n u a l ' ) ,  
                 ( ' r e p o r t ' ,   ' R e p o r t ' ) ,  
                 ( ' o t h e r ' ,   ' O t h e r ' ) ,  
         ]  
          
         t i t l e   =   m o d e l s . C h a r F i e l d ( m a x _ l e n g t h = 2 5 5 )  
         d e s c r i p t i o n   =   m o d e l s . T e x t F i e l d ( b l a n k = T r u e )  
         d o c u m e n t _ t y p e   =   m o d e l s . C h a r F i e l d ( m a x _ l e n g t h = 5 0 ,   c h o i c e s = D O C U M E N T _ T Y P E S )  
         f i l e   =   m o d e l s . F i l e F i e l d ( u p l o a d _ t o = ' d o c u m e n t s / ' )  
         c a t e g o r y   =   m o d e l s . F o r e i g n K e y ( ' C a t e g o r y ' ,   o n _ d e l e t e = m o d e l s . S E T _ N U L L ,   n u l l = T r u e ,   b l a n k = T r u e )  
         i s _ p u b l i c   =   m o d e l s . B o o l e a n F i e l d ( d e f a u l t = T r u e )  
         c r e a t e d _ a t   =   m o d e l s . D a t e T i m e F i e l d ( a u t o _ n o w _ a d d = T r u e )  
         u p d a t e d _ a t   =   m o d e l s . D a t e T i m e F i e l d ( a u t o _ n o w = T r u e )  
  
         c l a s s   M e t a :  
                 o r d e r i n g   =   [ ' - c r e a t e d _ a t ' ]  
  
         d e f   _ _ s t r _ _ ( s e l f ) :  
                 r e t u r n   s e l f . t i t l e  
  
         d e f   g e t _ f i l e _ e x t e n s i o n ( s e l f ) :  
                 i m p o r t   o s  
                 n a m e ,   e x t e n s i o n   =   o s . p a t h . s p l i t e x t ( s e l f . f i l e . n a m e )  
                 r e t u r n   e x t e n s i o n [ 1 : ] . u p p e r ( )   i f   e x t e n s i o n   e l s e   ' '  
 