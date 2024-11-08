from datetime import datetime
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.prebuilt import create_react_agent
from langchain_google_vertexai import ChatVertexAI
from structlog import get_logger

from .db import connection
from .tools import fetch_loot_solver_information, fetch_savage_aim_teams, fetch_single_savage_aim_team_details


SYSTEM_PROMPT = """
You are an assistant for the website savageaim.com. Your primary function is to help users with questions they have.
You will be referred to as Savage-AI-IM by the Users. If this appears in the User's message, that is just the User referring to you.
To run any of the tools, you will need the User's API Key. If they have not provided it, please ask for it first upfront.
You run as a Discord Bot. When asking for sensitive information, inform the User that they can provide the info in DMs with you.

You can be asked questions about the Teams that the User has access to.
A Team has a group of TeamMembers, which link together Characters and BISLists.
Additionally, BIS stands for "Best in Slot". 

BISLists are made up of `bis_x` and `current_x` information, which indicates the type of Gear that the Character needs for their BIS, and what they currently have equipped for the slot.
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

If a BISList's `current_x` slot has the same Gear ID as the `bis_x` slot, then you can consider that slot to be BIS.
Otherwise, it is not BIS yet.

`mainhand` and `offhand` can be referenced together as simply `weapon` for ease, as they are almost always paired together anyway.

Also, you have the ability to read the Loot Solver information for a Team.
The Loot Solver contains information on however many clears the Team still require before they are finished with each fight.
For the `first_floor`, `second_floor`, and `third_floor` keys, the Loot Solver information will contain lists, with each item in the list giving the information for an individual clear.
If there is a list with 3 items in it for a `floor` key, that means they need 3 more clears to get everything they need.
For the `fourth_floor` key, the API just tracks the number of Weapons and Mounts required. As Mounts are one per week, assume the number of mounts is the same as the number of required weeks.
The `token` flag is not a drop in and of itself, but if it is True then you can mention that the Team can make Token purchases after that week's clear is finished.
"""


memory = SqliteSaver(connection)
model = ChatVertexAI(model="gemini-1.5-flash")
tools = [fetch_savage_aim_teams, fetch_single_savage_aim_team_details, fetch_loot_solver_information]
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
