from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_teacher, name='register'),
    path('', views.landing_page, name='landing'),
    path('dashboard/', views.dashboard_redirect, name='dashboard'),

    # Admin Management
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/teachers/', views.admin_teacher_list, name='admin_teacher_list'),
    path('admin/teachers/register/', views.admin_register_teacher, name='admin_register_teacher'),
    path('admin/teachers/<int:teacher_id>/delete/', views.admin_delete_teacher, name='admin_delete_teacher'),
    path('admin/attendance/', views.admin_attendance, name='admin_attendance'),
    path('admin/messages/', views.admin_messages, name='admin_messages'),
    path('admin/messages/<int:msg_id>/reply/', views.admin_reply_message, name='admin_reply_message'),

    # Teacher
    path('teacher-dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teacher-profile-setup/', views.teacher_profile_setup, name='teacher_profile_setup'),
    path('teacher/send-message/', views.teacher_send_message, name='teacher_send_message'),
    path('teacher/my-messages/', views.teacher_my_messages, name='teacher_my_messages'),
    path('notification/read/<int:notif_id>/', views.mark_notification_read, name='mark_notification_read'),
]
