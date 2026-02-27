from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from . import form
from django.contrib.auth.models import User
from .models import BulletJournalKey, Log
from datetime import timedelta, date
import datetime as python_datetime
import calendar
from django.contrib.auth import update_session_auth_hash
from django.utils import timezone
from .form import ProfileForm, CustomPasswordChangeForm

def format_logs(logs):
    """Helper function to format log objects for templates, adding symbol and color from the related Key."""
    return [
        {
            'id': log.id,
            'log': log, # Keep the object reference for those templates that use log.id/log.content directly
            'content': log.content,
            'symbol': log.key.symbol if log.key else '-',
            'color': log.key.color if log.key else '#000000',
            'created_at': log.created_at,
            'log_type': log.log_type,
        }
        for log in logs
    ]

# Create your views here.
def login(request):
    if request.user.is_authenticated:
        now = timezone.localdate()
        return redirect('daily_log', year=now.year, month=now.month, day=now.day)

    if request.method == "POST":
        login_form = form.LoginForm(request.POST)
        if login_form.is_valid():
            email = login_form.cleaned_data['email']
            password = login_form.cleaned_data['password']
            
            try:
                user = User.objects.get(email=email)
                username = user.username
                user = authenticate(username=username, password=password)
            except User.DoesNotExist:
                user = None
                
            if user is not None:
                if user.is_active:
                    auth_login(request, user)
                    messages.success(request, 'Successfully logged in.')
                    now = timezone.localdate()
                    return redirect('daily_log', year=now.year, month=now.month, day=now.day)
                else:
                    messages.error(request, 'Account is not active.')
            else:
                messages.error(request, 'Login failed. Please check your credentials.')
        else:
            messages.error(request, 'Please check the input fields.')
    else:
        login_form = form.LoginForm()
    return render(request, 'login.html', locals())

def index(request):
    if request.user.is_authenticated:
        now = timezone.localdate()
        return redirect('daily_log', year=now.year, month=now.month, day=now.day)
    else:
        return redirect('login')

@login_required
def key(request):
    if request.method == 'POST' and 'key_action' in request.POST:
        action = request.POST.get('key_action')
        key_id = request.POST.get('key_id')
        if action == 'edit' and key_id:
            key = get_object_or_404(BulletJournalKey, id=key_id, user=request.user)
            if key.is_default:
                messages.error(request, 'Cannot edit default Key.')
            else:
                key.symbol = request.POST.get('symbol')
                key.color = request.POST.get('color')
                key.save()
                messages.success(request, 'Key updated successfully.')
        elif action == 'delete' and key_id:
            key = get_object_or_404(BulletJournalKey, id=key_id, user=request.user)
            if key.is_default:
                messages.error(request, 'Cannot delete default Key.')
            else:
                key.delete()
                messages.success(request, 'Custom Key deleted successfully.')
        elif action == 'add':
            BulletJournalKey.objects.create(
                user=request.user,
                symbol=request.POST.get('symbol'),
                description=request.POST.get('description'),
                color=request.POST.get('color'),
                is_default=False
            )
            messages.success(request, 'Custom Key added successfully.')

    keys = BulletJournalKey.objects.filter(user=request.user)
    
    context = {
        'keys': keys,
    }
    return render(request, 'key.html', context)

@login_required
def yearly_log(request, year):
    yearly_logs = Log.objects.filter(
        user=request.user,
        log_type='yearly',
        year=year,
        is_deleted=False,
    ).select_related('key')

    previous_year = year - 1
    next_year = year + 1

    logs_with_details = format_logs(yearly_logs)
    
    keys = BulletJournalKey.objects.filter(user=request.user).exclude(
        description__in=['Completed Task', 'Migrated Task', 'Scheduled Task']
    )

    context = {
        'year': year,
        'logs_with_details': logs_with_details,
        'previous_year': previous_year,
        'next_year': next_year,
        'keys': keys,
    }
    return render(request, 'yearly_log.html', context)

