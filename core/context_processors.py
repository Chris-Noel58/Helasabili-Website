from core.models import ContactInfo, AboutPage
from .models import SiteSettings, TeamMember


def site_context(request):
    """
    Global context processor to make site-wide data available to all templates
    """
    try:
        contact_info = ContactInfo.objects.first()
    except:
        contact_info = None
    
    try:
        about_page = AboutPage.objects.first()
    except:
        about_page = None
    
    try:
        site_settings = SiteSettings.objects.first()
    except Exception:
        site_settings = None

    # Add active team members to all templates
    try:
        team_members = TeamMember.objects.filter(is_active=True).order_by('order')
    except Exception:
        team_members = []

    return {
        'contact_info': contact_info,
        'about_page': about_page,
        'site_name': 'Nakuru College of Health Sciences and Management',
        'site_tagline': 'Kikuyu Campus',
        'site_settings': site_settings,
        'team_members': team_members,
    }
