from django.contrib import admin
from .models import BulletJournalKey, Log

class BulletJournalKeyAdmin(admin.ModelAdmin):
    list_display = ('user', 'symbol', 'description', 'color', 'is_default')
    search_fields = ('user__username', 'symbol', 'description')
    list_filter = ('symbol', 'is_default')

class LogAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'log_type', 'year', 'month', 'week', 'day', 'is_deleted', 'created_at')
    search_fields = ('title', 'user__username', 'content')
    list_filter = ('log_type', 'year', 'month', 'week', 'day', 'is_deleted')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'

    fieldsets = (
        (None, {
            'fields': ('title', 'user', 'key', 'content')
        }),
        ('Date Information', {
            'fields': ('year', 'month', 'week', 'day')
        }),
        ('Other Information', {
            'fields': ('log_type', 'is_deleted')
        }),
    )

    list_display_links = ('title', 'user')
    list_editable = ('is_deleted',)
    list_per_page = 20

    def save_model(self, request, obj, form, change):
        if not obj.pk:  # only set the log_type on creation
            if obj.year and not obj.month and not obj.week and not obj.day:
                obj.log_type = 'yearly'
            elif obj.year and obj.month and not obj.week and not obj.day:
                obj.log_type = 'monthly'
            elif obj.year and not obj.month and obj.week and not obj.day:
                obj.log_type = 'weekly'
            elif obj.year and obj.month and obj.day:
                obj.log_type = 'daily'
            else:
                obj.log_type = 'unplanned'
        super().save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'key':
            kwargs['queryset'] = BulletJournalKey.objects.filter(user=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(BulletJournalKey, BulletJournalKeyAdmin)
admin.site.register(Log, LogAdmin)




