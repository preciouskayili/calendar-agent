# AI Calendar Agent

An AI-powered calendar assistant that connects to your email accounts and calendars. It uses natural language processing to schedule meetings, find available times, and manage your calendar efficiently.

## Features

- Natural language processing for meeting scheduling
- Automatic availability checking
- Google Calendar integration
- Google Meet integration
- Multi-attendee scheduling
- Smart time slot suggestions

## Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Google Calendar API credentials

## Setup

1. Clone the repository:

```bash
git clone <repository-url>
cd calendar-agent
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up Google Calendar API:

   - Go to the [Google Cloud Console](https://console.cloud.google.com)
   - Create a new project
   - Enable the Google Calendar API
   - Create OAuth 2.0 credentials
   - Download the credentials and save as `credentials.json` in the project root

4. Set up your OpenAI API key:

```bash
# On Windows
set OPENAI_API_KEY=your-api-key-here

# On Linux/Mac
export OPENAI_API_KEY=your-api-key-here
```

## Usage

### Basic Example

```python
from agents import CalendarAgent

# Initialize the agent
agent = CalendarAgent(openai_api_key="your-api-key")

# Schedule a meeting using natural language
result = agent.schedule_meeting(
    "Schedule a meeting with ted@gmail.com for next Wednesday on Google Meet"
)
```

### Running the Example Script

```bash
python example.py
```

## Features in Detail

### Natural Language Processing

The agent understands various natural language formats for scheduling:

- "Schedule a meeting with [email] for [time] on [platform]"
- "Find a time to meet with [email] next week"
- "Set up a 30-minute call with [email] tomorrow afternoon"

### Availability Checking

The agent automatically:

- Checks calendar availability for all attendees
- Suggests alternative times if the requested slot is unavailable
- Considers time zones and working hours

### Google Meet Integration

- Automatically creates Google Meet links for virtual meetings
- Includes meeting links in calendar invites

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
