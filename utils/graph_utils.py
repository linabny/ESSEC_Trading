# utils/graph_utils.py
import plotly.graph_objs as go
import plotly.express as px
import streamlit as st

#Ces deux graphiques ont d'abord été implémentés par nous-même puis amélioré à l'aide de ChatGPT

def plot_performance(portfolio_cumulative):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=portfolio_cumulative.index,
        y=portfolio_cumulative.values,
        mode='lines+markers',
        name='Performance du Portefeuille',
        line=dict(color='#0611ab', width=3),
        marker=dict(size=6, color='#0611ab')
    ))
    
    fig.update_layout(
        title='',
        xaxis_title='Date',
        yaxis_title='Valeur Cumulative',
        template='plotly_white',
        height=550,
        margin=dict(l=50, r=50, t=30, b=50),
        hovermode='x unified',
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=0
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

    st.plotly_chart(fig, use_container_width=True)

def plot_pie(portfolio_df_sorted, col):
    colors = px.colors.sequential.Plasma
    fig = px.pie(
        portfolio_df_sorted,
        names=col,
        values='Poids (%)',
        hole=0.3,
        color=col,
        color_discrete_sequence=colors,
        #hover_data=['Nom de l\'Entreprise', 'Poids (%)'],
        labels={'Poids (%)': 'Poids (%)'},
        template='plotly_white'
    )

    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        marker=dict(line=dict(color='#ffffff', width=1)),
        pull=[0.1 if x == 'Autres' else 0 for x in portfolio_df_sorted[col]],
        hovertemplate='<b>%{label}</b><br>Poids: %{value:.2f}%<br>Valeur: %{percent:.2f}%'
    )

    fig.update_layout(
        title='',
        showlegend=True,
        legend=dict(title=col, orientation='h'),
        height=550,
        margin=dict(t=50, b=50, l=50, r=50),
        annotations=[dict(text='Portefeuille', x=0.5, y=0.5, font_size=14, showarrow=False)],
        transition=dict(duration=500)
    )

    st.plotly_chart(fig, use_container_width=True)
