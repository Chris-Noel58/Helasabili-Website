from django import forms
from django.contrib.auth.models import User
from django.forms import inlineformset_factory
from django.utils import timezone
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Row, Column, Submit, HTML
from core.rich_text import sanitize_rich_text
from core.models import (
    Course, CourseImage, BlogPost, Testimonial, CustomerReview, GalleryImage,
    Application, SiteVisitBooking, AboutPage, ContactInfo, AdminProfile, TeamMember
)
from core.models import Video


class CustomerReviewForm(forms.ModelForm):
    publication_consent = forms.BooleanField(
        required=True,
        label='I agree that my name and review may be published if approved.',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )

    class Meta:
        model = CustomerReview
        fields = ['name', 'email', 'rating', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'autocomplete': 'email'}),
            'rating': forms.Select(attrs={'class': 'form-select'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'maxlength': 2000}),
        }


class VideoForm(forms.ModelForm):
    """Form for creating/editing YouTube video links"""
    class Meta:
        model = Video
        fields = ['title', 'youtube_url', 'description', 'thumbnail', 'is_active', 'order']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Video title'}),
            'youtube_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Full YouTube URL'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Optional description'}),
            'thumbnail': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Optional thumbnail URL'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class ApplicationForm(forms.ModelForm):
    """Customer inquiry form for property listings."""
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
                'placeholder': 'Optional: include preferred visit dates, budget, or questions about the listing',
                'rows': 4
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['course'].queryset = Course.objects.filter(is_active=True)
        self.fields['course'].label = 'Listing'
        self.fields['course'].widget.attrs.update({'placeholder': 'Select a listing'})
        self.fields['message'].required = False


class SiteVisitBookingForm(forms.ModelForm):
    property_project = forms.ModelChoiceField(
        queryset=Course.objects.none(),
        empty_label='Select a property project',
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Property project',
    )

    class Meta:
        model = SiteVisitBooking
        fields = ['customer_name', 'email', 'phone', 'property_project', 'preferred_date', 'message']
        widgets = {
            'customer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'autocomplete': 'name',
                'placeholder': 'Your name',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'autocomplete': 'email',
                'placeholder': 'you@example.com',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'autocomplete': 'tel',
                'placeholder': 'Your phone number',
            }),
            'preferred_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'maxlength': 1000,
                'placeholder': 'Optional details',
            }),
        }
        labels = {
            'customer_name': 'Your name',
            'preferred_date': 'Preferred visit date',
            'message': 'Message (optional)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['property_project'].queryset = Course.objects.filter(
            is_active=True,
        ).order_by('-created_at', '-pk')

    def clean_preferred_date(self):
        preferred_date = self.cleaned_data['preferred_date']
        if preferred_date < timezone.localdate():
            raise forms.ValidationError('Choose today or a future date.')
        return preferred_date


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
    """Property project management form for admin."""
    class Meta:
        model = Course
        fields = ['title', 'description', 'location', 'plot_size', 'fees', 'featured_image', 'extra_details', 'is_active', 'order']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Project Title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Listing Description'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Location or nearest town'
            }),
            'plot_size': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Plot size (e.g., 50 x 100)'
            }),
            'fees': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Price (optional)'
            }),
            'featured_image': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'extra_details': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional listing details (optional)'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control'
            }),
        }


class CourseImageForm(forms.ModelForm):
    class Meta:
        model = CourseImage
        fields = ['image', 'caption', 'order', 'is_active']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'caption': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Picture description'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


CourseImageFormSet = inlineformset_factory(
    Course,
    CourseImage,
    form=CourseImageForm,
    fields=['image', 'caption', 'order', 'is_active'],
    extra=3,
    can_delete=True,
)


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
    """Customer review management form for admin"""
    class Meta:
        model = Testimonial
        fields = ['name', 'course', 'message', 'photo', 'rating', 'is_active', 'order']
        labels = {
            'name': 'Customer Name',
            'course': 'Property / Service',
            'message': 'Review',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Customer Name'
            }),
            'course': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Property or Service'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Customer Review'
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
        fields = [
            'title', 'image', 'category', 'description', 'is_active',
            'show_in_gallery', 'order',
        ]
        help_texts = {
            'image': (
                'For homepage hero use, upload a landscape image around 1600 × 1200 px '
                '(minimum 1200 × 900 px). The hero crops and zooms images to fit, so '
                'keep the main subject near the center.'
            ),
            'show_in_gallery': (
                'Display this image on the public Gallery page and in the homepage Property Gallery.'
            ),
        }
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
            'show_in_gallery': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control'
            }),
        }


class TeamMemberForm(forms.ModelForm):
    """Team member management form for the dashboard."""
    class Meta:
        model = TeamMember
        fields = ['name', 'title', 'bio', 'photo', 'order', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Team member name',
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Role or title',
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Optional short biography',
            }),
            'photo': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }
        help_texts = {
            'photo': 'Use a high-resolution portrait or team photo for the clearest display.',
            'order': 'Lower numbers appear first on the website.',
        }


class AboutPageForm(forms.ModelForm):
    """About page management form for admin"""
    rich_text_fields = (
        'history',
        'mission',
        'vision',
        'values',
        'principal_message',
        'campus_description',
    )

    class Meta:
        model = AboutPage
        fields = ['title', 'history', 'history_image', 'mission', 'vision', 'values', 'principal_message',
                  'principal_name', 'principal_image', 'campus_description', 'campus_image',
                  'location', 'established_year']
        labels = {
            'history': 'Company history',
            'history_image': 'Company history picture',
            'values': 'Company values',
            'principal_message': 'Managing Director message',
            'principal_name': 'Managing Director name',
            'principal_image': 'Managing Director photo',
            'campus_description': 'Company Description',
            'campus_image': 'Company or property image',
            'location': 'Primary service area',
            'established_year': 'Year established',
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'history': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Company history'
            }),
            'history_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
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
                'placeholder': 'Company values'
            }),
            'principal_message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Director\'s Message'
            }),
            'principal_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Director Name'
            }),
            'principal_image': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'campus_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Company Description'
            }),
            'campus_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Primary service area (e.g., Nakuru and Nanyuki)'
            }),
            'established_year': forms.NumberInput(attrs={
                'class': 'form-control'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        for field_name in self.rich_text_fields:
            if field_name in cleaned_data:
                cleaned_data[field_name] = sanitize_rich_text(cleaned_data[field_name])
        return cleaned_data


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
