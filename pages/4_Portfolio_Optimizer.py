# Libraires pour la page 'Portfolio Optimizer'

import pandas as pd
import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
import numpy as np
from utils.graph_utils import plot_performance, plot_pie
from utils.optimizer_utils import calculate_PP, get_risk_free_rate
from utils.optimizer_utils import calculate_FE, plot_FE, plot_portfolio_performance

# Frontière d'efficience codé à l'aide de : https://youtu.be/Isutk-wqJfE?si=a2HVgMUsLGivkm0E

description_page = (
    "Portfolio Optimizer permet aux utilisateurs de récupérer le portefeuille "
    "créé dans la section Portfolio Visualizer pour une analyse approfondie. Le "
    "portefeuille est résumé à travers un tableau récapitulatif des principales "
    "statistiques et un graphique illustrant la répartition des poids entre les "
    "entreprises. Ensuite, π² Trading calcule la frontière d’efficience à l’aide "
    "de la Modern Portfolio Theory pour optimiser les rendements. La plateforme "
    "affiche ensuite la frontière d’efficience avec la position actuelle du portefeuille "
    "et propose un portefeuille optimal, soit pour minimiser la volatilité, soit pour "
    "maximiser le ratio Sharpe. Les rendements des différents portefeuilles ainsi "
    "obtenus sont représentés graphiquement sur une échelle de temps 10 ans."
)