@login_required
def monthly_log(request, year, month):
    today = timezone.localdate()
    
    # Determine the selected day
    selected_day = request.GET.get('day', today.day if today.year == year and today.month == month else 1)
    selected_day = int(selected_day)
    selected_date = date(year, month, selected_day)
    
    # Fetch daily logs for the selected date
    daily_logs = Log.objects.filter(
        user=request.user,
        log_type='daily',
        year=year,
        month=month,
        is_deleted=False
    ).select_related('key').order_by('day')

    selected_daily_logs = format_logs(daily_logs.filter(day=selected_day))

    # Fetch monthly logs
    monthly_logs = Log.objects.filter(
        user=request.user,
        log_type='monthly',
        year=year,
        month=month,
        is_deleted=False
    ).select_related('key')

    monthly_logs_details = format_logs(monthly_logs)

    # Generate the calendar for the month
    cal = calendar.Calendar()
    month_days = list(cal.itermonthdays(year, month))

    # Get previous and next month info
    previous_month_info, next_month_info = get_previous_next_months(year, month)
    keys = BulletJournalKey.objects.filter(user=request.user).exclude(
        description__in=['Completed Task', 'Migrated Task', 'Scheduled Task']
    )

    context = {
        'year': year,
        'month': month,
        'month_days': month_days,
        'selected_date': selected_date,
        'selected_daily_logs': selected_daily_logs,
        'monthly_logs': monthly_logs_details,
        'previous_month_info': previous_month_info,
        'next_month_info': next_month_info,
        'today': today,
        'keys': keys,
    }
    return render(request, 'monthly_log.html', context)

@login_required
def weekly_log(request, year, week):
    from django.db.models import Q

    week_dates = get_week_date_range(year, week)
    
    date_queries = Q()
    for d in week_dates:
        date_queries |= Q(year=d.year, month=d.month, day=d.day)

    daily_logs = Log.objects.filter(
        date_queries,
        user=request.user,
        log_type='daily',
        is_deleted=False
    ).select_related('key').order_by('month', 'day')

    weekly_logs = Log.objects.filter(
        user=request.user,
        log_type='weekly',
        year=year,
        week=week,
        is_deleted=False
    ).select_related('key')


    # Use only date part for logs_by_date
    logs_by_date = {date: [] for date in week_dates}

    for log_detail in format_logs(daily_logs):
        log_obj = log_detail['log']
        log_date = date(log_obj.year, log_obj.month, log_obj.day)
        logs_by_date[log_date].append(log_detail)

    previous_week_info, next_week_info = get_previous_next_weeks(year, week)
    keys = BulletJournalKey.objects.filter(user=request.user).exclude(
        description__in=['Completed Task', 'Migrated Task', 'Scheduled Task']
    )

    context = {
        'year': year,
        'week': week,
        'week_dates': week_dates,
        'logs_by_date': logs_by_date,
        'weekly_logs': weekly_logs,
        'previous_week_info': previous_week_info,
        'next_week_info': next_week_info,
        'keys': keys,
    }
    return render(request, 'weekly_log.html', context)

@login_required
def daily_log(request, year, month, day):
    # Constructing standard py_date which serves the request context
    req_date = date(year, month, day)
    previous_day = req_date - timedelta(days=1)
    next_day = req_date + timedelta(days=1)

    if request.method == 'POST':
        content = request.POST.get('content')
        key_id = request.POST.get('key_id')
        key = BulletJournalKey.objects.get(id=key_id) if key_id else None
        log_type = request.POST.get('log_type', 'daily')

        year = request.POST.get('day_year') or request.POST.get('week_year') or request.POST.get('month_year') or request.POST.get('yearly_year')
        month = request.POST.get('day_month') or request.POST.get('month_number')
        week = request.POST.get('week_number')
        day = request.POST.get('day_number')
        
        if log_type == 'daily':
            log_year, log_month, log_week, log_day = year, month, None, day
        elif log_type == 'weekly':
            log_year, log_month, log_week, log_day = year, None, week, None
        elif log_type == 'monthly':
            log_year, log_month, log_week, log_day = year, month, None, None
        elif log_type == 'yearly':
            log_year, log_month, log_week, log_day = year, None, None, None

        Log.objects.create(
            user=request.user, title=content, content=content, key=key,
            log_type=log_type, year=log_year,
            month=log_month, week=log_week, day=log_day
        )
        
        if log_type == 'daily':
            return redirect('daily_log', year=log_year, month=log_month, day=log_day)
        elif log_type == 'weekly':
            return redirect('weekly_log', year=log_year, week=log_week)
        elif log_type == 'monthly':
            return redirect('monthly_log', year=log_year, month=log_month)
        elif log_type == 'yearly':
            return redirect('yearly_log', year=log_year)
        else:
            return redirect('dashboard')
    
    logs = Log.objects.filter(
        user=request.user, year=year, month=month, day=day, log_type='daily', is_deleted=False
    ).select_related('key')
    keys = BulletJournalKey.objects.filter(user=request.user).exclude(
        description__in=['Completed Task', 'Migrated Task', 'Scheduled Task']
    )

    logs_with_details = format_logs(logs)

    context = {
        'logs_with_details': logs_with_details,
        'keys': keys,
        'date': req_date,
        'previous_day': previous_day,
        'next_day': next_day,
        'default_log_type': 'daily',
        'default_date': req_date.strftime('%Y-%m-%d')
    }
    return render(request, 'daily_log.html', context)


