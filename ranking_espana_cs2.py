import requests
import pandas as pd
import time
from datetime import datetime
import os
import json

# ←←← LEE LA API KEY desde variable de entorno (GitHub la pone automáticamente)
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    API_KEY = "PEGA_AQUÍ_TU_API_KEY_PARA_PRUEBAS_LOCALES"  # solo para probar en tu PC

BASE_URL = "https://open.faceit.com/data/v4"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

def get_spanish_ranking(max_pages=30):
    all_players = []
    for page in range(max_pages):
        offset = page * 100
        url = f"{BASE_URL}/rankings/games/cs2/regions/eu?country=es&offset={offset}&limit=100"
        
        r = requests.get(url, headers=HEADERS)
        if r.status_code == 401:
            print("❌ API Key inválida o no encontrada")
            return None
        if r.status_code != 200:
            print(f"❌ Error página {page+1}: {r.status_code}")
            break
        
        data = r.json().get("items", [])
        if not data:
            break
        
        for p in data:
            player_id = p["player_id"]
            stats_url = f"{BASE_URL}/players/{player_id}/stats/cs2"
            stats_r = requests.get(stats_url, headers=HEADERS)
            stats = stats_r.json() if stats_r.status_code == 200 else {}
            
            map_stats = {}
            if "segments" in stats:
                for seg in stats["segments"]:
                    if seg.get("mode") == "5v5":
                        map_name = seg.get("label", "Unknown")
                        map_stats[map_name] = {
                            "winrate": seg.get("stats", {}).get("Win Rate %", "N/A"),
                            "kd": seg.get("stats", {}).get("K/D Ratio", "N/A"),
                            "rounds": seg.get("stats", {}).get("Rounds", "N/A")
                        }
            
            all_players.append({
                "position": p.get("position"),
                "nickname": p["nickname"],
                "player_id": player_id,
                "elo": p.get("faceit_elo"),
                "level": p.get("skill_level"),
                "country": "ES",
                "last_updated": datetime.now().isoformat(),
                "map_stats": map_stats,
                "lifetime_matches": stats.get("lifetime", {}).get("matches", "N/A")
            })
        
        print(f"✅ Página {page+1}/{max_pages} → {len(data)} jugadores")
        time.sleep(0.6)
    
    df = pd.DataFrame(all_players)
    df.to_json("ranking_espana_cs2.json", orient="records", force_ascii=False, indent=2)
    df.to_csv("ranking_espana_cs2.csv", index=False)
    print(f"\n🎉 Ranking guardado! Total jugadores españoles: {len(df)}")
    return df

if __name__ == "__main__":
    get_spanish_ranking()