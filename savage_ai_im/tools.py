from uuid import UUID

import requests
from langchain_core.tools import tool
from .schema import LootHistoryDetails, Team, LootSolverResponse


@tool
def fetch_savage_aim_teams(api_key: str) -> list[Team]:
    """
    Fetch a list of all of the Team objects.
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
    Retrieve the full suite of Loot Solver information for a given Team.
    Help the AI by replacing the IDs with Character Names
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
    """
    headers = {'Authorization': f'Token {api_key}'}
    response = requests.get(f'https://savageaim.com/backend/api/team/{team_id}/loot/', headers=headers)
    if response.status_code != 200:
        raise Exception(f'An error occurred ({response.status_code}): {response.text}')

    return LootHistoryDetails(**response.json().get('loot', {}))

