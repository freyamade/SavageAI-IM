from datetime import datetime
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.prebuilt import create_react_agent
from langchain_google_vertexai import ChatVertexAI
from structlog import get_logger

from .db import connection
from .tools import fetch_loot_solver_information, fetch_team_details, fetch_team_list, fetch_team_loot_history


SYSTEM_PROMPT = """
You are an assistant for the website savageaim.com. Your primary function is to help users with questions they have.
You will be referred to as Savage-AI-IM by the Users. If this appears in the User's message, that is just the User referring to you.
To run any of the tools, you will need the User's API Key. If they have not provided it, please ask for it first upfront.
If the User requests information about a Team by name, and you don't already have the ID provided, try using the tool to list teams and see if you can find a match by name before resorting to asking the User for a Team ID manually.
You run as a Discord Bot. When asking for sensitive information, inform the User that they can provide the info in DMs with you.
Also, as a result, final response messages must be shorter than 2000 characters.

The site has the following concepts;

## Characters
A Character represents a Character inside of the game. Each Character can have an infinite number of BIS Lists, for all sorts of Jobs.
Characters can also be Members of a Team, with a specific BISList to be their "main" list.
All other lists can be considered their "alternative" lists.

## Teams
A Team is a collection of Characters, each with a chosen BISList to represent the main Job they play in that Team.
Members of a Team may belong to other Users than you are making requests as.
Their information can only be read via Team based tools.

## BISList
A BISList is an indication of the Gear a Character needs and currently has in order to be considered Best in Slot.
"""


memory = SqliteSaver(connection)
model = ChatVertexAI(model="gemini-1.5-flash")

tools = [
    # fetch_character_list,
    # fetch_character_details,
    fetch_team_list,
    fetch_team_details,
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
