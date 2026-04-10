import requests
import pandas as pd
import time
from datetime import datetime
import os
import json

API_KEY = os.getenv("API_KEY")
if not API_KEY:
    API_KEY = "PEGA_AQUÍ_TU_API_KEY_PARA_PRUEBAS_LOCALES"   # ← Solo para pruebas en tu PC

BASE_URL = "https://open.faceit.com/data/v4"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

def get_spanish_ranking(max_pages=15):
    all_players = []
    print("🚀 Iniciando búsqueda GLOBAL de jugadores españoles...")

    for page in range(max_pages):
        offset = page * 100
        # Endpoint GLOBAL (sin /regions/eu) → suele funcionar mejor
        url = f"{BASE_URL}/rankings/games/cs2?offset={offset}&limit=100"
        
        r = requests.get(url, headers=HEADERS)
        print(f"Página {page+1} → Status: {r.status_code}")

        if r.status_code != 200:
            print(f"❌ Error: {r.text[:400]}")
            break

        data = r.json().get("items", [])
        print(f"   → {len(data)} jugadores en el ranking global")

        if not data:
            print("   → No hay más jugadores")
            break

        # Debug: mostramos el country de los primeros 5 jugadores para ver qué devuelve Faceit
        if page == 0:
            print("   → Ejemplo de countries en página 1:")
            for p in data[:5]:
                print(f"       {p.get('nickname')} → country = '{p.get('country')}'")

        for p in data:
            country = str(p.get("country", "")).lower()
            if country in ["es", "esp", "españa", "spain"]:
                player_id = p["player_id"]
                
                stats_url = f"{BASE_URL}/players/{player_id}/stats/cs2"
                stats_r = requests.get(stats_url, headers=HEADERS)
                stats = stats_r.json() if stats_r.status_code == 200 else {}

                map_stats = {}
                if "segments" in stats:
                    for seg in stats.get("segments", []):
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
                    "level": p.get("game_skill_level") or p.get("skill_level"),
                    "country": "ES",
                    "last_updated": datetime.now().isoformat(),
                    "map_stats": map_stats,
                    "lifetime_matches": stats.get("lifetime", {}).get("matches", "N/A")
                })

        time.sleep(0.7)

    print(f"\n🎉 TOTAL JUGADORES ESPAÑOLES ENCONTRADOS: {len(all_players)}")
    df = pd.DataFrame(all_players)
    df.to_json("ranking_espana_cs2.json", orient="records", force_ascii=False, indent=2)
    df.to_csv("ranking_espana_cs2.csv", index=False)
    print("✅ Archivos guardados")
    return df

if __name__ == "__main__":
    get_spanish_ranking()
