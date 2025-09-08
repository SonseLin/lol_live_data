from pypresence import Presence
import time
import requests
import json
import os
from urllib3.exceptions import InsecureRequestWarning
# Suppress only the single warning from urllib3 needed
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
livegame_endpoint = "https://127.0.0.1:2999/liveclientdata/allgamedata"


def get_movespeed(data):
    return data.json()["activePlayer"]["championStats"]["moveSpeed"]

def get_active_player_nickname(data):
    return data.json()['activePlayer']['summonerName']

def get_KDA(data):
    data = data.json()
    active_player_nickname = data["activePlayer"]["summonerName"]
    for player in data["allPlayers"]:
        if player["riotId"] != active_player_nickname:
            continue
        scores = player["scores"]
        return f"K/D/A: {scores['kills']}/{scores['deaths']}/{scores['assists']}"

def get_creepScore(data, active_player):
    data = data.json()
    for player in data["allPlayers"]:
        if player["riotId"] != active_player:
            continue
        scores = player["scores"]
        print("got player iteration")
        return f"creeps: {scores['creepScore']}"
    
def get_hero_name(data, active_player):
    data = data.json()
    for player in data["allPlayers"]:
        if player["riotId"] != active_player:
            continue
        return player["championName"]
    
def get_icon_for_hero(hero):
     return hero.lower().replace(' ', '_').replace("'", "").replace("'", "")
    
def get_game_time(data):
    data = data.json()
    time = int(data['gameData']['gameTime'])
    return time

# Your Discord Application ID (create at https://discord.com/developers/applications)
client_id = os.environ.get("DISCORD_CLIENT_ID")

try:
    RPC = Presence(client_id)
    RPC.connect()
    print("✅ Connected to Discord RPC")
except Exception as e:
    print(f"❌ Failed to connect to Discord RPC: {e}")
    exit(1)

def update_RPC(game_time, hero_name, creeps, kda):
    buttons = [
                {
                    "label": "GitHub", 
                    "url": "https://github.com/sonselin"
                },
                {
                    "label": "Follow", 
                    "url": "https://github.com/sonselin?tab=followers"
                }
            ]
    RPC.update(
    state=kda,
    details=creeps,
    large_image=get_icon_for_hero(hero_name),  # Image key from Discord Developer Portal
    large_text=f"Playing as {hero_name}",
    small_image="zani",       # Another image key
    small_text="Developer Mode",
    start=game_time,
    buttons=buttons
    )


print("Rich Presence is now active!")

try:
    data = requests.get(livegame_endpoint, verify=False)
    active_player = get_active_player_nickname(data)
    time_start = time.time()
    while True:
        time.sleep(1)
        data = requests.get(livegame_endpoint, verify=False)
        kda = get_KDA(data)
        creeps = get_creepScore(data, active_player)
        game_time = time_start - get_game_time(data)
        nickname = get_active_player_nickname(data)
        hero_name = get_hero_name(data, active_player)
        update_RPC(hero_name=hero_name, game_time=game_time
                   ,creeps=creeps, kda=kda)
        print(f"Rich Presence is now updating on time!")
        print("KDA", kda)
        print("creeps", creeps)
        print("player", nickname, " as ", hero_name)
        with open("data_lol.json", "w") as file:
            file.write(json.dumps(data.json(), indent=4))
except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to League client. Is the game running?")
except requests.exceptions.Timeout:
        print("⏰ Request timeout. Retrying...")
        time.sleep(5)
            
except json.JSONDecodeError:
        print("❌ Invalid JSON response from League API")
        time.sleep(5)
            
except KeyError as e:
        print(f"❌ Missing data in API response: {e}")
        time.sleep(5)
            
except Exception as e:
        print(f"❌ Unexpected error: {e}")
        time.sleep(5)
except KeyboardInterrupt:
    RPC.close()
    print("✅ RPC disconnected")