@login_required
def migrate_task(request, log_type, log_id):
    log_entry = get_log_entry(log_type, log_id, request.user)
    if log_entry is None:
        messages.error(request, 'Invalid log type.')
        return redirect('dashboard')

    if log_type == 'daily':
        current_date = date(log_entry.year, log_entry.month, log_entry.day)
        next_date = current_date + timedelta(days=1)
        Log.objects.create(
            user=request.user, title=log_entry.title, content=log_entry.content,
            key=log_entry.key, log_type='daily',
            year=next_date.year, month=next_date.month, day=next_date.day
        )
    elif log_type == 'weekly':
        current_week_start = get_week_date_range(log_entry.year, log_entry.week)[0]
        next_week_date = current_week_start + timedelta(days=7)
        iso_year, iso_week, _ = next_week_date.isocalendar()
        Log.objects.create(
            user=request.user, title=log_entry.title, content=log_entry.content,
            key=log_entry.key, log_type='weekly',
            year=iso_year, week=iso_week
        )
    elif log_type == 'monthly':
        if log_entry.month == 12:
            next_month = 1
            next_year = log_entry.year + 1
        else:
            next_month = log_entry.month + 1
            next_year = log_entry.year
            
        Log.objects.create(
            user=request.user, title=log_entry.title, content=log_entry.content,
            key=log_entry.key, log_type='monthly',
            year=next_year, month=next_month
        )
    elif log_type == 'yearly':
        next_year = log_entry.year + 1
        Log.objects.create(
            user=request.user, title=log_entry.title, content=log_entry.content,
            key=log_entry.key, log_type='yearly',
            year=next_year
        )

    migrated_key = BulletJournalKey.objects.filter(user=request.user, description='Migrated Task').first()
    if migrated_key:
        log_entry.key = migrated_key
    log_entry.save()
    messages.success(request, f'{log_type.capitalize()} task migrated successfully.')
    return redirect_to_log_page(log_entry, log_type)



@login_required
def schedule_task(request, log_type, log_id):
    log_entry = get_log_entry(log_type, log_id, request.user)
    if log_entry is None:
        messages.error(request, 'Invalid log type.')
        return redirect('dashboard')

    if request.method == 'POST':
        scheduled_date = request.POST.get('scheduled_date')
        if scheduled_date:
            scheduled_date = python_datetime.datetime.strptime(scheduled_date, '%Y-%m-%d').date()
            iso_year, iso_week, _ = scheduled_date.isocalendar()
            
            Log.objects.create(
                user=request.user,
                title=log_entry.title,
                content=log_entry.content,
                key=log_entry.key,
                log_type=log_entry.log_type,
                year=iso_year if log_entry.log_type == 'weekly' else scheduled_date.year,
                month=None if log_entry.log_type == 'weekly' else scheduled_date.month,
                week=iso_week,
                day=None if log_entry.log_type == 'weekly' else scheduled_date.day
            )
            
            scheduled_key = BulletJournalKey.objects.filter(user=request.user, description='Scheduled Task').first()
            if scheduled_key:
                log_entry.key = scheduled_key
                log_entry.save()
            
            messages.success(request, 'Task scheduled successfully.')
        
        return redirect_to_log_page(log_entry, log_type)

    context = {
        'log_entry': log_entry,
        'log_type': log_type,
    }
    return render(request, 'schedule_task.html', context)


@login_required
def delete_task(request, log_type, log_id):
    log_entry = get_log_entry(log_type, log_id, request.user)

    if log_entry is None:
        messages.error(request, 'Invalid log type.')
        return redirect('/')

    log_entry.is_deleted = True
    log_entry.save()
    messages.success(request, f'{log_type.capitalize()} task marked as deleted.')
    return redirect_to_log_page(log_entry, log_type)

@login_required
def edit_log_inline(request, log_type, log_id):
    log_entry = get_log_entry(log_type, log_id, request.user)
    if log_entry is None:
        messages.error(request, 'Invalid log type.')
        return redirect('dashboard')

    if request.method == 'POST':
        content = request.POST.get('content')
        key_id = request.POST.get('key_id')
        key = BulletJournalKey.objects.get(id=key_id) if key_id else None
        log_entry.content = content
        log_entry.key = key
        log_entry.save()
        messages.success(request, 'Log entry updated successfully.')
        return redirect_to_log_page(log_entry, log_type)

    context = {
        'log_entry': log_entry,
        'log_type': log_type,
    }
    return render(request, 'edit_log_inline.html', context)

