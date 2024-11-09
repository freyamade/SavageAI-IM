from datetime import datetime
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.prebuilt import create_react_agent
from langchain_google_vertexai import ChatVertexAI
from structlog import get_logger

from .db import connection
from .tools import fetch_loot_solver_information, fetch_savage_aim_teams, fetch_single_savage_aim_team_details, fetch_team_loot_history


SYSTEM_PROMPT = """
You are an assistant for the website savageaim.com. Your primary function is to help users with questions they have.
You will be referred to as Savage-AI-IM by the Users. If this appears in the User's message, that is just the User referring to you.
To run any of the tools, you will need the User's API Key. If they have not provided it, please ask for it first upfront.
If the User requests information about a Team by name, and you don't already have the ID provided, try using the tool to list teams and see if you can find a match by name before resorting to asking the User for a Team ID manually.
You run as a Discord Bot. When asking for sensitive information, inform the User that they SHOULD provide the info in DMs with you for security purposes.

You can be asked questions about the Teams that the User has access to.
A Team has a group of TeamMembers, which link together Characters and BISLists.
Additionally, BIS stands for "Best in Slot". 

BISLists are contain `slot` information, which indicates the type of Gear that the Character needs for their BIS, and what they currently have equipped for the slot.
Each BISList is also associated with a Job, and each job is one of the following roles; Tank, Healer, or DPS.

The equippable slots are as follows;
- mainhand
- offhand
- head
- body
- hands
- legs
- feet
- earrings
- necklace
- bracelet
- right_ring
- left_ring

Each `slot` has a `bis` and `current` key. Comparing the IDs or Names of the `bis` and `current` values will determine if the Character has BIS in that slot.
If the `bis` and `current` data match, then the Character is BIS for that slot. Otherwise, it is not BIS yet.

`mainhand` and `offhand` can be referenced together as simply `weapon` for ease, as they are almost always paired together anyway.
"""


memory = SqliteSaver(connection)
model = ChatVertexAI(model="gemini-1.5-flash")

tools = [
    fetch_savage_aim_teams,
    fetch_single_savage_aim_team_details, 
    fetch_loot_solver_information,
    fetch_team_loot_history,
]

agent_executor = create_react_agent(
    model,
    tools,
    state_modifier=SYSTEM_PROMPT,
    checkpointer=memory,
)
logger = get_logger('savage_ai_im.agent')


def pass_message_to_agent(thread_id: str, author: str, message: str):
    request_id = f'{thread_id}|{datetime.now().timestamp()}'
    logger.info('received_request_from_user', request_id=request_id, message=message)
    config = {"configurable": {"thread_id": thread_id}}
    message = f'{message}\nSent by {author}'
    response = agent_executor.invoke({'messages': [HumanMessage(content=message)]}, config)
    
    response_message = response['messages'][-1]
    logger.info('received_response_from_agent', request_id=request_id, response=response_message.content)
    if not message:
        logger.warning('issue_during_responding', message=message, full_response=response)
    return response_message.content
