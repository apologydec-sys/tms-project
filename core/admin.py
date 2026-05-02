from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, Department, Subject, TeacherProfile, ClassSchedule, 
    Notification, Attendance, TeacherMessage, SchoolRegistrationCode
)


class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Role Info', {'fields': ('is_teacher', 'is_admin', 'full_name', 'phone', 'date_joined_school', 'registration_code')}),
    )
    list_display = ('username', 'full_name', 'email', 'is_teacher', 'is_admin', 'is_staff')
    search_fields = ('username', 'full_name', 'email')


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'date', 'status', 'marked_by', 'created_at')
    list_filter = ('status', 'date')
    search_fields = ('teacher__username', 'teacher__full_name')
    date_hierarchy = 'date'


@admin.register(TeacherMessage)
class TeacherMessageAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'subject', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('teacher__username', 'subject')


admin.site.register(User, CustomUserAdmin)
admin.site.register(Department)
admin.site.register(Subject)
admin.site.register(TeacherProfile)
admin.site.register(ClassSchedule)
admin.site.register(Notification)


@admin.register(SchoolRegistrationCode)
class SchoolRegistrationCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'is_used', 'used_by', 'created_at')
    list_filter = ('is_used',)
    search_fields = ('code', 'used_by__username')
