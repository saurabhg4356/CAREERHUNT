"""
Authentication and profile forms for CareerHunt candidates.
"""
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import UserProfile, UserEducation, UserSkill
from apps.jobs.models import Skill


class CandidateRegistrationForm(forms.ModelForm):
    """
    Candidate registration form with validation and password confirmation.
    """
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Create a strong password (min 8 characters)"}),
        label="Password",
        min_length=8,
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Confirm your password"}),
        label="Confirm Password",
    )
    first_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "First Name"}),
        required=True,
    )
    last_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Last Name"}),
        required=True,
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "name@example.com"}),
        required=True,
    )

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password")
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control", "placeholder": "Choose a unique username"}),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email address already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            self.add_error("confirm_password", "Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class CandidateLoginForm(AuthenticationForm):
    """
    Standard authentication form with styled form controls.
    """
    username = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Username or Email"}),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Your Password"}),
    )


class UserProfileUpdateForm(forms.ModelForm):
    """
    Form allowing candidates to update headline, location, bio, and preferences.
    """
    first_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
    last_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={"class": "form-control", "readonly": "readonly"}))

    preferred_job_types_raw = forms.MultipleChoiceField(
        choices=[
            ("internship", "Internship"),
            ("full-time", "Full-time"),
            ("part-time", "Part-time"),
            ("graduate-program", "Graduate Program"),
            ("trainee", "Trainee"),
            ("apprenticeship", "Apprenticeship"),
        ],
        widget=forms.CheckboxSelectMultiple(),
        required=False,
        label="Preferred Opportunity Types",
    )

    preferred_locations_str = forms.CharField(
        max_length=255,
        required=False,
        label="Preferred Locations (comma separated)",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Bangalore, Pune, Remote"}),
    )

    class Meta:
        model = UserProfile
        fields = (
            "headline", "phone", "location", "bio", "experience_level",
            "preferred_work_mode", "expected_salary_min", "resume"
        )
        widgets = {
            "headline": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Full Stack Developer | Final Year BCA"}),
            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "+91 9876543210"}),
            "location": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Bangalore, India"}),
            "bio": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Brief introduction about your technical interests..."}),
            "experience_level": forms.Select(attrs={"class": "form-control"}),
            "preferred_work_mode": forms.Select(attrs={"class": "form-control"}),
            "expected_salary_min": forms.NumberInput(attrs={"class": "form-control", "placeholder": "e.g. 500000"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields["first_name"].initial = self.instance.user.first_name
            self.fields["last_name"].initial = self.instance.user.last_name
            self.fields["email"].initial = self.instance.user.email
            self.fields["preferred_job_types_raw"].initial = self.instance.preferred_job_types
            self.fields["preferred_locations_str"].initial = ", ".join(self.instance.preferred_locations or [])

    def save(self, commit=True):
        profile = super().save(commit=False)
        profile.preferred_job_types = self.cleaned_data.get("preferred_job_types_raw", [])
        
        loc_str = self.cleaned_data.get("preferred_locations_str", "")
        if loc_str:
            profile.preferred_locations = [loc.strip() for loc in loc_str.split(",") if loc.strip()]
        else:
            profile.preferred_locations = []

        if commit:
            profile.save()
            user = profile.user
            user.first_name = self.cleaned_data["first_name"]
            user.last_name = self.cleaned_data["last_name"]
            user.save()
        return profile


class UserEducationForm(forms.ModelForm):
    class Meta:
        model = UserEducation
        fields = ("degree", "institution", "start_year", "end_year", "grade_or_cgpa")
        widgets = {
            "degree": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. B.Tech Computer Science"}),
            "institution": forms.TextInput(attrs={"class": "form-control", "placeholder": "University or College"}),
            "start_year": forms.NumberInput(attrs={"class": "form-control", "placeholder": "2023"}),
            "end_year": forms.NumberInput(attrs={"class": "form-control", "placeholder": "2027"}),
            "grade_or_cgpa": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. 8.5 CGPA"}),
        }
