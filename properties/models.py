import uuid
from django.db import models
from users.models import User
from django.contrib.postgres.fields import ArrayField

MODERATION_STATUS_CHOICES = [
    ('PENDING', 'pending'),
    ('APPROVED', 'approved'),
    ('REJECTED', 'rejected')
]
COMPLETION_STATUS_CHOICES = [
    ('IN-PROGRESS', 'construction in progress'),
    ('COMPLETED', 'contruction completed'),
]
MEDIA_TYPE_CHOICES = [
    ('IMAGE', 'images'),
    ('DOCUMENT', 'documents'),
]


class MediaAlbum(models.Model):
    
    class Meta:
        db_table = 'MediaAlbums'

def get_upload_path(instance, filename):
    model = instance.album.__module__.split('.')[0]
    name = model.replace(' ', '_')
    return f'{name}/images/{filename}'


def get_upload_path_for_document(instance, filename):
    model = instance.album.__module__.split('.')[0]
    name = model.replace(' ', '_')
    return f'{name}/documents/{filename}'

class MediaFiles(models.Model):
    name = models.CharField(max_length=256, blank=True, null=True)
    image = models.ImageField(
        upload_to=get_upload_path, default='', null=True, blank=True)
    document = models.FileField(upload_to=get_upload_path_for_document, null=True, blank=True)
    media_type = models.CharField(
        max_length=256,
        choices= MEDIA_TYPE_CHOICES,
        default= MEDIA_TYPE_CHOICES[0][0]
        )
    album = models.ForeignKey(
        MediaAlbum, related_name='media', on_delete=models.CASCADE)

    class Meta:
        db_table = 'MediaFiles'

    def delete_image_from_storage(self):
        if self.image:
            self.image.delete(save=False)

    def delete_document_from_storage(self):
        if self.document:
            self.document.delete(save=False)


class Property(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=256, blank=False)
    agent = models.ForeignKey(User, on_delete=models.CASCADE)
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

    def attach_images(self):
        self.images = MediaFiles.objects.filter(album=self.image_album).values()

    def attach_documents(self):
        self.documents = MediaFiles.objects.filter(album=self.document_album).values()

