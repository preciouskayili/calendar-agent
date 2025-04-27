import json
from agents import function_tool
from googleapis import create_service
from typing import List, Optional, Dict, Any
from account_manager import account_manager


def construct_google_calendar_client(account_id: str):
    """
    Constructs a Google Calendar API client for a specific account.

    Parameters:
    - account_id (str): The ID of the account to use.

    Returns:
    - service: The Google Calendar API service instance.
    """
    API_NAME = "calendar"
    API_VERSION = "v3"
    SCOPES = [
        "https://www.googleapis.com/auth/calendar",
        "https://www.googleapis.com/auth/calendar.events",
    ]

    # Get credentials for the account
    creds = account_manager.get_account(account_id)
    if not creds:
        raise ValueError(f"No credentials found for account {account_id}")

    service = create_service(
        "credentials.json",  # This is just a placeholder, actual credentials are passed
        API_NAME,
        API_VERSION,
        SCOPES,
        prefix=f"_{account_id}",  # Use account-specific token file
    )
    return service


@function_tool
def add_calendar_account(account_id: str) -> Dict[str, Any]:
    """
    Adds a new Google Calendar account.

    Parameters:
    - account_id (str): A unique identifier for the new account.

    Returns:
    - dict: Information about the added account.
    """
    success = account_manager.add_account(account_id)
    if success:
        return {"status": "success", "account_id": account_id}
    else:
        return {"status": "error", "message": "Failed to add account"}


@function_tool
def list_calendar_accounts() -> List[str]:
    """
    Lists all available calendar accounts.

    Returns:
    - list: A list of account IDs.
    """
    return account_manager.list_accounts()


@function_tool
def create_calendar_list(account_id: str, calendar_name: str) -> Dict[str, Any]:
    """
    Creates a new calendar list for a specific account.

    Parameters:
    - account_id (str): The ID of the account to use.
    - calendar_name (str): The name of the new calendar list.

    Returns:
    - dict: A dictionary containing the ID of the new calendar list.
    """
    calendar_service = construct_google_calendar_client(account_id)
    calendar_list = {"summary": calendar_name}
    created_calendar_list = (
        calendar_service.calendars().insert(body=calendar_list).execute()
    )
    return created_calendar_list


@function_tool
def list_calendar_list(account_id: str, max_capacity: int) -> List[Dict[str, str]]:
    """
    Lists calendar lists for a specific account.

    Parameters:
    - account_id (str): The ID of the account to use.
    - max_capacity (int or str): The maximum number of calendar lists to retrieve.

    Returns:
    - list: A list of dictionaries containing calendar list information.
    """
    if isinstance(max_capacity, str):
        max_capacity = int(max_capacity)

    calendar_service = construct_google_calendar_client(account_id)
    all_calendars = []
    all_calendars_cleaned = []
    next_page_token = None
    capacity_tracker = 0

    while True:
        calendar_list = (
            calendar_service.calendarList()
            .list(
                maxResults=min(200, max_capacity - capacity_tracker),
                pageToken=next_page_token,
            )
            .execute()
        )

        calendars = calendar_list.get("items", [])
        all_calendars.extend(calendars)
        capacity_tracker += len(calendars)
        if capacity_tracker >= max_capacity:
            break

        next_page_token = calendar_list.get("nextPageToken")
        if not next_page_token:
            break

    for calendar in all_calendars:
        all_calendars_cleaned.append(
            {
                "id": calendar["id"],
                "name": calendar["summary"],
                "description": calendar.get("description", ""),
            }
        )
    return all_calendars_cleaned


@function_tool
def list_calendar_events(
    account_id: str, calendar_id: str, max_capacity: int
) -> List[Dict[str, Any]]:
    """
    Lists events from a specified calendar for a specific account.

    Parameters:
    - account_id (str): The ID of the account to use.
    - calendar_id (str): The ID of the calendar from which to list events.
    - max_capacity (int or str): The maximum number of events to retrieve.

    Returns:
    - list: A list of events from the specified calendar.
    """
    if isinstance(max_capacity, str):
        max_capacity = int(max_capacity)

    calendar_service = construct_google_calendar_client(account_id)
    all_events = []
    next_page_token = None
    capacity_tracker = 0
    while True:
        events_list = (
            calendar_service.events()
            .list(
                calendarId=calendar_id,
                maxResults=min(250, max_capacity - capacity_tracker),
                pageToken=next_page_token,
                orderBy="startTime",
                singleEvents=True,
            )
            .execute()
        )
        events = events_list.get("items", [])
        all_events.extend(events)
        capacity_tracker += len(events)
        if capacity_tracker >= max_capacity:
            break
        next_page_token = events_list.get("nextPageToken")
        if not next_page_token:
            break

    return all_events


@function_tool
def insert_calendar_event(
    account_id: str,
    calendar_id: str,
    summary: str,
    start_time: str,
    end_time: str,
    description: str,
    location: str,
    attendees: Optional[List[str]],
    timezone: str,
    create_google_meet: bool,
) -> Dict[str, Any]:
    """
    Inserts an event into the specified calendar for a specific account.

    Parameters:
    - account_id (str): The ID of the account to use.
    - calendar_id (str): The ID of the calendar where the event will be inserted.
    - summary (str): Title of the event.
    - start_time (str): Start time in ISO format.
    - end_time (str): End time in ISO format.
    - description (str): Optional description of the event.
    - location (str): Optional location of the event.
    - attendees (List[str]): Optional list of attendee email addresses.
    - timezone (str): Timezone for the event.
    - create_google_meet (bool): Whether to create a Google Meet link.

    Returns:
    - dict: The created event.
    """
    if attendees is None:
        attendees = []

    calendar_service = construct_google_calendar_client(account_id)
    request_body = {
        "summary": summary,
        "location": location,
        "description": description,
        "start": {
            "dateTime": start_time,
            "timeZone": timezone,
        },
        "end": {
            "dateTime": end_time,
            "timeZone": timezone,
        },
        "attendees": [{"email": email} for email in attendees],
    }

    if create_google_meet:
        request_body["conferenceData"] = {
            "createRequest": {
                "requestId": f"meet_{start_time.replace(':', '').replace('-', '')}",
                "conferenceSolutionKey": {"type": "hangoutsMeet"},
            }
        }

    event = (
        calendar_service.events()
        .insert(calendarId=calendar_id, body=request_body, conferenceDataVersion=1)
        .execute()
    )

    return event
