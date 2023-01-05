from django.db import models
from django.utils import timezone


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
    date = str(timezone.now().date())
    return f'{name}/images/{date}/{filename}'


def get_upload_path_for_document(instance, filename):
    model = instance.album.__module__.split('.')[0]
    name = model.replace(' ', '_')
    date = str(timezone.now().date())
    return f'{name}/documents/{date}/{filename}'


class MediaFiles(models.Model):
    name = models.CharField(max_length=256, blank=True, null=True)
    image = models.ImageField(
        upload_to=get_upload_path, default='', null=True, blank=True)
    document = models.FileField(
        upload_to=get_upload_path_for_document, null=True, blank=True)
    media_type = models.CharField(
        max_length=256,
        choices=MEDIA_TYPE_CHOICES,
        default=MEDIA_TYPE_CHOICES[0][0]
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
