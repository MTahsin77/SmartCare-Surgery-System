import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from django.conf import settings
from django.urls import reverse

def get_calendar_service(request):
    credentials = get_credentials(request)
    return build('calendar', 'v3', credentials=credentials)

def get_credentials(request):
    if 'credentials' not in request.session:
        return None

    return Credentials(
        **request.session['credentials'],
        scopes=settings.GOOGLE_OAUTH2_SCOPES
    )

def create_flow(request):
    flow = Flow.from_client_secrets_file(
        settings.GOOGLE_OAUTH2_CLIENT_SECRETS_JSON,
        scopes=settings.GOOGLE_OAUTH2_SCOPES,
        redirect_uri=request.build_absolute_uri(reverse('oauth2callback'))
    )
    return flow

def create_calendar_event(service, summary, description, start_time, end_time):
    event = {
        'summary': summary,
        'description': description,
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': 'Europe/London',
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': 'Europe/London',
        },
    }
    return service.events().insert(calendarId='primary', body=event).execute()

def update_calendar_event(service, event_id, summary, description, start_time, end_time):
    event = service.events().get(calendarId='primary', eventId=event_id).execute()
    event.update({
        'summary': summary,
        'description': description,
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': 'Europe/London',
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': 'Europe/London',
        },
    })
    return service.events().update(calendarId='primary', eventId=event_id, body=event).execute()

def delete_calendar_event(service, event_id):
    service.events().delete(calendarId='primary', eventId=event_id).execute()