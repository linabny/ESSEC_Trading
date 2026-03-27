# Beta_Forecast.py

import streamlit as st
import yfinance as yf
import pandas as pd
from prophet import Prophet
import plotly.graph_objects as go
import datetime as dt

@st.cache_data
def get_stock_data(ticker, start_date, end_date):
    """Download and clean stock data once."""
    data = yf.download(ticker, start=start_date, end=end_date)
    if data.empty:
        return pd.DataFrame()
    data = data[['Close']].reset_index()
    data.columns = ['ds', 'y']
    data['ds'] = data['ds'].dt.tz_localize(None)
    return data.ffill().bfill()

@st.cache_resource
def run_beta_forecast(df, horizon):
    """Train Prophet model and generate forecast (cached)."""
    m = Prophet(daily_seasonality=True)
    m.fit(df)
    future = m.make_future_dataframe(periods=horizon)
    forecast = m.predict(future)
    return forecast

def main():
    # CSS to adjust content area width
    st.markdown(
        """
        <style>
        div.block-container { max-width: 90%; margin: auto; padding: 1rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("Stock Forecast")

    # Using the shortened, adapted description
    description = (
        "Predict future stock performance using the Prophet library. Select any asset and set a 1–365 day horizon "
        "to generate forecasts with confidence intervals. Analyze price targets—Min, Max, and Average—via our "
        "intuitive Recommendation Gauge, then export your findings to CSV."
    )

    st.markdown(f"<div style='text-align: justify;'>{description}</div>", unsafe_allow_html=True)
    st.write("")

    # Load data
    try:
        df_list = pd.read_csv("Data/data_trading.csv")
    except FileNotFoundError:
        st.error("Data file not found. Please check the 'Data/data_trading.csv' path.")
        return

    # Filter by Index
    st.header("Filter by Index")
    indices = df_list['Ind'].unique().tolist()
    selected_indices = st.multiselect("Select one or more indices", options=indices, default=indices)

    filtered_companies = df_list[df_list['Ind'].isin(selected_indices)] if selected_indices else df_list.copy()

    if filtered_companies.empty:
        st.warning("No companies found for the selected indices.")
        return

    # Company Selection
    company = st.selectbox("Select a company:", filtered_companies["Company"].tolist())
    ticker = filtered_companies[filtered_companies["Company"] == company]["Ticker"].values[0]
    horizon = st.slider("Forecast Horizon (in days):", 1, 365, 90)

    # Date setup
    current_date = dt.date.today().strftime('%Y-%m-%d')
    
    with st.spinner(f"Generating forecast for {ticker}..."):
        # 1. Get Data (Cached)
        data = get_stock_data(ticker, "2015-01-01", current_date)
        
        if data.empty:
            st.error("No data found for this ticker.")
            return

        # 2. Run Forecast (Cached)
        forecast = run_beta_forecast(data, horizon)

        # 3. Visualization (Starting from Day 1)
        fig = go.Figure()

        # Historical (Black)
        fig.add_trace(go.Scatter(x=data['ds'], y=data['y'], name="Historical Data", line=dict(color="black")))

        # Predictions (Blue - Future only)
        future_mask = forecast['ds'] > data['ds'].max()
        future_df = forecast[future_mask]
        
        fig.add_trace(go.Scatter(x=future_df['ds'], y=future_df['yhat'], name="Predictions", line=dict(color="blue")))

        # Confidence Intervals
        fig.add_trace(go.Scatter(x=future_df['ds'], y=future_df['yhat_upper'], line=dict(width=0), showlegend=False))
        fig.add_trace(go.Scatter(x=future_df['ds'], y=future_df['yhat_lower'], fill='tonexty', 
                                 fillcolor='rgba(173, 216, 230, 0.3)', line=dict(width=0), name="Confidence Interval"))

        fig.update_layout(title=f"Price Prediction for {company}", template="plotly_white", height=600,
                          xaxis_title="Date", yaxis_title="Price ($)")
        
        st.plotly_chart(fig, use_container_width=True, key="beta_main_chart")

        # 4. Metrics
        last_adjclose = data['y'].iloc[-1]
        prediction = future_df['yhat'].iloc[-1]
        borne_inf = future_df['yhat_lower'].iloc[-1]
        borne_sup = future_df['yhat_upper'].iloc[-1]

        st.write(f"### Prediction Statistics ({horizon} days)")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Current Price", f"{last_adjclose:.2f}")
        c2.metric("Predicted Price", f"{prediction:.2f}", f"{((prediction/last_adjclose)-1)*100:.2f}%")
        c3.metric("Min Forecast", f"{borne_inf:.2f}")
        c4.metric("Max Forecast", f"{borne_sup:.2f}")

        # 5. Recommendation Gauge
        percentage_delta = ((prediction - last_adjclose) / last_adjclose) * 100
        level = max(min(50 + percentage_delta * 5, 100), 0)

        if level >= 80: rec, col = "Strong Buy", "darkgreen"
        elif level >= 60: rec, col = "Buy", "green"
        elif level >= 40: rec, col = "Hold", "orange"
        elif level >= 20: rec, col = "Sell", "red"
        else: rec, col = "Strong Sell", "darkred"

        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number", value=level,
            title={'text': f"Recommendation: <b>{rec}</b>", 'font': {'color': col, 'size': 24}},
            gauge={'axis': {'range': [0, 100]}, 
                   'bar': {'color': "black"},
                   'steps': [
                       {'range': [0, 20], 'color': "darkred"},
                       {'range': [20, 40], 'color': "red"},
                       {'range': [40, 60], 'color': "orange"},
                       {'range': [60, 80], 'color': "green"},
                       {'range': [80, 100], 'color': "darkgreen"}]
                  }
        ))
        fig_gauge.update_layout(height=400)
        st.plotly_chart(fig_gauge, use_container_width=True, key="beta_gauge")

        # 6. Download
        csv = forecast.to_csv(index=False)
        st.download_button(
            label="Download Forecasts as CSV",
            data=csv,
            file_name=f"forecasts_{company.replace(' ', '_')}.csv",
            mime='text/csv'
        )

if __name__ == "__main__":
    main()