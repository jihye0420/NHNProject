from rest_framework import serializers

from nhn.models import Post


def string_to_list(string):
    return string.split(',')


class PostSerializer(serializers.ModelSerializer):
    attachment_list = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['url', 'title', 'published_datetime', 'body', 'attachment_list']

    def get_attachment_list(self, obj):
        return string_to_list(obj.attachment_list)