def redirect_to_log_page(request, log_entry, log_type):
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    
    if log_type == 'daily':
        return redirect('daily_log', year=log_entry.year, month=log_entry.month, day=log_entry.day)
    elif log_type == 'weekly':
        return redirect('weekly_log', year=log_entry.year, week=log_entry.week)
    elif log_type == 'monthly':
        return redirect('monthly_log', year=log_entry.year, month=log_entry.month)
    elif log_type == 'yearly':
        return redirect('yearly_log', year=log_entry.year)
    elif log_type == 'note':
        return redirect('note')
    else:
        return redirect('dashboard')

def get_log_entry(log_type, log_id, user):
    return get_object_or_404(Log, id=log_id, user=user, log_type=log_type)

@login_required
def toggle_log_status(request, log_type, log_id):
    if request.method == 'POST':
        log_entry = get_log_entry(log_type, log_id, request.user)
        if log_entry and log_entry.key:
            if log_entry.key.description == 'Task':
                completed_key = BulletJournalKey.objects.filter(user=request.user, description='Completed Task').first()
                if completed_key:
                    log_entry.key = completed_key
                    log_entry.save()
            elif log_entry.key.description == 'Completed Task':
                task_key = BulletJournalKey.objects.filter(user=request.user, description='Task').first()
                if task_key:
                    log_entry.key = task_key
                    log_entry.save()
        return redirect_to_log_page(log_entry, log_type)
    return redirect('dashboard')

@login_required
def note(request):
    notes = Log.objects.filter(
        user=request.user, key__description="Note", is_deleted=False
    ).select_related('key').order_by('-created_at')
    
    logs_with_details = format_logs(notes)

    context = {
        'logs_with_details': logs_with_details,
    }
    return render(request, 'note.html', context)

@login_required
def setting(request):
    if request.method == 'POST':
        # 初始化表单
        profile_form = ProfileForm(request.POST, instance=request.user)
        password_form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        
        if 'profile_submit' in request.POST:
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Your profile has been updated successfully.')
                return redirect('setting')
            else:
                messages.error(request, 'Please correct the errors below in your profile.')

        elif 'password_submit' in request.POST:
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Your password was successfully updated.')
                return redirect('setting') 
            else:
                messages.error(request, 'Please correct the errors below in your password.')

    else:
        profile_form = ProfileForm(instance=request.user)
        password_form = CustomPasswordChangeForm(user=request.user)

    context = {
        'profile_form': profile_form,
        'password_form': password_form,
    }
    return render(request, 'setting.html', context)


def logout(request):
    auth_logout(request)
    messages.success(request, '成功登出了')
    return redirect('/')

@login_required
def add_log_entry(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        key_id = request.POST.get('key_id')
        key = BulletJournalKey.objects.get(id=key_id) if key_id else None
        log_type = request.POST.get('log_type')

        entry_year = entry_month = entry_week = entry_day = None

        if log_type == 'daily':
            entry_date = request.POST.get('date_daily')
            entry_date = python_datetime.datetime.strptime(entry_date, '%Y-%m-%d').date()
            entry_year = entry_date.year
            entry_month = entry_date.month
            entry_day = entry_date.day
        elif log_type == 'weekly':
            entry_year = int(request.POST.get('week_year'))
            entry_week = int(request.POST.get('week_number'))
        elif log_type == 'monthly':
            entry_year = int(request.POST.get('month_year'))
            entry_month = int(request.POST.get('month_number'))
        elif log_type == 'yearly':
            entry_year = int(request.POST.get('yearly_year'))

        Log.objects.create(
            user=request.user,
            title=content,
            content=content,
            key=key,
            log_type=log_type,
            year=entry_year,
            month=entry_month,
            week=entry_week,
            day=entry_day
        )
        messages.success(request, 'Log entry added successfully.')
        return redirect('dashboard')

    keys = BulletJournalKey.objects.filter(user=request.user)
    return render(request, 'task_form.html', {'keys': keys})

def get_week_date_range(year, week):
    d = python_datetime.datetime.strptime(f'{year}-W{week:02d}-1', "%G-W%V-%u").date()
    week_dates = [d + timedelta(days=i) for i in range(7)]
    return week_dates


def get_previous_next_weeks(year, week):
    current_week_start = get_week_date_range(year, week)[0]
    
    prev_week_start = current_week_start - timedelta(days=7)
    next_week_start = current_week_start + timedelta(days=7)
    
    prev_year, prev_week, _ = prev_week_start.isocalendar()
    next_year, next_week, _ = next_week_start.isocalendar()

    return (prev_year, prev_week), (next_year, next_week)

def get_previous_next_months(year, month):
    from datetime import date

    if month == 1:
        previous_month = 12
        previous_year = year - 1
    else:
        previous_month = month - 1
        previous_year = year

    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year

    return (previous_year, previous_month), (next_year, next_month)
