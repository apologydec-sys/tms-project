from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    is_teacher = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    full_name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    date_joined_school = models.DateField(null=True, blank=True)
    registration_code = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.full_name if self.full_name else self.username


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Subject(models.Model):
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='subjects')

    def __str__(self):
        return f"{self.name} ({self.department.name})"


class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    profession_details = models.TextField(
        help_text="Describe the teacher's professional background and qualifications.",
        blank=True
    )
    skills = models.TextField(
        blank=True,
        help_text="List the teacher's skills and acquired competencies (comma-separated)."
    )
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    subjects = models.ManyToManyField(Subject, blank=True, help_text="Select subjects taught.")

    def __str__(self):
        return f"Profile of {self.user.username}"

    def skills_list(self):
        """Return skills as a list."""
        if self.skills:
            return [s.strip() for s in self.skills.split(',') if s.strip()]
        return []


class ClassSchedule(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='schedules')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    room = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.subject.name} by {self.teacher.username} on {self.date} at {self.time}"


class Notification(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.teacher.username} - {self.created_at}"


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('on_leave', 'On Leave'),
    ]
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='present')
    notes = models.TextField(blank=True, null=True)
    marked_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='marked_attendances'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('teacher', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.teacher.username} - {self.date} - {self.status}"


class TeacherMessage(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('read', 'Read'),
        ('replied', 'Replied'),
    ]
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    subject = models.CharField(max_length=200)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_reply = models.TextField(blank=True, null=True)
    replied_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"From {self.teacher.username}: {self.subject}"


class SchoolRegistrationCode(models.Model):
    code = models.CharField(max_length=50, unique=True)
    is_used = models.BooleanField(default=False)
    used_by = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='used_school_code')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        status = "Used" if self.is_used else "Available"
        return f"{self.code} ({status})"
