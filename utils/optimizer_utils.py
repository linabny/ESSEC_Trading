# Utils pour la page 'Portfolio Optimizer'

import pandas as pd
import yfinance as yf
import plotly.graph_objs as go
import requests
import numpy as np


def calculate_PP(tickers, weights, period='1y'):
    """
    Calcule les performances d'un portefeuille sur une période donnée.

    :param tickers: Liste des tickers des actifs.
    :param weights: Pondérations des actifs dans le portefeuille.
    :param period: Période pour télécharger les données (par défaut '1y').
    :return: Tuple (cumul des rendements du portefeuille, rendements journaliers du portefeuille).
    """
    # Téléchargement des prix ajustés des tickers
    data = yf.download(tickers, period=period)['Close']

    # Gérer le cas où un seul ticker est fourni (data devient une série au lieu d'un DataFrame)
    if isinstance(data, pd.Series):
        data = data.to_frame()

    # Calcul des rendements journaliers
    returns = data.pct_change().dropna()

    # Calcul des rendements pondérés du portefeuille
    weighted_returns = returns.multiply(weights, axis=1)
    # Somme des rendements pondérés pour chaque jour
    portfolio_returns = weighted_returns.sum(axis=1)

    # Calcul des rendements cumulés du portefeuille
    portfolio_cumulative = (1 + portfolio_returns).cumprod()

    return portfolio_cumulative, portfolio_returns


