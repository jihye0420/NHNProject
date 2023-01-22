import traceback

from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Post
from .serializers import PostSerializer


# Create your views here.
@api_view(['GET'])
def test(request):
    return HttpResponse("test nhn api")


class PostPagination(PageNumberPagination):
    page_size = 10


# 게시물 조회
class PostView(APIView):
    # pagination_class = PostPagination

    def get(self, request):
        try:
            res = []
            # todo: 10개 게시물만 가져오기!
            # todo: 카테고리 수정
            for category in ['iam_school', 'naver_blog', 'bbc_news']:
                query_set = Post.objects.filter(category=category).order_by('-published_datetime')[:10]
                result = PostSerializer(query_set, many=True).data
                print(result)
                print(type(result))
                # res.append(list(result))
                # res.append(result) # todo: 출력 형식 [[], [], [], ...]
                res += result  # todo: 출력 형식 [{}, {}, ...]
                print(res)
            return Response(res)
        except:
            print(traceback.print_exc())
            return Response({"message": "error"})


# 게시물 조회
class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    pagination_class = PostPagination
    queryset = Post.objects.filter(category='iam_school').order_by('-published_datetime')
    # return Response(serializer.data)

# Minxin, APIView generic
