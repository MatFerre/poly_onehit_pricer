import pandas as pd
import numpy as np
from scipy.stats import norm
import matplotlib.pyplot as plt
import requests
from get_data import get_btc_price_binance

def pricing_one_touch_stable(S, K, T_jours, sigma, direction, r=0.045):
    """
    S : Prix Spot (ex: 96500)
    K : Strike / Barrière (ex: 100000)
    T_jours : Jours restants (ex: 15)
    sigma : Volatilité (ex: 0.60)
    direction : 'call' (Up) ou 'put' (Down)
    """
    # 1. Sécurités
    if T_jours <= 0: return 0.0
    T = T_jours / 365.0
    
    # 2. Vérification immédiate : Est-ce déjà gagné ?
    # Si on parie à la hausse (Call) et qu'on est DÉJÀ au-dessus du strike
    if direction == 1 and S >= K:
        return 100.0
        
    # Si on parie à la baisse (Put) et qu'on est DÉJÀ en-dessous du strike
    if direction == 0 and S <= K:
        return 100.0

    # 3. Paramètres mathématiques (Reiner & Rubinstein)
    try:
        mu = (r - 0.5 * sigma**2) / sigma**2
        lam = np.sqrt(mu**2 + 2 * r / sigma**2)
        
        # 4. Calcul selon la direction (avec inversion pour stabilité)
        if direction == 1:
            # UP-AND-IN : La barrière est en HAUT (K > S)
            # On utilise le ratio (S/K) qui est < 1 pour éviter l'explosion
            ratio = S / K 
            y = np.log(ratio) # Sera négatif
            z = y / (sigma * np.sqrt(T)) + lam * sigma * np.sqrt(T)
            
            # Formule stabilisée pour Call
            term1 = (ratio)**(-mu + lam) * norm.cdf(z)
            term2 = (ratio)**(-mu - lam) * norm.cdf(z - 2 * lam * sigma * np.sqrt(T))
            p = term1 + term2
            
        else: # direction == 'put'
            # DOWN-AND-IN : La barrière est en BAS (K < S)
            # On utilise le ratio (K/S) qui est < 1
            ratio = K / S
            y = np.log(ratio) # Sera négatif
            z = y / (sigma * np.sqrt(T)) + lam * sigma * np.sqrt(T)
            
            # Formule stabilisée pour Put
            term1 = (ratio)**(mu + lam) * norm.cdf(z)
            term2 = (ratio)**(mu - lam) * norm.cdf(z - 2 * lam * sigma * np.sqrt(T))
            p = term1 + term2

        # Résultat borné
        return max(0.0, min(100.0, p * 100))

    except Exception as e:
        print(f"Erreur Math: {e}")
        return 0.0
    
def filling_table(row):
    theorical_price = pricing_one_touch_stable(S, K= row["strike"], T_jours = 10, sigma=0.65, direction = row["direction"])
    return theorical_price


if __name__ == "__main__":
    S = get_btc_price_binance()
    sigma = 0.75
    df = pd.read_csv(r"C:\Users\utilisateur\Desktop\programmation\Polymarket\data.csv")
    df["strike"]=df["strike"].str.replace(",","").astype(float)
    print(df)
    df["theorical_price"] = df.apply(filling_table, axis =1)
    df.to_csv("data_priced.csv")