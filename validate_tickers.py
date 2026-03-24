"""
Script pour valider les tickers dans data_trading.csv
Identifie les tickers qui ne fonctionnent pas avec yfinance
"""

import pandas as pd
import yfinance as yf

# Charger le CSV
df = pd.read_csv("Data/data_trading.csv")

print(f"Total tickers à vérifier: {len(df)}\n")

invalid_tickers = []
valid_tickers = []

for idx, row in df.iterrows():
    ticker = row['Ticker'].strip().upper()
    
    # Afficher la progression tous les 10 tickers
    if (idx + 1) % 10 == 0:
        print(f"⏳ Progression: {idx + 1}/{len(df)} tickers vérifiés...")
    
    try:
        # Essayer de télécharger 1 jour de données
        data = yf.download(ticker, period='1d', progress=False)
        
        if data.empty:
            invalid_tickers.append((ticker, row['Company'], "Pas de données disponibles"))
        else:
            # Vérifier si on peut récupérer les infos
            info = yf.Ticker(ticker).info
            company_name = info.get('longName', 'N/A')
            valid_tickers.append(ticker)
            
    except Exception as e:
        invalid_tickers.append((ticker, row['Company'], str(e)))

print("\n" + "="*80)
print(f"✅ TICKERS VALIDES: {len(valid_tickers)}")
print("="*80)

print("\n" + "="*80)
print(f"❌ TICKERS INVALIDES: {len(invalid_tickers)}")
print("="*80)

if invalid_tickers:
    for ticker, company, reason in invalid_tickers:
        print(f"{ticker:12} | {company:40} | {reason}")
    
    print("\n" + "="*80)
    print("Tickers à supprimer (copier/coller dans une requête de remplacement):")
    print("="*80)
    for ticker, company, _ in invalid_tickers:
        print(f"{ticker},{company},")
else:
    print("\n✅ Tous les tickers sont valides!")

print(f"\nRésumé: {len(valid_tickers)} valides, {len(invalid_tickers)} invalides")
