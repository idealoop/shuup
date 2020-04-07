# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2020-04-07 11:51
from __future__ import unicode_literals

from django.db import migrations
import django.db.models.deletion
import parler.fields


class Migration(migrations.Migration):

    dependencies = [
        ('shuup_tasks', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tasktypetranslation',
            name='master',
            field=parler.fields.TranslationsForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='shuup_tasks.TaskType'),
        ),
    ]
