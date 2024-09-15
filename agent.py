from uagents import Agent, Context, Model
import os
from dotenv import load_dotenv
load_dotenv()

class TestRequest(Model):
    message: str


class Response(Model):
    text: str


def sendEmergencyMsg(message: str):
    from twilio.rest import Client

    # Your Account SID and Auth Token from Twilio Console
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")

    # Initialize the client
    client = Client(account_sid, auth_token)

    # Send SMS
    message = client.messages.create(
        body=message,  # The content of the SMS
        from_='+18777161342',  # Your Twilio number
        to='+16462296260'  # The recipient's phone number
    )
    sms_sid = message.sid
    print(f"Message sent with SID: {sms_sid}")


agent = Agent(
    name="your_agent_name_here",
    seed="your_agent_seed_here",
    port=8001,
    endpoint="http://localhost:8001/submit",
)


@agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"Starting up {agent.name}")
    ctx.logger.info(f"With address: {agent.address}")
    ctx.logger.info(f"And wallet address: {agent.wallet.address()}")


@agent.on_query(model=TestRequest, replies={Response})
async def query_handler(ctx: Context, sender: str, query: TestRequest):
    #print the message
    ctx.logger.info(query.message)
    sendEmergencyMsg(query.message)
    await ctx.send(sender, Response(text="success"))


if __name__ == "__main__":
    agent.run()