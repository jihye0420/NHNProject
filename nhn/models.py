from django.db import models


# Create your models here.
class Post(models.Model):
    url = models.URLField(primary_key=True, verbose_name='게시물 URL')
    title = models.CharField(max_length=255, verbose_name='게시물 제목')
    published_datetime = models.DateTimeField(verbose_name='게시물 발행일(작성일자)')
    body = models.TextField(verbose_name='게시물 HTML')
    attachment_list = models.TextField(verbose_name='첨부파일 이름 리스트')

    class Meta:
        managed = True
        db_table = 'post'
