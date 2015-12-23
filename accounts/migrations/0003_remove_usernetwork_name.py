# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_usernetwork'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usernetwork',
            name='name',
        ),
    ]
