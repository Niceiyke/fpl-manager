import requests
from backend.services import Parse_player_data,map_selected_picks
URL ="https://fantasy.premierleague.com/api"
headers={"User-Agent": "Dalvik/2.1.0 (Linux; U; Android 5.1; PRO 5 Build/LMY47D)", 'accept-language': 'en'}
async def get_manager_team(manager_id):
    team =await requests.get(f"{URL}/my-team/{manager_id}/", headers=headers)
    team=team.json()
    selected_players=await Parse_player_data(team)
    selected_players =await map_selected_picks(selected_players)
    print("selected players",selected_players)
    return selected_players

