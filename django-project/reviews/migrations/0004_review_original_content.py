# Generated manually for adding original_content field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0003_reviewlike'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='original_content',
            field=models.TextField(blank=True, help_text='원문 리뷰 (번역 전 내용)'),
        ),
    ]

