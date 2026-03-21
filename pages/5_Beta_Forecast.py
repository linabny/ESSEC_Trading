# Beta_Forecast.py

import streamlit as st 
import yfinance as yf
import pandas as pd 
from prophet import Prophet
import plotly.graph_objects as go 
import datetime as dt
import numpy as np


def main():
    #CSS pour ajuster la largeur de la zone de contenu
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

    st.title("Beta Forecast")

    description = (
        "Beta Forecast est une fonctionnalité avancée de π²Trading (actuellement en version beta) qui permet aux utilisateurs "
        "de réaliser des prévisions précises des prix d'actions à l'aide de la biliothèque Prophet. "
        "Après avoir sélectionné une entreprise parmi une liste préexistante, l'utilisateur "
        "peut définir un horizon de prévision (de 30 à 365 jours). L'application récupère les "
        "données historiques correspondantes et génère des prévisions accompagnées d'intervalles "
        "de confiance. Un tableau des métriques clés, incluant le prix actuel, les prévisions de "
        "prix minimum, maximum, et moyen, est affiché pour faciliter l'analyse. Enfin, une jauge "
        "de recommandation intuitive aide à interpréter les prévisions et à prendre des décisions "
        "d'investissement stratégiques. L'utilisateur peut également télécharger les résultats "
        "en format CSV pour une exploration ultérieure."
    )

    justified_description = f"""
    <div style='text-align: justify; text-justify: inter-word;'>
        {description}
    </div>
    """
    st.markdown(justified_description, unsafe_allow_html=True)

    st.write("")

    df = pd.read_csv("Data/data_pisquared.csv")

    #entreprise = st.selectbox("Choisissez une entreprise :", df['Company'])
    #Sélection de l'indice
    st.header("Filtrer par Indice")
    indices = df['Ind'].unique().tolist()
    selected_indices = st.multiselect(
        "Choisissez un ou plusieurs indices",
        options=indices,
        default=indices 
    )##

    if selected_indices:
        filtered_companies = df[df['Ind'].isin(selected_indices)]
    else:
        filtered_companies = df.copy()

    if filtered_companies.empty:
        st.warning("Aucune entreprise trouvée pour les indices sélectionnés.")

    #Sélection entreprise
    companies = filtered_companies["Company"].tolist()
    entreprise = st.selectbox("Choisissez une entreprise :", companies)

    #Afficher le ticker associé
    ticker = filtered_companies[filtered_companies["Company"] == entreprise]["Ticker"].values[0]

    #Pour que l'utilisateur puisse choisir la période de prévision
    horizon = st.slider("Horizon de prévision (en jours) :", min_value=30, max_value=365, value=90)

    #ticker = df.loc[df['Company'] == entreprise, 'Ticker'].values[0]

    #Pour obtenir la date d'aujourd'hui
    current_date = str(dt.date.today())

    data = yf.download(ticker, start="2015-01-01", end=current_date)

    data = data[['Close']].reset_index()

    #Convention pour prophet : y représente la valeur qu'on veut forecast et ds la date 
    data.columns = ['ds', 'y']

    #On doit garder la data dans un format YYYY-MM-DD donc on supprime le fuseau horaire : 
    data['ds'] = data['ds'].dt.tz_localize(None)

    #On initialise le modèle et on l'ajuste aux données
    m = Prophet()
    m.fit(data)

    #On ajoute des nouvelles dates aux dates qu'on a déjà et correspond à la période où on veut forecast le prix
    future = m.make_future_dataframe(periods=horizon)

    forecast = m.predict(future)

    fig = go.Figure()

    #Scatter plot des données historiques
    fig.add_trace(go.Scatter(
        x=data['ds'], y=data['y'],
        mode='lines',
        name="Données historiques",
        line=dict(color="black")
    ))

    #Scatter plot des données prédites
    fig.add_trace(go.Scatter(
        x=forecast['ds'], y=forecast['yhat'],
        mode='lines',
        name="Prédictions",
        line=dict(color="blue")
    ))

    #Intervalles de confiance
    fig.add_trace(go.Scatter(
        x=forecast['ds'], y=forecast['yhat_upper'],
        fill=None,
        mode='lines',
        line=dict(color='lightblue', dash='dot'),
        name="Intervalle supérieur"
    ))
    fig.add_trace(go.Scatter(
        x=forecast['ds'], y=forecast['yhat_lower'],
        fill='tonexty',
        mode='lines',
        line=dict(color='lightblue', dash='dot'),
        name="Intervalle inférieur"
    ))

    #Titres
    fig.update_layout(
        title="Prédiction des Prix Futures",
        height=600,
        width = 1000,
        xaxis_title="Date",
        yaxis_title="Prix ($)",
        template="plotly_white"
    )

    #Fonction pour afficher graph sur streamlit
    st.plotly_chart(fig, use_container_width=True)

    #Récupérer la dernier data de forecast pour ensuite prix max, min et actuel prédits
    last_date = forecast['ds'].iloc[-1]
    last_date_str = last_date.strftime('%Y-%m-%d')

    #Prix close le plus récent pour comparer aux prédictions
    last_adjclose = data['y'].iloc[-1]

    borne_inf = forecast.loc[forecast['ds'] == last_date_str]['yhat_lower'].values[0]
    borne_sup = forecast.loc[forecast['ds'] == last_date_str]['yhat_upper'].values[0]
    prediction = forecast.loc[forecast['ds'] == last_date_str]['yhat'].values[0]

    st.write(f"### Statistiques de la prédiction à {horizon} jours")
    metrics_labels = [
        "Prix actuel", "Prix prédit", "Prix prédit minimum", "Prix prédit maximum"
    ]
    metrics_values = [
        f"{last_adjclose:.2f}", f"{prediction:.2f}", f"{borne_inf:.2f}", f"{borne_sup:.2f}"
    ]

    num_metrics = len(metrics_labels)
    cols = st.columns(num_metrics)

    for col, label, value in zip(cols, metrics_labels, metrics_values):
        with col:
            st.metric(label, value)

    #Variation pourcentage prix
    percentage_delta = ((prediction - last_adjclose) / last_adjclose) * 100

    #Map variation à l'échelle 0-100
    niveau = max(min(50 + percentage_delta * 5, 100), 0)  

    #étiquette et couleur à afficher en fonction du niveau
    if 80 <= niveau <= 100:
        recommendation = "Strong Buy"
        text_color = "darkgreen"
    elif 60 <= niveau < 80:
        recommendation = "Buy"
        text_color = "green"
    elif 40 <= niveau < 60:
        recommendation = "Hold"
        text_color = "orange"
    elif 20 <= niveau < 40:
        recommendation = "Sell"
        text_color = "red"
    else:
        recommendation = "Strong Sell"
        text_color = "darkred"

    num_levels = 100 

    #Ce graphique à été réalisé à l'aide de ChatGPT
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge", 
        value=niveau,
        title={'text': "Recommandation"}, 
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "black"},
            'bar': {'color': "black", 'thickness': 0.2},
            'steps': [
                {'range': [i, i + 100 / num_levels], 
                'color': f"rgb({int(255 - (i * 2.55))},{int(i * 2.55)},0)"} 
                for i in np.linspace(0, 100, num_levels)
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': niveau
            }
        }
    ))

    #Ajouter le texte sous le graphique
    fig_gauge.add_trace(go.Scatter(
        x=[0.5],
        y=[-1.2],  
        text=[f"<b>{recommendation}</b>"],  
        mode="text",
        textfont=dict(size=50, color=text_color), 
        showlegend=False
    ))

    fig_gauge.update_layout(
        xaxis=dict(visible=False),  
        yaxis=dict(visible=False),  
        paper_bgcolor="white"       
    )

    st.plotly_chart(fig_gauge, use_container_width=True)

    #Permet à l'utilsateur de télécharger le dataframe des prévisions en CSV
    csv = forecast.to_csv(index=False)
    st.download_button(
        label="Télécharger les prévisions en CSV",
        data=csv,
        file_name=f"previsions_{entreprise}.csv",
        mime='text/csv'
    )

if __name__ == "__main__":
    main()