def get_risk_free_rate(api_key="f1f1a2d3abcf1f08e76d3bc4fc1efd19"):
    """
    Récupère le taux sans risque (rendement des obligations à 10 ans) depuis l'API FRED.

    Si une erreur survient, retourne un taux par défaut de 2 %.

    :param api_key: Clé API pour accéder à l'API FRED.
    :return: Taux sans risque sous forme de float (par exemple, 0.02 pour 2 %).
    """
    url = 'https://api.stlouisfed.org/fred/series/observations'
    params = {
        'series_id': 'DGS10',
        'api_key': api_key,
        'file_type': 'json',
        'sort_order': 'desc',
        'limit': 1
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Vérifie les erreurs HTTP
        data = response.json()
        # Retourne le premier taux disponible, converti en décimal
        return float(data['observations'][0]['value']) / 100
    except Exception:
        # Retourne un taux par défaut de 2 % en cas d'erreur
        return 0.02


def calculate_portfolio_metrics(weights, returns, cov_matrix, risk_free_rate):
    """
    Calcule les métriques d'un portefeuille : rendement attendu, volatilité et ratio de Sharpe.

    :param weights: Liste ou tableau des pondérations des actifs dans le portefeuille.
    :param returns: Liste ou tableau des rendements attendus des actifs.
    :param cov_matrix: Matrice de covariance des actifs.
    :param risk_free_rate: Taux sans risque (float).
    :return: Tuple (rendement attendu, volatilité, ratio de Sharpe).
    """
    weights = np.array(weights)  # Conversion en tableau NumPy
    portfolio_return = np.dot(returns, weights)  # Rendement attendu du portefeuille

    # Calcul de la variance et de la volatilité
    portfolio_variance = np.dot(weights, np.dot(cov_matrix, weights))
    portfolio_volatility = np.sqrt(portfolio_variance)

    # Calcul du ratio de Sharpe
    if portfolio_volatility:
        sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_volatility
    else:
        0

    return portfolio_return, portfolio_volatility, sharpe_ratio


def simulate_portfolios(returns, cov_matrix, risk_free_rate, num_portfolios=10000):
    """
    Génère des portefeuilles aléatoires pour simuler la frontière efficiente.

    :param returns: Liste ou tableau des rendements attendus des actifs.
    :param cov_matrix: Matrice de covariance des actifs.
    :param risk_free_rate: Taux sans risque (float).
    :param num_portfolios: Nombre de portefeuilles à simuler (int).
    :return: Tableau NumPy contenant pondérations, rendements, volatilités et ratios de
    Sharpe pour chaque portefeuille.
    """
    num_assets = len(returns)
    results = np.zeros((num_portfolios, num_assets + 3))  # Colonnes : pondérations + métriques

    for i in range(num_portfolios):
        weights = np.random.random(num_assets)     # Génération de pondérations aléatoires
        weights /= weights.sum()                   # Normalisation à 1

        # Calcul des métriques pour le portefeuille
        portfolio_return, portfolio_volatility, sharpe_ratio = calculate_portfolio_metrics(
            weights, returns, cov_matrix, risk_free_rate
        )

        # Stockage des résultats
        results[i, :num_assets] = weights
        results[i, num_assets:] = portfolio_return, portfolio_volatility, sharpe_ratio

    return results


def calculate_FE(returns, cov_matrix, risk_free_rate, portfolio_weights):
    """
    Effectue les calculs pour la frontière efficiente.

    :param returns: Rendements moyens des actifs.
    :param cov_matrix: Matrice de covariance des actifs.
    :param risk_free_rate: Taux sans risque.
    :param portfolio_weights: Pondérations du portefeuille actuel.
    :return: Un tuple contenant le DataFrame des portefeuilles simulés,
             le portefeuille à volatilité minimale et le portefeuille au Sharpe maximal.
    """
    # Simuler les portefeuilles
    num_assets = len(returns)
    num_portfolios = 10000
    results = np.zeros((num_portfolios, num_assets + 3))  # Colonnes : pondérations + métriques

    for i in range(num_portfolios):
        weights = np.random.random(num_assets)
        weights /= weights.sum()  # Normalisation à 1
        portfolio_return, portfolio_volatility, sharpe_ratio = calculate_portfolio_metrics(
            weights, returns, cov_matrix, risk_free_rate
        )
        results[i, :num_assets] = weights
        results[i, num_assets:] = portfolio_return, portfolio_volatility, sharpe_ratio

    # Convertir en DataFrame
    columns = (
        [f'Weight {i+1}' for i in range(num_assets)]
        + ['Rendement', 'Volatilité', 'Ratio de Sharpe']
    )
    portfolios = pd.DataFrame(results, columns=columns)

    # Trouver les portefeuilles optimaux
    min_volatility_idx = portfolios['Volatilité'].idxmin()
    max_sharpe_idx = portfolios['Ratio de Sharpe'].idxmax()

    min_volatility_portfolio = portfolios.iloc[min_volatility_idx]
    max_sharpe_portfolio = portfolios.iloc[max_sharpe_idx]

    # Calculer les métriques du portefeuille actuel
    portfolio_return, portfolio_volatility, sharpe_ratio = calculate_portfolio_metrics(
        portfolio_weights, returns, cov_matrix, risk_free_rate
    )
    current_portfolio_metrics = {
        "Rendement": portfolio_return * 100,
        "Volatilité": portfolio_volatility * 100,
        "Ratio de Sharpe": sharpe_ratio
    }

    return portfolios, min_volatility_portfolio, max_sharpe_portfolio, current_portfolio_metrics


# FE améliorée à l'aide de ChatGPT
def plot_FE(portfolios, min_volatility_portfolio, max_sharpe_portfolio, current_portfolio_metrics,
            individual_volatility, individual_returns, asset_names):
    """
    Trace la frontière efficiente avec les portefeuilles simulés.

    :param portfolios: DataFrame des portefeuilles simulés.
    :param min_volatility_portfolio: Portefeuille à volatilité minimale.
    :param max_sharpe_portfolio: Portefeuille avec le Sharpe maximal.
    :param current_portfolio_metrics: Dictionnaire contenant les métriques du portefeuille actuel.
    :param individual_volatility: Volatilité individuelle des actifs.
    :param individual_returns: Rendements individuels des actifs.
    :param asset_names: Liste des noms des actifs.
    :return: Objet Plotly `Figure`.
    """
    fig = go.Figure()

    # Tracer les portefeuilles simulés
    fig.add_trace(go.Scatter(
        x=portfolios['Volatilité'] * 100,
        y=portfolios['Rendement'] * 100,
        mode='markers',
        marker=dict(
            size=5,
            color=portfolios['Ratio de Sharpe'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title='Ratio de Sharpe')
        ),
        text=portfolios['Ratio de Sharpe'],
        name='Portefeuilles simulés'
    ))

    # Ajouter le portefeuille actuel
    fig.add_trace(go.Scatter(
        x=[current_portfolio_metrics["Volatilité"]],
        y=[current_portfolio_metrics["Rendement"]],
        mode='markers+text',
        marker=dict(color='black', size=12, symbol='hexagram'),
        text=['Portefeuille Actuel'],
        textposition="top center",
        name='Portefeuille Actuel'
    ))

    # Ajouter les actifs individuels
    fig.add_trace(go.Scatter(
        x=individual_volatility * 100,
        y=individual_returns * 100,
        mode='markers+text',
        marker=dict(color='blue', size=8),
        text=asset_names,
        textposition="top center",
        name='Actifs'
    ))

    # Ajouter le portefeuille à volatilité minimale
    fig.add_trace(go.Scatter(
        x=[min_volatility_portfolio['Volatilité'] * 100],
        y=[min_volatility_portfolio['Rendement'] * 100],
        mode='markers+text',
        marker=dict(color='magenta', size=12, symbol='star-diamond'),
        text=['Min Vol'],
        textposition="top center",
        name='Portefeuille à Volatilité Minimale'
    ))

    # Ajouter le portefeuille avec Sharpe maximal
    fig.add_trace(go.Scatter(
        x=[max_sharpe_portfolio['Volatilité'] * 100],
        y=[max_sharpe_portfolio['Rendement'] * 100],
        mode='markers+text',
        marker=dict(color='red', size=12, symbol='star-diamond'),
        text=['Max Sharpe'],
        textposition="top center",
        name='Portefeuille avec Sharpe Maximal'
    ))

    # Mettre à jour la mise en page
    fig.update_layout(
        title='Frontière efficiente avec portefeuilles et actifs',
        xaxis_title='Volatilité (%)',
        yaxis_title='Rendement attendu (%)',
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.3,
            xanchor="center",
            x=0.5
        ),
        width=800,
        height=600
    )

    return fig


