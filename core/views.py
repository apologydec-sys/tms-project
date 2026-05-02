from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.db.models import Count
from django.utils import timezone
from .models import (
    User, Department, Subject, TeacherProfile,
    ClassSchedule, Notification, Attendance, TeacherMessage
)
from .forms import (
    TeacherProfileForm, ClassScheduleForm, CustomUserCreationForm,
    AdminRegisterTeacherForm, AttendanceForm, TeacherMessageForm, AdminReplyForm
)



def is_admin(user):
    return user.is_authenticated and user.is_admin

def is_teacher(user):
    return user.is_authenticated and user.is_teacher


def landing_page(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'core/landing.html')




def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


def register_teacher(request):
    """Staff registration with serial number validation."""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful. Please log in.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'core/register.html', {'form': form})


@login_required
def dashboard_redirect(request):
    if request.user.is_admin:
        return redirect('admin_dashboard')
    elif request.user.is_teacher:
        return redirect('teacher_dashboard')
    else:
        logout(request)
        return redirect('login')



@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    teachers_count = User.objects.filter(is_teacher=True).count()
    recent_teachers = TeacherProfile.objects.select_related('user', 'department').order_by('-id')[:5]
    departments = Department.objects.annotate(num_subjects=Count('subjects'))
    unread_messages_count = TeacherMessage.objects.filter(status='pending').count()

    if request.method == 'POST':
        schedule_form = ClassScheduleForm(request.POST)
        if schedule_form.is_valid():
            schedule = schedule_form.save()
            Notification.objects.create(
                teacher=schedule.teacher,
                message=(
                    f"New class scheduled: {schedule.subject.name} on "
                    f"{schedule.date} at {schedule.time}"
                    + (f" in room {schedule.room}." if schedule.room else ".")
                )
            )
            messages.success(request, 'Class scheduled successfully and teacher notified.')
            return redirect('admin_dashboard')
    else:
        schedule_form = ClassScheduleForm()
        schedule_form.fields['teacher'].queryset = User.objects.filter(is_teacher=True)

    context = {
        'teachers_count': teachers_count,
        'recent_teachers': recent_teachers,
        'departments': departments,
        'schedule_form': schedule_form,
        'unread_messages_count': unread_messages_count,
    }
    return render(request, 'core/admin_dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def admin_register_teacher(request):
    """Admin registers a new teacher account (unlimited)."""
    if request.method == 'POST':
        form = AdminRegisterTeacherForm(request.POST)
        if form.is_valid():
            teacher = form.save()
            messages.success(
                request,
                f"Teacher '{teacher.full_name or teacher.username}' registered successfully!"
            )
            return redirect('admin_teacher_list')
    else:
        form = AdminRegisterTeacherForm()
    return render(request, 'core/admin_register_teacher.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def admin_teacher_list(request):
    """List all registered teachers."""
    teachers = User.objects.filter(is_teacher=True).select_related('teacher_profile').order_by('-date_joined')
    return render(request, 'core/admin_teacher_list.html', {'teachers': teachers})


@login_required
@user_passes_test(is_admin)
def admin_delete_teacher(request, teacher_id):
    """Delete a teacher account."""
    teacher = get_object_or_404(User, id=teacher_id, is_teacher=True)
    if request.method == 'POST':
        name = teacher.full_name or teacher.username
        teacher.delete()
        messages.success(request, f"Teacher '{name}' has been removed.")
        return redirect('admin_teacher_list')
    return render(request, 'core/admin_confirm_delete.html', {'teacher': teacher})




@login_required
@user_passes_test(is_admin)
def admin_attendance(request):
    """Admin views & marks teacher attendance."""
    today = timezone.now().date()
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            attendance = form.save(commit=False)
            attendance.marked_by = request.user
            
            Attendance.objects.update_or_create(
                teacher=attendance.teacher,
                date=attendance.date,
                defaults={
                    'status': attendance.status,
                    'notes': attendance.notes,
                    'marked_by': request.user,
                }
            )
            messages.success(request, 'Attendance recorded.')
            return redirect('admin_attendance')
    else:
        form = AttendanceForm(initial={'date': today})

    
    attendance_records = (
        Attendance.objects
        .filter(date=today)
        .select_related('teacher', 'marked_by')
        .order_by('teacher__full_name', 'teacher__username')
    )
    all_records = (
        Attendance.objects
        .select_related('teacher')
        .order_by('-date', 'teacher__username')[:50]
    )
    context = {
        'form': form,
        'attendance_records': attendance_records,
        'all_records': all_records,
        'today': today,
    }
    return render(request, 'core/admin_attendance.html', context)




@login_required
@user_passes_test(is_admin)
def admin_messages(request):
    """Admin views all teacher messages."""
    all_messages = TeacherMessage.objects.select_related('teacher').all()
    return render(request, 'core/admin_messages.html', {'all_messages': all_messages})


@login_required
@user_passes_test(is_admin)
def admin_reply_message(request, msg_id):
    """Admin replies to a teacher message."""
    msg = get_object_or_404(TeacherMessage, id=msg_id)
    if request.method == 'POST':
        form = AdminReplyForm(request.POST)
        if form.is_valid():
            msg.admin_reply = form.cleaned_data['admin_reply']
            msg.status = 'replied'
            msg.replied_at = timezone.now()
            msg.save()
            
            Notification.objects.create(
                teacher=msg.teacher,
                message=f"Admin replied to your message '{msg.subject}': {msg.admin_reply}"
            )
            messages.success(request, 'Reply sent and teacher notified.')
            return redirect('admin_messages')
    else:
        msg.status = 'read'
        msg.save()
        form = AdminReplyForm()
    return render(request, 'core/admin_reply_message.html', {'msg': msg, 'form': form})




@login_required
@user_passes_test(is_teacher)
def teacher_dashboard(request):
    if not hasattr(request.user, 'teacher_profile'):
        return redirect('teacher_profile_setup')

    profile = request.user.teacher_profile
    schedules = ClassSchedule.objects.filter(
        teacher=request.user, date__gte=timezone.now().date()
    ).order_by('date', 'time')
    notifications = Notification.objects.filter(teacher=request.user).order_by('-created_at')
    my_attendance = Attendance.objects.filter(teacher=request.user).order_by('-date')[:10]
    my_messages = TeacherMessage.objects.filter(teacher=request.user).order_by('-created_at')[:5]

    context = {
        'profile': profile,
        'schedules': schedules,
        'notifications': notifications,
        'my_attendance': my_attendance,
        'my_messages': my_messages,
    }
    return render(request, 'core/teacher_dashboard.html', context)


@login_required
@user_passes_test(is_teacher)
def teacher_profile_setup(request):
    if hasattr(request.user, 'teacher_profile'):
        return redirect('teacher_dashboard')
    if request.method == 'POST':
        form = TeacherProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            selected_subjects = form.cleaned_data['subjects']
            if selected_subjects.exists():
                profile.department = selected_subjects.first().department
            profile.save()
            form.save_m2m()
            messages.success(request, 'Profile created successfully!')
            return redirect('teacher_dashboard')
    else:
        form = TeacherProfileForm()
    return render(request, 'core/profile_setup.html', {'form': form})


@login_required
@user_passes_test(is_teacher)
def teacher_send_message(request):
    """Teacher sends a message/notice to the admin."""
    if request.method == 'POST':
        form = TeacherMessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.teacher = request.user
            msg.save()
            messages.success(request, 'Your message has been sent to the admin.')
            return redirect('teacher_dashboard')
    else:
        form = TeacherMessageForm()
    return render(request, 'core/teacher_send_message.html', {'form': form})


@login_required
@user_passes_test(is_teacher)
def teacher_my_messages(request):
    """Teacher views their own sent messages and admin replies."""
    my_messages = TeacherMessage.objects.filter(teacher=request.user).order_by('-created_at')
    return render(request, 'core/teacher_my_messages.html', {'my_messages': my_messages})


@login_required
@user_passes_test(is_teacher)
def mark_notification_read(request, notif_id):
    notif = get_object_or_404(Notification, id=notif_id, teacher=request.user)
    notif.is_read = True
    notif.save()
    return redirect('teacher_dashboard')
