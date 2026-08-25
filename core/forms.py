from django import forms
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Row, Column, Submit, HTML
from core.models import (
    Course, BlogPost, Testimonial, GalleryImage, 
    Application, AboutPage, ContactInfo, AdminProfile
)


class ApplicationForm(forms.ModelForm):
    """Application form for students"""
    class Meta:
        model = Application
        fields = ['full_name', 'email', 'phone', 'course', 'message']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full Name',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email Address',
                'required': True
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number',
                'required': True
            }),
            'course': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Tell us why you want to join this course (optional)',
                'rows': 4
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['course'].queryset = Course.objects.filter(is_active=True)
        self.fields['message'].required = False


class NewsletterForm(forms.Form):
    """Newsletter subscription form"""
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address',
            'required': True
        })
    )


class CourseForm(forms.ModelForm):
    """Course management form for admin"""
    class Meta:
        model = Course
        fields = ['title', 'description', 'duration', 'intake_period', 'fees', 'featured_image', 'is_active', 'order']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Course Title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Course Description'
            }),
            'duration': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 2 Years'
            }),
            'intake_period': forms.Select(attrs={
                'class': 'form-control'
            }),
            'fees': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Fees (optional)'
            }),
            'featured_image': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control'
            }),
        }


class BlogPostForm(forms.ModelForm):
    """Blog post management form for admin"""
    class Meta:
        model = BlogPost
        fields = ['title', 'featured_image', 'content', 'excerpt', 'author', 'status', 'is_featured']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Post Title'
            }),
            'featured_image': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'Post Content'
            }),
            'excerpt': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Brief summary of the post'
            }),
            'author': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Author Name'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class TestimonialForm(forms.ModelForm):
    """Testimonial management form for admin"""
    class Meta:
        model = Testimonial
        fields = ['name', 'course', 'message', 'photo', 'rating', 'is_active', 'order']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Student Name'
            }),
            'course': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Course Name'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Testimonial Message'
            }),
            'photo': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'rating': forms.Select(attrs={
                'class': 'form-control'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control'
            }),
        }


class GalleryImageForm(forms.ModelForm):
    """Gallery image management form for admin"""
    class Meta:
        model = GalleryImage
        fields = ['title', 'image', 'category', 'description', 'is_active', 'order']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Image Title'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Image Description'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control'
            }),
        }


class AboutPageForm(forms.ModelForm):
    """About page management form for admin"""
    class Meta:
        model = AboutPage
        fields = ['title', 'history', 'mission', 'vision', 'values', 'principal_message', 
                  'principal_name', 'principal_image', 'campus_description', 'location', 'established_year']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'history': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'College History'
            }),
            'mission': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Mission Statement'
            }),
            'vision': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Vision Statement'
            }),
            'values': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'College Values'
            }),
            'principal_message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Principal\'s Message'
            }),
            'principal_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Principal Name'
            }),
            'principal_image': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'campus_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Kikuyu Campus Description'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Campus Location'
            }),
            'established_year': forms.NumberInput(attrs={
                'class': 'form-control'
            }),
        }


class ContactInfoForm(forms.ModelForm):
    """Contact information management form for admin"""
    class Meta:
        model = ContactInfo
        fields = [
            'phone_primary', 'phone_secondary', 'email', 'email_alternative',
            'address', 'postal_code', 'city', 'country',
            'facebook', 'twitter', 'linkedin', 'instagram', 'youtube',
            'latitude', 'longitude', 'opening_hours'
        ]
        widgets = {
            'phone_primary': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Primary Phone Number'
            }),
            'phone_secondary': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Secondary Phone Number'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Primary Email'
            }),
            'email_alternative': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Alternative Email'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Street Address'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Postal Code'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Country'
            }),
            'facebook': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Facebook URL'
            }),
            'twitter': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Twitter URL'
            }),
            'linkedin': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'LinkedIn URL'
            }),
            'instagram': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Instagram URL'
            }),
            'youtube': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'YouTube URL'
            }),
            'latitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Latitude',
                'step': 'any'
            }),
            'longitude': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Longitude',
                'step': 'any'
            }),
            'opening_hours': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Monday - Friday: 8:00 AM - 5:00 PM'
            }),
        }


class AdminLoginForm(forms.Form):
    """Admin login form"""
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )


class ContactForm(forms.Form):
    """Simple contact form used on the public site"""
    name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    subject = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}))

    def clean_email(self):
        email = self.cleaned_data.get('email')
        return email
