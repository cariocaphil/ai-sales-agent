from dotenv import load_dotenv
from agents import Agent, Runner, trace, function_tool
from openai.types.responses import ResponseTextDeltaEvent
import sendgrid
import os
from sendgrid.helpers.mail import Mail, Email, To, Content
import asyncio

load_dotenv()


def send_test_email():
    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get("SENDGRID_API_KEY"))

    from_email = Email("cariocaphil@gmail.com")  # Change to your verified sender
    to_email = To("cariocaphil@gmail.com")

    content = Content("text/plain", "This is an important test email")
    mail = Mail(from_email, to_email, "Test email", content).get()

    response = sg.client.mail.send.post(request_body=mail)
    print(response.status_code)


send_test_email()


instructions1 = """
You are a professional sales agent working for SynthPilot,
a fictional AI product that helps software teams automatically analyze user feedback,
detect product pain points, and generate prioritized feature recommendations.

You write professional, serious cold emails.
"""

instructions2 = """
You are a humorous, engaging sales agent working for SynthPilot,
a fictional AI product that helps software teams automatically analyze user feedback,
detect product pain points, and generate prioritized feature recommendations.

You write witty, engaging cold emails that are likely to get a response.
"""

instructions3 = """
You are a busy sales agent working for SynthPilot,
a fictional AI product that helps software teams automatically analyze user feedback,
detect product pain points, and generate prioritized feature recommendations.

You write concise, to-the-point cold emails.
"""


sales_agent1 = Agent(
    name="Professional Sales Agent",
    instructions=instructions1,
    model="gpt-4o-mini",
)

sales_agent2 = Agent(
    name="Engaging Sales Agent",
    instructions=instructions2,
    model="gpt-4o-mini",
)

sales_agent3 = Agent(
    name="Busy Sales Agent",
    instructions=instructions3,
    model="gpt-4o-mini",
)


async def main():
    result = Runner.run_streamed(
        sales_agent1,
        input="Write a cold sales email",
    )

    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(
            event.data,
            ResponseTextDeltaEvent,
        ):
            print(event.data.delta, end="", flush=True)

    message = "Write a cold sales email"

    with trace("Parallel cold emails"):
        results = await asyncio.gather(
            Runner.run(sales_agent1, message),
            Runner.run(sales_agent2, message),
            Runner.run(sales_agent3, message),
        )

    outputs = [result.final_output for result in results]

    for output in outputs:
        print(output + "\n\n")

    sales_picker = Agent(
        name="sales_picker",
        instructions="""
        You pick the best cold sales email from the given options.
        Imagine you are a customer and pick the one you are most likely to respond to.
        Do not give an explanation; reply with the selected email only.
        """,
        model="gpt-4o-mini",
    )

    with trace("Selection from sales people"):
        results = await asyncio.gather(
            Runner.run(sales_agent1, message),
            Runner.run(sales_agent2, message),
            Runner.run(sales_agent3, message),
        )

        outputs = [result.final_output for result in results]

        emails = "Cold sales emails:\n\n" + "\n\nEmail:\n\n".join(outputs)

        best = await Runner.run(sales_picker, emails)

        print(f"Best sales email:\n{best.final_output}")


@function_tool
def send_email(body: str):
    """Send out an email with the given body to all sales prospects."""

    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get("SENDGRID_API_KEY"))

    from_email = Email("cariocaphil@gmail.com")
    to_email = To("cariocaphil@gmail.com")

    content = Content("text/plain", body)
    mail = Mail(from_email, to_email, "Sales email", content).get()

    sg.client.mail.send.post(request_body=mail)

    return {"status": "success"}


description = "Write a cold sales email"

tool1 = sales_agent1.as_tool(
    tool_name="sales_agent1",
    tool_description=description,
)

tool2 = sales_agent2.as_tool(
    tool_name="sales_agent2",
    tool_description=description,
)

tool3 = sales_agent3.as_tool(
    tool_name="sales_agent3",
    tool_description=description,
)

tools = [tool1, tool2, tool3, send_email]


manager_instructions = """
You are a Sales Manager at SynthPilot.

SynthPilot is a fictional AI product that helps software teams automatically analyze user feedback,
detect product pain points, and generate prioritized feature recommendations.

Your goal is to find the single best cold sales email using the sales_agent tools.

Follow these steps carefully:

1. Generate Drafts:
Use all three sales_agent tools to generate three different email drafts.
Do not proceed until all three drafts are ready.

2. Evaluate and Select:
Review the drafts and choose the single best email using your judgment of which one is most effective.

3. Send:
Use the send_email tool to send the best email, and only the best email, to the user.

Crucial Rules:
- You must use the sales agent tools to generate the drafts.
- Do not write the drafts yourself.
- You must send ONE email using the send_email tool.
- Never send more than one email.
"""


sales_manager = Agent(
    name="Sales Manager",
    instructions=manager_instructions,
    tools=tools,
    model="gpt-4o-mini",
)


async def run_sales_manager():
    message = "Send a cold sales email addressed to 'Dear Product Leader'"

    with trace("Sales manager"):
        result = await Runner.run(sales_manager, message)

    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
    asyncio.run(run_sales_manager())