# Generated by Django 4.1.5 on 2023-01-21 09:10

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField(verbose_name='게시물 URL')),
                ('title', models.CharField(max_length=255, verbose_name='게시물 제목')),
                ('published_datetime', models.DateTimeField(verbose_name='게시물 발행일(작성일자)')),
                ('body', models.TextField(verbose_name='게시물 HTML')),
                ('attachment_list', models.TextField(verbose_name='첨부파일 이름 리스트')),
                ('category', models.CharField(max_length=255, verbose_name='게시물 수집 대상')),
            ],
            options={
                'db_table': 'post',
                'managed': True,
            },
        ),
    ]
