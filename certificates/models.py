from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
import uuid
import secrets
import string

User = get_user_model()


class Certificate(models.Model):
    """Certificate of authenticity model"""
    
    PENDING = 'pending'
    ISSUED = 'issued'
    VERIFIED = 'verified'
    REVOKED = 'revoked'
    
    STATUS_CHOICES = [
        (PENDING, _('Pending')),
        (ISSUED, _('Issued')),
        (VERIFIED, _('Verified')),
        (REVOKED, _('Revoked')),
    ]
    
    # Certificate identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Related artwork and order
    artwork = models.OneToOneField('catalog.Artwork', on_delete=models.CASCADE, related_name='certificate')
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='certificates', null=True, blank=True)
    
    # Certificate details
    serial_number = models.CharField(_('serial number'), max_length=20, unique=True)
    status = models.CharField(_('status'), max_length=10, choices=STATUS_CHOICES, default=PENDING)
    
    # Certificate files
    pdf_file = models.FileField(_('PDF certificate'), upload_to='certificates/pdf/', blank=True, null=True)
    qr_code_image = models.ImageField(_('QR code'), upload_to='certificates/qr/', blank=True, null=True)
    
    # QR code data
    qr_url = models.URLField(_('QR verification URL'), blank=True)
    qr_data = models.JSONField(_('QR code data'), default=dict, blank=True)
    
    # Blockchain integration (optional)
    blockchain_network = models.CharField(_('blockchain network'), max_length=50, blank=True)
    token_id = models.CharField(_('token ID'), max_length=100, blank=True)
    contract_address = models.CharField(_('contract address'), max_length=100, blank=True)
    transaction_hash = models.CharField(_('transaction hash'), max_length=100, blank=True)
    
    # Certificate metadata
    issuer = models.CharField(_('issuer'), max_length=200, default='SafariCrafts')
    issued_to = models.CharField(_('issued to'), max_length=200, blank=True)
    issue_location = models.CharField(_('issue location'), max_length=200, default='Tanzania')
    
    # Verification tracking
    verification_count = models.PositiveIntegerField(_('verification count'), default=0)
    last_verified_at = models.DateTimeField(_('last verified at'), null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    issued_at = models.DateTimeField(_('issued at'), null=True, blank=True)
    
    class Meta:
        db_table = 'certificates'
        verbose_name = _('Certificate')
        verbose_name_plural = _('Certificates')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['serial_number']),
            models.Index(fields=['status']),
            models.Index(fields=['artwork']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.serial_number:
            self.serial_number = self.generate_serial_number()
        
        if not self.issued_to and self.order:
            self.issued_to = self.order.user.full_name or self.order.user.email
        
        super().save(*args, **kwargs)
    
    def generate_serial_number(self):
        """Generate unique serial number"""
        prefix = "SC"
        year = str(self.created_at.year if self.created_at else 2024)[-2:]
        
        # Generate random alphanumeric suffix
        suffix = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        
        serial = f"{prefix}{year}{suffix}"
        
        # Ensure uniqueness
        while Certificate.objects.filter(serial_number=serial).exists():
            suffix = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            serial = f"{prefix}{year}{suffix}"
        
        return serial
    
    def __str__(self):
        return f"Certificate {self.serial_number} - {self.artwork.title}"
    
    @property
    def verification_url(self):
        """Get the public verification URL"""
        from django.conf import settings
        from django.urls import reverse
        
        # This would be the frontend URL in production
        return f"https://safaricrafts.com/certificates/verify/{self.serial_number}"
    
    def increment_verification_count(self):
        """Increment verification count"""
        from django.utils import timezone
        
        self.verification_count += 1
        self.last_verified_at = timezone.now()
        self.save(update_fields=['verification_count', 'last_verified_at'])


class CertificateVerification(models.Model):
    """Track certificate verification attempts"""
    
    certificate = models.ForeignKey(Certificate, on_delete=models.CASCADE, related_name='verifications')
    
    # Verification details
    ip_address = models.GenericIPAddressField(_('IP address'), null=True, blank=True)
    user_agent = models.TextField(_('user agent'), blank=True)
    referrer = models.URLField(_('referrer'), blank=True)
    
    # Geographic data (if available)
    country = models.CharField(_('country'), max_length=100, blank=True)
    city = models.CharField(_('city'), max_length=100, blank=True)
    
    # Verification result
    is_valid = models.BooleanField(_('is valid'), default=True)
    
    verified_at = models.DateTimeField(_('verified at'), auto_now_add=True)
    
    class Meta:
        db_table = 'certificate_verifications'
        verbose_name = _('Certificate Verification')
        verbose_name_plural = _('Certificate Verifications')
        ordering = ['-verified_at']
        indexes = [
            models.Index(fields=['certificate', 'verified_at']),
            models.Index(fields=['ip_address']),
        ]
    
    def __str__(self):
        return f"Verification of {self.certificate.serial_number} at {self.verified_at}"


class CertificateTemplate(models.Model):
    """Template for generating certificates"""
    
    name = models.CharField(_('template name'), max_length=100)
    description = models.TextField(_('description'), blank=True)
    
    # Template files
    template_file = models.FileField(_('template file'), upload_to='certificate_templates/')
    preview_image = models.ImageField(_('preview image'), upload_to='certificate_previews/', blank=True, null=True)
    
    # Template configuration
    config = models.JSONField(_('template configuration'), default=dict, help_text=_('JSON configuration for template variables'))
    
    # Usage
    is_default = models.BooleanField(_('is default'), default=False)
    is_active = models.BooleanField(_('is active'), default=True)
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        db_table = 'certificate_templates'
        verbose_name = _('Certificate Template')
        verbose_name_plural = _('Certificate Templates')
        ordering = ['name']
    
    def __str__(self):
        return self.name
