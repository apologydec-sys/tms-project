from django import forms
from django.contrib.auth.forms import UserCreationForm, UsernameField
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import TeacherProfile, Subject, ClassSchedule, Attendance, TeacherMessage

User = get_user_model()



class AdminRegisterTeacherForm(forms.ModelForm):
    """Full registration form used by the admin to create teacher accounts with profile details."""
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter password'}),
        min_length=8,
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm password'}),
    )
    
    
    department = forms.ModelChoiceField(
        queryset=None, 
        required=False,
        label="Department"
    )
    skills = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'e.g. Java, Python, Project Management'}),
        help_text="Comma-separated skills."
    )
    profession_details = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Professional background...'}),
        help_text="Professional profile details."
    )

    class Meta:
        model = User
        fields = ['username', 'full_name', 'email', 'phone', 'date_joined_school']
        widgets = {
            'username':          forms.TextInput(attrs={'placeholder': 'e.g. john_doe'}),
            'full_name':         forms.TextInput(attrs={'placeholder': 'Full legal name'}),
            'email':             forms.EmailInput(attrs={'placeholder': 'teacher@school.com'}),
            'phone':             forms.TextInput(attrs={'placeholder': '+1 234 567 8900'}),
            'date_joined_school': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import Department
        self.fields['department'].queryset = Department.objects.all()

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError('A user with this email already exists.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('Passwords do not match.')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.is_teacher = True
        if commit:
            user.save()
            

            TeacherProfile.objects.create(
                user=user,
                department=self.cleaned_data.get('department'),
                skills=self.cleaned_data.get('skills', ''),
                profession_details=self.cleaned_data.get('profession_details', '')
            )
        return user



class CustomUserCreationForm(UserCreationForm):
    full_name = forms.CharField(max_length=150, required=True, label="Full Legal Name")
    email = forms.EmailField(required=True, label="Email Address")
    registration_code = forms.CharField(
        max_length=50, 
        required=True, 
        label="School Serial Number",
        help_text="Enter the unique code provided by the school administration."
    )

    class Meta:
        model = User
        fields = ('username', 'full_name', 'email', 'registration_code')
        field_classes = {'username': UsernameField}

    def clean_registration_code(self):
        code_str = self.cleaned_data.get('registration_code')
        from .models import SchoolRegistrationCode
        try:
            code_obj = SchoolRegistrationCode.objects.get(code=code_str)
            if code_obj.is_used:
                raise forms.ValidationError("This registration code has already been used.")
            return code_str
        except SchoolRegistrationCode.DoesNotExist:
            raise forms.ValidationError("Invalid registration code. Please contact school administration.")

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.full_name = self.cleaned_data['full_name']
        user.email = self.cleaned_data['email']
        user.registration_code = self.cleaned_data['registration_code']
        user.is_teacher = True  
        
        if commit:
            user.save()
            

            from .models import SchoolRegistrationCode
            code_obj = SchoolRegistrationCode.objects.get(code=user.registration_code)
            code_obj.is_used = True
            code_obj.used_by = user
            code_obj.save()
            
        return user



class TeacherProfileForm(forms.ModelForm):
    subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        help_text="Select up to two subjects.",
        required=True,
    )

    class Meta:
        model = TeacherProfile
        fields = ['profession_details', 'skills', 'profile_picture', 'subjects']

    def clean_subjects(self):
        subjects = self.cleaned_data.get('subjects')
        if subjects and subjects.count() > 2:
            raise forms.ValidationError('You can select a maximum of two subjects.')
        return subjects



class ClassScheduleForm(forms.ModelForm):
    class Meta:
        model = ClassSchedule
        fields = ['teacher', 'subject', 'date', 'time', 'room']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }



class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['teacher', 'date', 'status', 'notes']
        widgets = {
            'date':   forms.DateInput(attrs={'type': 'date'}),
            'notes':  forms.Textarea(attrs={'rows': 2, 'placeholder': 'Optional notes…'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['teacher'].queryset = User.objects.filter(is_teacher=True)



class TeacherMessageForm(forms.ModelForm):
    class Meta:
        model = TeacherMessage
        fields = ['subject', 'body']
        widgets = {
            'subject': forms.TextInput(attrs={'placeholder': 'e.g. Unable to attend tomorrow'}),
            'body':    forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe your situation…'}),
        }



class AdminReplyForm(forms.Form):
    admin_reply = forms.CharField(
        label='Reply',
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Type your reply…'}),
    )
