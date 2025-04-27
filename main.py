import os
import click
from calendar_agents import main_agent
from agents import Runner, set_default_openai_key
from openai import OpenAI
from dotenv import load_dotenv
from calendar_tools import (
    list_calendar_list,
    insert_calendar_event,
    list_calendar_events,
    create_calendar_list,
)
from vectorstore import (
    create_store,
    upsert_message,
    fetch_session_messages,
    get_new_session_id,
)

load_dotenv()
set_default_openai_key(os.getenv("OPENAI_API_KEY"))

# Initialize Pinecone store
create_store()


def format_conversation_history(messages):
    """Format conversation history for the agent."""
    formatted_history = []
    for msg in messages:
        formatted_history.append(f"{msg['role']}: {msg['content']}")
    return "\n".join(formatted_history)


@click.group()
def cli():
    """🗓️ AI Calendar Assistant - Schedule meetings and manage your calendar with ease."""
    pass


@cli.command()
@click.option(
    "--interactive",
    "-i",
    is_flag=True,
    help="Start interactive mode for continuous scheduling",
)
@click.option(
    "--session-id",
    default=None,
    help="Continue an existing chat session",
)
@click.option(
    "--new-chat",
    is_flag=True,
    help="Start a new chat session",
)
def schedule(interactive, session_id, new_chat):
    """Start scheduling meetings and managing your calendar."""
    # Handle session management
    if new_chat or not session_id:
        session_id = get_new_session_id()
        click.secho(f"Starting new chat session: {session_id}", fg="yellow")
    else:
        click.secho(f"Continuing chat session: {session_id}", fg="yellow")

    # Load previous messages for context
    memory = fetch_session_messages(session_id)
    if memory:
        click.secho("\nPrevious conversation context loaded.", fg="green")

    if interactive:
        click.secho(
            "🤖 AI Calendar Assistant - Interactive Mode", fg="green", bold=True
        )
        click.secho("Type 'exit' or 'quit' to end the session\n", fg="yellow")

        while True:
            user_input = click.prompt(
                click.style("What would you like to do?", fg="bright_blue")
                + "\nExample: Schedule a meeting with ted@gmail.com for next Wednesday on Google Meet"
            )

            if user_input.lower() in ("exit", "quit", "quit()", "q"):
                click.secho("\nGoodbye! 👋", fg="green")
                break

            click.echo(f"\n🎯 Processing: {user_input}\n")

            # Store user message
            upsert_message(session_id, "user", user_input)

            # Format conversation history
            conversation_history = format_conversation_history(memory)

            # Run the agent with conversation history
            result = Runner.run_sync(
                main_agent,
                f"Previous conversation:\n{conversation_history}\n\nCurrent message: {user_input}",
                max_turns=50,
            )

            # Store assistant response
            upsert_message(session_id, "assistant", result.final_output)

            click.secho("✨ Result:", fg="green", bold=True)
            click.echo(result.final_output + "\n")

            # Update memory for next iteration
            memory = fetch_session_messages(session_id)
    else:
        # Single command mode
        user_input = click.prompt(
            click.style("What would you like to schedule?", fg="bright_blue")
            + "\nExample: Schedule a meeting with ted@gmail.com for next Wednesday on Google Meet"
        )
        click.echo(f"\n🎯 Processing: {user_input}\n")

        # Store user message
        upsert_message(session_id, "user", user_input)

        # Format conversation history
        conversation_history = format_conversation_history(memory)

        # Run the agent with conversation history
        result = Runner.run_sync(
            main_agent,
            f"Previous conversation:\n{conversation_history}\n\nCurrent message: {user_input}",
            max_turns=50,
        )

        # Store assistant response
        upsert_message(session_id, "assistant", result.final_output)

        click.secho("✨ Result:", fg="green", bold=True)
        click.echo(result.final_output)


if __name__ == "__main__":
    cli()
