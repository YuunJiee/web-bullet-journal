# Generated by Django 4.2.13 on 2024-06-20 13:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('journal', '0006_auto_20240616_2301'),
    ]

    operations = [
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('log_type', models.CharField(choices=[('yearly', 'Yearly'), ('monthly', 'Monthly'), ('weekly', 'Weekly'), ('daily', 'Daily'), ('unplanned', 'Unplanned')], default='unplanned', max_length=10)),
                ('year', models.IntegerField(blank=True, null=True)),
                ('month', models.IntegerField(blank=True, null=True)),
                ('week', models.IntegerField(blank=True, null=True)),
                ('day', models.IntegerField(blank=True, null=True)),
                ('content', models.TextField()),
                ('is_deleted', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('key', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='journal.bulletjournalkey')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.RemoveField(
            model_name='monthlylog',
            name='key',
        ),
        migrations.RemoveField(
            model_name='monthlylog',
            name='user',
        ),
        migrations.RemoveField(
            model_name='weeklylog',
            name='key',
        ),
        migrations.RemoveField(
            model_name='weeklylog',
            name='user',
        ),
        migrations.RemoveField(
            model_name='yearlylog',
            name='key',
        ),
        migrations.RemoveField(
            model_name='yearlylog',
            name='user',
        ),
        migrations.DeleteModel(
            name='DailyLog',
        ),
        migrations.DeleteModel(
            name='MonthlyLog',
        ),
        migrations.DeleteModel(
            name='WeeklyLog',
        ),
        migrations.DeleteModel(
            name='YearlyLog',
        ),
    ]
