"""Server-confirmed analytics events.

A view calls track_event() after a lead is actually saved; the event is kept in
the session and sent to Google Analytics on the next rendered page (usually the
page the view redirects to). This counts real submissions, not button clicks.
"""
import json

from django.conf import settings
from django.utils.safestring import mark_safe

_SESSION_KEY = 'analytics_events'
_JSON_ESCAPES = {ord('>'): '\\u003E', ord('<'): '\\u003C', ord('&'): '\\u0026'}


def track_event(request, name, **params):
    if not settings.GA_MEASUREMENT_ID or not hasattr(request, 'session'):
        return
    events = request.session.get(_SESSION_KEY, [])[-9:]
    events.append([name, params])
    request.session[_SESSION_KEY] = events


def pop_events_js(request):
    """Queued events as a JS array literal (safe inside <script>), or ''."""
    if not settings.GA_MEASUREMENT_ID or not hasattr(request, 'session'):
        return ''
    events = request.session.pop(_SESSION_KEY, None)
    if not events:
        return ''
    return mark_safe(json.dumps(events).translate(_JSON_ESCAPES))