def main():

    # CSS pour ajuster la largeur de la zone de contenu
    st.markdown(
        """
        <style>
        div.block-container {
            max-width: 90%;
            margin: auto;
            padding: 1rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Header de la page
    st.title("Portfolio optimizer")
    justified_description = f"""
    <div style='text-align: justify; text-justify: inter-word;'>
        {description_page}
    </div>
    """
    st.markdown(justified_description, unsafe_allow_html=True)

    risk_free_rate = get_risk_free_rate()
    st.write(
        f"*Note à l'utilisateur* : par défaut, l'historique des données utilisé est fixé à 10 ans. "
        f"Le taux sans risque considéré est celui "
        f"du rendement des obligations US à 10 ans, obtenu depuis l'API FRED i.e. *r* = "
        f"{risk_free_rate:.3%}."
    )
    # L'utilisateur a bien rentré un portefeuille dans la page 'Portfolio Visualizer'
    if 'portfolio' in st.session_state and not st.session_state['portfolio'].empty:

        data = st.session_state['portfolio']
        portfolio_df = data

        for i in range(len(portfolio_df)):
            portfolio_df.loc[i, 'Industrie'] = yf.Ticker(portfolio_df.loc[i, 'Actions']).info.get('industry', 'N/A')
        grouped_by_industry = portfolio_df.groupby('Industrie')['Poids (%)'].apply(np.sum).reset_index()

        st.write("### Portefeuille actuel")

        fig_table = go.Figure(data=[go.Table(
            header=dict(
                values=list(portfolio_df.columns),
                fill_color='#0611ab',
                font=dict(color='white', size=14),
                align='center',
                height=40
            ),
            cells=dict(
                values=[portfolio_df.Actions, portfolio_df["Nom de l'Entreprise"], portfolio_df['Poids (%)'], portfolio_df['Industrie']],
                fill_color=['#f8f9fa']*len(data),
                font=dict(color='black', size=12),
                align='center',
                height=30
            )
        )])
        fig_table.update_layout(
            width=600,
            height=200,
            margin=dict(l=0, r=0, t=40, b=0)
        )
        st.plotly_chart(fig_table, use_container_width=True, key="optimisation_portfolio_table")

        poids_tot = data['Poids (%)'].sum()
        poids_moy = data['Poids (%)'].mean()
        poids_max = data['Poids (%)'].max()
        poids_min = data['Poids (%)'].min()

        # Rendement attendu (annualisé)
        tickers = data['Actions'].tolist()
        weights = np.array(data['Poids (%)'].tolist()) / 100

        if len(tickers) > 0:
            try:
                portfolio_cumulative, portfolio_returns = calculate_PP(
                    tickers,
                    weights,
                    period='1y'
                )
                expected_return = portfolio_returns.mean() * 252  # 252 jours de bourse par an

                # Volatilité (annualisée)
                volatility = portfolio_returns.std() * np.sqrt(252)

                # Ratio de Sharpe (avec un taux sans risque de 2%)
                if volatility != 0:
                    sharpe_ratio = (expected_return - risk_free_rate) / volatility
                else:
                    np.nan

                st.write("### Statistiques du Portefeuille")
                metrics_labels = [
                    "Poids Total", "Poids Moyen", "Poids Maximum", "Poids Minimum",
                    "Rendement Attendu", "Volatilité", "Ratio de Sharpe"
                ]
                metrics_val = [
                    f"{poids_tot:.2f}%", f"{poids_moy:.2f}%", f"{poids_max:.2f}%",
                    f"{poids_min:.2f}%", f"{expected_return*100:.2f}%",
                    f"{volatility*100:.2f}%", f"{sharpe_ratio:.2f}"
                ]
                metrics_des = [
                    "La somme des poids doit être de 100%.", "", "", "",
                    "Rendement attendu annualisé.", "Volatilité annualisée du portefeuille.",
                    "Ratio de Sharpe (rendement ajusté au risque)."
                ]

                num_metrics = len(metrics_labels)
                cols = st.columns(num_metrics)

                for col, label, value, des in zip(cols, metrics_labels, metrics_val, metrics_des):
                    with col:
                        st.metric(label, value)
                        if des:
                            st.caption(des)

                graph_cols = st.columns(2)

                with graph_cols[0]:
                    st.write("### Répartition du portefeuille par industrie")
                    grouped_sorted = grouped_by_industry.sort_values(by='Poids (%)', ascending=False)
                    plot_pie(grouped_sorted, 'Industrie')  #Module des fonctions graphiques

                with graph_cols[1]:
                    st.write("### Répartition des poids dans le portefeuille")
                    portfolio_df_sorted = portfolio_df.sort_values(by='Poids (%)', ascending=False)
                    plot_pie(portfolio_df_sorted, 'Actions')  #Module des fonctions graphiques

                st.write("### Performance historique du portefeuille")
                plot_performance(portfolio_cumulative)

                st.session_state['portfolio'] = data
                # st.success("✅ Le portefeuille a été enregistré pour une utilisation ultérieure.")

            except ValueError as ve:
                st.error(f"Erreur lors du calcul des performances du portefeuille : {ve}")
            except Exception as e:
                st.error(f"Une erreur est survenue lors de l'optimisation : {e}")

        st.write("### Optimisation du portefeuille avec MPT")

        data = st.session_state['portfolio']
        tickers = data['Actions'].tolist()
        weights = np.array(data['Poids (%)'].tolist()) / 100
        stock_data = yf.download(tickers, period='10y')['Close']
        returns = stock_data.pct_change().mean() * 252
        cov_matrix = stock_data.pct_change().cov() * 252
        individual_volatility = np.sqrt(np.diag(cov_matrix))

        # Simuler les portefeuilles
        portfolios, min_vol_pf, max_sharpe_pf, current_portfolio_metrics = calculate_FE(
            returns=returns,
            cov_matrix=cov_matrix,
            risk_free_rate=risk_free_rate,
            portfolio_weights=weights
        )

        # Appeler la fonction plot_FE pour créer le graphique
        fig = plot_FE(
            portfolios=portfolios,
            min_volatility_portfolio=min_vol_pf,
            max_sharpe_portfolio=max_sharpe_pf,
            current_portfolio_metrics=current_portfolio_metrics,
            individual_volatility=individual_volatility,
            individual_returns=returns,
            asset_names=tickers
        )

        # Afficher le graphique
        st.plotly_chart(fig)

        # Ajouter les détails des portefeuilles optimaux
        sep = st.columns(2)

        # Ignorer ligne 0, garder pondérations
        weights_min_volatility = min_vol_pf.iloc[0:-3].values
        weights_max_sharpe = max_sharpe_pf.iloc[0:-3].values

        # Préparer les données pour le camembert
        min_volatility_portfolio_df = pd.DataFrame({
            # Associe les tickers aux pondérations
            'Actions': tickers[:len(weights_min_volatility)],
            # Convertit les poids en pourcentages
            'Poids (%)': weights_min_volatility * 100
        }).sort_values(by='Poids (%)', ascending=False)
        max_sharpe_portfolio_df = pd.DataFrame({
            'Actions': tickers[:len(weights_max_sharpe)],
            'Poids (%)': weights_max_sharpe * 100
        }).sort_values(by='Poids (%)', ascending=False)

        with sep[0]:
            st.write("### Portefeuille à Volatilité Minimale")
            plot_pie(min_volatility_portfolio_df, 'Actions')

        with sep[1]:
            st.write("### Portefeuille avec Sharpe Maximal")
            plot_pie(max_sharpe_portfolio_df, 'Actions')

        st.write("### Comparaison des Performances des Portefeuilles sur 10 Ans")
        fig = plot_portfolio_performance(
            tickers=tickers,
            weights=weights,
            min_vol_weights=min_vol_pf[:len(weights)].values,
            max_sharpe_weights=max_sharpe_pf[:len(weights)].values,
            period='10y'
        )
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info(
            "Veuillez créer un portefeuille dans la section **Portfolio Visualizer**"
            "avant de procéder à l'optimisation."
        )


if __name__ == "__main__":
    main()
