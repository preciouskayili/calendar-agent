from agents import Agent, Runner, function_tool
from prompts import calendar_agent_system_prompt, main_agent_system_prompt
from calendar_tools import (
    list_calendar_list,
    list_calendar_events,
    insert_calendar_event,
    create_calendar_list,
    add_calendar_account,
    list_calendar_accounts,
)

MODEL = "gpt-4o-mini"


@function_tool
def transfer_to_main_agent():
    return main_agent


@function_tool
def transfer_to_calendar_agent():
    return calendar_agent


calendar_agent = Agent(
    name="calendar_agent",
    instructions=calendar_agent_system_prompt,
)

main_agent = Agent(
    name="main_agent",
    instructions=main_agent_system_prompt,
    model=MODEL,
    tools=[
        calendar_agent.as_tool(
            tool_name="transfer_to_calendar_agent",
            tool_description="Handle the user's calendar requests",
        )
    ],
)


calendar_agent.tools.extend(
    [
        add_calendar_account,
        list_calendar_accounts,
        list_calendar_events,
        list_calendar_list,
        insert_calendar_event,
        create_calendar_list,
    ]
)
