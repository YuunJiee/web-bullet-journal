# Generated by Django 4.2.13 on 2024-06-16 14:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('journal', '0004_dailylog_is_deleted_monthlylog_is_deleted_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='BulletJournalKey',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('symbol', models.CharField(max_length=10)),
                ('description', models.CharField(max_length=100)),
                ('color', models.CharField(default='#000000', max_length=7)),
                ('is_default', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterField(
            model_name='dailylog',
            name='key',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='journal.bulletjournalkey'),
        ),
        migrations.AlterField(
            model_name='monthlylog',
            name='key',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='journal.bulletjournalkey'),
        ),
        migrations.AlterField(
            model_name='weeklylog',
            name='key',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='journal.bulletjournalkey'),
        ),
        migrations.AlterField(
            model_name='yearlylog',
            name='key',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='journal.bulletjournalkey'),
        ),
        migrations.DeleteModel(
            name='Key',
        ),
    ]
