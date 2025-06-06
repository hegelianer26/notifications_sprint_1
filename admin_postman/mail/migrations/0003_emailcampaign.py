# Generated by Django 5.0.3 on 2024-04-01 14:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mail', '0002_alter_emailtemplate_content'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailCampaign',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('duration', models.DurationField()),
                ('time', models.DateTimeField()),
                ('user_gropus', models.CharField(default='basic', max_length=100)),
                ('active', models.BooleanField(default=False)),
                ('template', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mail.emailtemplate')),
            ],
        ),
    ]
