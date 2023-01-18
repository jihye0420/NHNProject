from rest_framework import serializers
from nhn.models import Post

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['url', 'title', 'published_datetime', 'body', 'attachment_list']