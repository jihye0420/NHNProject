from django.http import HttpResponse
from rest_framework.decorators import api_view


# Create your views here.
@api_view(['GET'])
def test(request):
    return HttpResponse("test nhn api")