def plot_portfolio_performance(tickers, weights, min_vol_weights, max_sharpe_weights, period='10y'):
    """
    Trace la performance cumulée des portefeuilles sur une période donnée.

    :param tickers: Liste des tickers des actifs du portefeuille.
    :param weights: Pondérations du portefeuille original.
    :param min_vol_weights: Pondérations du portefeuille à volatilité minimale.
    :param max_sharpe_weights: Pondérations du portefeuille avec Sharpe maximal.
    :param period: Période pour les calculs (par défaut '10y').
    :return: Objet Plotly `Figure`.
    """
    # Calculer les performances cumulées
    # Portefeuille original
    original_cumulative, _ = calculate_PP(tickers, weights, period=period)

    # Portefeuille à volatilité minimale
    min_vol_cumulative, _ = calculate_PP(tickers, min_vol_weights, period=period)

    # Portefeuille avec Sharpe maximal
    max_sharpe_cumulative, _ = calculate_PP(tickers, max_sharpe_weights, period=period)

    # Tracer les performances cumulées
    fig = go.Figure()

    # Performance du portefeuille original
    fig.add_trace(go.Scatter(
        x=original_cumulative.index,
        y=original_cumulative.values,
        mode='lines',  # Lignes sans marqueurs
        name='Portefeuille Original',
        line=dict(color='#0611ab', width=3)
    ))

    # Performance du portefeuille à volatilité minimale
    fig.add_trace(go.Scatter(
        x=min_vol_cumulative.index,
        y=min_vol_cumulative.values,
        mode='lines',  # Lignes sans marqueurs
        name='Portefeuille Volatilité Minimale',
        line=dict(color='green', width=3)
    ))

    # Performance du portefeuille avec Sharpe maximal
    fig.add_trace(go.Scatter(
        x=max_sharpe_cumulative.index,
        y=max_sharpe_cumulative.values,
        mode='lines',  # Lignes sans marqueurs
        name='Portefeuille Sharpe Maximal',
        line=dict(color='gold', width=3)
    ))

    # Mettre à jour la mise en page du graphique
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Valeur Cumulative',
        template='plotly_white',
        height=550,
        margin=dict(l=50, r=50, t=30, b=50),
        hovermode='x unified',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor='lightgray',
            zeroline=True,
            zerolinecolor='black',
            zerolinewidth=1
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='lightgray',
            zeroline=True,
            zerolinecolor='black',
            zerolinewidth=1
        ),
        plot_bgcolor='rgba(255, 255, 255, 0.9)',
        paper_bgcolor='rgba(255, 255, 255, 1)',
    )

    return fig
