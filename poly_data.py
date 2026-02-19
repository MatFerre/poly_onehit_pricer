import requests
import json

def get_polymarket_data(slug):
    url = "https://gamma-api.polymarket.com/events"
    params = {"slug": slug}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if not data:
            return []

        event = data[0]
        markets = event.get('markets', [])
        
        output_table = []

        for market in markets:
            # 1. Récupération du titre brut (ex: "↑ 100,000")
            raw_title = market.get('groupItemTitle', market.get('question'))
            
            # 2. Logique de Direction (1 ou 0)
            # 1 = Call (Hausse), 0 = Put (Baisse)
            direction = 0 # Par défaut (ou -1 si vous préférez gérer les erreurs)
            
            if any(x in raw_title for x in ['↑', 'Up', 'High', 'Above']):
                direction = 1
            elif any(x in raw_title for x in ['↓', 'Down', 'Low', 'Below']):
                direction = 0
            
            # 3. Nettoyage du titre (On enlève les flèches pour garder juste le strike)
            clean_title = raw_title.replace('↑', '').replace('↓', '').strip()

            # 4. Prix
            try:
                prices = json.loads(market.get('outcomePrices', '["0", "0"]'))
                price_yes = float(prices[0])
            except:
                price_yes = 0.0

            volume = float(market.get('volume', 0))
            
            output_table.append({
                "strike": clean_title,    # Ex: "100,000"
                "direction": direction,   # 1 ou 0
                "price": price_yes,       # Ex: 0.02
                "volume": volume
            })

        # Tri par probabilité décroissante
        output_table.sort(key=lambda x: x['price'], reverse=True)

        return output_table

    except Exception as e:
        print(f"Erreur : {e}")
        return []

# --- TEST ---
if __name__ == "__main__":
    slug = "what-price-will-bitcoin-hit-in-february-2026"
    data = get_polymarket_data(slug)
    
    print(f"{'DIR':<5} | {'STRIKE':<15} | {'PRIX':<10}")
    print("-" * 35)
    for row in data:
        print(f"{row['direction']:<5} | {row['strike']:<15} | {row['price']:.3f}")