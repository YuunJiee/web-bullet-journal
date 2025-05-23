from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('accounts/', include('django_registration.backends.activation.urls')),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
    path('log/<int:year>y/', views.yearly_log, name='yearly_log'),
    path('log/<int:year>y/<int:month>m/', views.monthly_log, name='monthly_log'),
    path('log/<int:year>y/<int:month>m/<int:day>d/', views.daily_log, name='daily_log'),
    path('log/<int:year>y/<int:week>w/', views.weekly_log, name='weekly_log'),
    path('log/schedule/<str:log_type>/<int:log_id>/', views.schedule_task, name='schedule_task'),
    path('log/migrate/<str:log_type>/<int:log_id>/', views.migrate_task, name='migrate_task'),
    path('log/edit/inline/<str:log_type>/<int:log_id>/', views.edit_log_inline, name='edit_log_inline'),
    path('log/delete/<str:log_type>/<int:log_id>/', views.delete_task, name='delete_task'),
    path('key/', views.key, name='key'),
    path('note/', views.note, name='note'),
    path('setting/', views.setting, name='setting'),
    path('logout/', views.logout, name='logout'),
]
