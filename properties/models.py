import uuid
from django.db import models
from users.models import User, Company
from django.contrib.postgres.fields import ArrayField
from album.models import MediaFiles, MediaAlbum


MODERATION_STATUS_CHOICES = [
    ('PENDING', 'pending'),
    ('APPROVED', 'approved'),
    ('REJECTED', 'rejected')
]
COMPLETION_STATUS_CHOICES = [
    ('IN-PROGRESS', 'construction in progress'),
    ('COMPLETED', 'contruction completed'),
]



class Property(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=256, blank=False)
    agent = models.ForeignKey(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=256, blank=True)
    description = models.TextField(blank=True)
    moderation_status = models.CharField(
        choices=MODERATION_STATUS_CHOICES,
        max_length=255, 
        default=MODERATION_STATUS_CHOICES[0][0] )
    archived  = models.BooleanField(default=False)
    completion_status = models.CharField(
        max_length=255,
        choices=COMPLETION_STATUS_CHOICES,
        default=COMPLETION_STATUS_CHOICES[0][0]
        )
    apartment_type = models.CharField(max_length=255, blank=False)
    address = models.CharField(max_length=255, blank=False)
    city = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=50, blank=False)
    country = models.CharField(max_length=50, blank=False)
    percentage_discount = models.PositiveIntegerField(null=True)
    promotion_closing_date = models.DateField(null=True)
    promotion_type = models.CharField(max_length=255, blank=True)
    other_deals = models.TextField(blank=True)
    image_album = models.OneToOneField(MediaAlbum, related_name='image_album', on_delete=models.CASCADE, null=True)
    document_album = models.OneToOneField(
        MediaAlbum, related_name='document_album', on_delete=models.CASCADE, null=True)
    number_of_bedrooms = models.PositiveIntegerField(null=True)
    number_of_toilets = models.PositiveIntegerField(null=True)
    benefits = ArrayField(models.CharField(max_length=255), default=list)
    amenities = ArrayField(models.CharField(max_length=255), default=list)
    # bathroom_description = models.TextField(blank=True)
    ERF_size = models.CharField(blank=True, max_length=256)
    dining_area = models.CharField(blank=True, max_length=256)
    cross_streets = ArrayField(models.CharField(max_length=255), default=list)
    landmarks = ArrayField(models.CharField(max_length=255), default=list)
    floor_size = models.CharField(max_length=255, blank=True)
    date_built = models.DateField(null=True)
    # listing_date = models.DateField(null=True)
    # additional_details = models.JSONField(default=dict)
    price_per_share = models.PositiveBigIntegerField(null=True)
    completion_cost = models.PositiveBigIntegerField(null=True)
    completion_date = models.DateField(null=True)
    percentage_completed = models.PositiveIntegerField(null=True)
    zip_code = models.PositiveIntegerField(null=True)
    total_number_of_shares = models.PositiveIntegerField(null=True)
    total_property_cost = models.PositiveBigIntegerField(null=True)
    expected_ROI    = models.PositiveBigIntegerField(null=True)
    area_rent_rolls = models.CharField(max_length=255, blank=True)
    scheduled_stays = ArrayField(
        ArrayField(
            models.DateField(),
            default=list
            ), default=list)
    other_incentives = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Properties'

    def get_images(self):
        if not self.image_album:
            return []
        setattr(self,'images', MediaFiles.objects.filter(album=self.image_album))
        return self.images

    def get_documents(self):
        if not self.document_album:
            return []
        setattr(self, 'documents', MediaFiles.objects.filter(album=self.document_album))
        return self.documents


class ShoppingCart(models.Model):

    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    property = models.ForeignKey(to=Property, on_delete=models.CASCADE)
    quantity = models.IntegerField(null=False, default=1)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ShoppingCart'
