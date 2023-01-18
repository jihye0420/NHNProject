import traceback

from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets


from .models import Post
from .serializers import PostSerializer


# Create your views here.
@api_view(['GET'])
def test(request):
    return HttpResponse("test nhn api")


class PostPagination(PageNumberPagination):
    page_size = 10


#게시물 조회
class PostView(APIView):
    # pagination_class = PostPagination

    def get(self, request):
        try:
            # res = {}
            # todo: 10개 게시물만 가져오기!
            query_set = Post.objects.all().order_by('-id')[:10]
            # query_set = Post.objects.all().order_by('-id')
            post_data = PostSerializer(query_set, many=True).data
            # res = list(post_data)
            print(post_data)
            print(PostSerializer(query_set, many=True))
            return Response(list(post_data))
        except:
            print(traceback.print_exc())
            return Response({"message": "error"})


# 게시물 조회
# class PostViewSet(viewsets.ModelviewSet):
#     query_set = Post.objects.all().order_by('-id')
#     serializer_class = PostSerializer
#     pagination_class = PostPagination
#     return Response(Po)

