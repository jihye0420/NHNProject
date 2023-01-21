from django.db import models


# Create your models here.
class Post(models.Model):
    url = models.URLField(verbose_name='게시물 URL')
    title = models.CharField(max_length=255, verbose_name='게시물 제목')
    published_datetime = models.DateTimeField(null=True, verbose_name='게시물 발행일(작성일자)')
    body = models.TextField(null=True, verbose_name='게시물 HTML')
    attachment_list = models.TextField(null=True,verbose_name='첨부파일 이름 리스트')
    category = models.CharField(max_length=255, verbose_name='게시물 수집 대상')

    class Meta:
        managed = True
        db_table = 'post'
