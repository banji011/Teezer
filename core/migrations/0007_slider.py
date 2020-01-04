# Generated by Django 3.0.1 on 2020-01-02 20:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_item_timestamp'),
    ]

    operations = [
        migrations.CreateModel(
            name='Slider',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='marketing/images/')),
                ('order', models.IntegerField(default=0)),
                ('url_link', models.CharField(blank=True, max_length=250, null=True)),
                ('sub_heading', models.CharField(blank=True, max_length=120, null=True)),
                ('side_heading', models.CharField(blank=True, max_length=120, null=True)),
                ('header_text', models.CharField(blank=True, max_length=120, null=True)),
                ('text', models.CharField(blank=True, max_length=300, null=True)),
                ('active', models.BooleanField(default=False)),
                ('featured', models.BooleanField(default=False)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('start_date', models.DateTimeField(blank=True, null=True)),
                ('end_date', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'ordering': ['order', '-start_date', '-end_date'],
            },
        ),
    ]
