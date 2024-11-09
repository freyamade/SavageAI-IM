from uuid import UUID

import requests
from langchain_core.tools import tool
from .schema import LootHistoryDetails, Team, LootSolverResponse


@tool
def fetch_savage_aim_teams(api_key: str) -> list[Team]:
    """
    Fetch a list of all of the Team objects.
    When asked about Teams by name, try running this tool to get all of the User's Teams and from there you can determine IDs.
    """
    headers = {'Authorization': f'Token {api_key}'}
    response = requests.get('https://savageaim.com/backend/api/team/', headers=headers)
    if response.status_code != 200:
        raise Exception(f'An error occurred ({response.status_code}): {response.text}')
    return [Team(**t) for t in response.json()]


@tool
def fetch_single_savage_aim_team_details(api_key: str, team_id: UUID) -> Team:
    """
    Fetch the data of a single Team, referenced by its ID.
    """
    headers = {'Authorization': f'Token {api_key}'}
    response = requests.get(f'https://savageaim.com/backend/api/team/{team_id}/', headers=headers)
    if response.status_code != 200:
        raise Exception(f'An error occurred ({response.status_code}): {response.text}')
    return Team(**response.json())


@tool
def fetch_loot_solver_information(api_key: str, team_id: UUID) -> LootSolverResponse:
    """
    Retrieve all of the Loot Solver information for a given Team.
    The Loot Solver contains information on however many clears the Team still require before they are finished with each fight.
    For the `first_floor`, `second_floor`, and `third_floor` keys, the Loot Solver information will contain lists, with each item in the list giving the information for an individual clear.
    If there is a list with 3 items in it for a `floor` key, that means they need 3 more clears to get everything they need.
    For the `fourth_floor` key, the API just tracks the number of Weapons and Mounts required. As Mounts are one per week, assume the number of mounts is the same as the number of required weeks.
    The `token` flag is not a drop in and of itself, but if it is True then you can mention that the Team can make Token purchases after that week's clear is finished.
    """
    team = fetch_single_savage_aim_team_details.invoke({'team_id': team_id, 'api_key': api_key})
    headers = {'Authorization': f'Token {api_key}'}
    response = requests.get(f'https://savageaim.com/backend/api/team/{team_id}/loot/solver/', headers=headers)
    if response.status_code != 200:
        raise Exception(f'An error occurred ({response.status_code}): {response.text}')
    details = response.json()

    # Replace the loot solver ids with names
    name_map = {
        member.id: member.character.name
        for member in team.members
    }
    for key in ['first_floor', 'second_floor', 'third_floor']:
        for week_data in details[key]:
            for slot in week_data:
                if slot == 'token':
                    continue
                week_data[slot] = name_map.get(week_data[slot], None)
    return LootSolverResponse(**details)


@tool
def fetch_team_loot_history(api_key: str, team_id: UUID) -> LootHistoryDetails:
    """
    Retrieve a list of all of the Loot items retrieved over the course of the Tier a Team is currently progressing.
    If asked about Loot Drops, or what Team Member received an item, or how many items a Team Member has receieved, use this tool call.
    """
    headers = {'Authorization': f'Token {api_key}'}
    response = requests.get(f'https://savageaim.com/backend/api/team/{team_id}/loot/', headers=headers)
    if response.status_code != 200:
        raise Exception(f'An error occurred ({response.status_code}): {response.text}')

    return LootHistoryDetails(**response.json().get('loot', {}))

