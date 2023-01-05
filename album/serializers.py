from rest_framework import serializers

from .models import MediaAlbum, MediaFiles


class MediaFilesSerializer (serializers.ModelSerializer):

    class Meta:
        model = MediaFiles
        fields = ['image', 'document', 'id']


class MediaAlbumSerializer (serializers.ModelSerializer):

    media = MediaFilesSerializer(many=True, read_only=True)

    class Meta:
        model = MediaAlbum
        fields = ['media']
