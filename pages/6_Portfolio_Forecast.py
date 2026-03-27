# Portfolio_Forecast.py

import streamlit as st
import yfinance as yf
import pandas as pd
from prophet import Prophet
import plotly.graph_objects as go
import datetime as dt
import numpy as np
from utils.optimizer_utils import calculate_efficient_frontier, get_risk_free_rate

# Cache functions for performance optimization

@st.cache_data
def get_historical_data(tickers, start_date, end_date):
    """Download and clean data only once."""
    data = yf.download(tickers, start=start_date, end=end_date)['Close']
    if len(tickers) == 1:
        data = data.to_frame()
    return data.ffill().bfill()

@st.cache_resource
def run_prophet_forecast(df_prices, horizon):
    """ Train model and generate forecast (cached)."""
    # Prepare Prophet format
    df_prophet = pd.DataFrame({
        'ds': df_prices.index.tz_localize(None),
        'y': df_prices.values
    })
    
    model = Prophet(daily_seasonality=True)
    model.fit(df_prophet)
    
    future = model.make_future_dataframe(periods=horizon)
    forecast = model.predict(future)
    return df_prophet, forecast

def calculate_portfolio_price(stock_data, weights):
    """Calculate historical portfolio price based on weights"""
    weights = np.array(weights) / np.sum(weights)
    portfolio_value = (stock_data * weights).sum(axis=1)
    return portfolio_value

def main():
    # CSS to adjust content area width
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

    st.title("Portfolio Forecast")

    description = (
        "Predict the future of your entire strategy using the Facebook Prophet library. Select a stock, set your horizon (1-365 days), and generate forecasts with confidence intervals. Analyze key metrics—including min, max, and average price targets—via our intuitive Recommendation Gauge, then export your results to CSV. "
    )

    justified_description = f"""
    <div style='text-align: justify; text-justify: inter-word;'>
        {description}
    </div>
    """
    st.markdown(justified_description, unsafe_allow_html=True)

    st.write("")

    if 'portfolio' not in st.session_state or st.session_state['portfolio'].empty:
        st.info("Please create a portfolio in the **Portfolio Visualizer** section first.")
        return

    # Data Setup
    portfolio_data = st.session_state['portfolio']
    tickers = portfolio_data['Ticker'].tolist()
    weights = np.array(portfolio_data['Weight (%)'].tolist()) / 100
    horizon = st.slider("Forecast Horizon (days):", 1, 365, 90)
    
    try:
        # Download historical data for the portfolio
        hist_start = "2015-01-01"
        today = dt.date.today().strftime('%Y-%m-%d')
        stock_data = get_historical_data(tickers, hist_start, today)

        # Calculate returns and covariance for efficient frontier
        returns = stock_data.pct_change().mean() * 252
        cov_matrix = stock_data.pct_change().cov() * 252
        _, min_vol_pf, max_sharpe_pf, _ = calculate_efficient_frontier(
            returns, cov_matrix, get_risk_free_rate(), weights
        )

        strategies = {
            "Original Portfolio": weights,
            "Minimum Volatility Portfolio": min_vol_pf.iloc[0:-3].values,
            "Maximum Sharpe Portfolio": max_sharpe_pf.iloc[0:-3].values
        }

        tabs = st.tabs(list(strategies.keys()))

        for tab, (name, strat_weights) in zip(tabs, strategies.items()):
            with tab:
                st.subheader(f"{name} Analysis")

                # Forecast price series for the portfolio
                price_series = calculate_portfolio_price(stock_data, strat_weights)
                hist_df, forecast = run_prophet_forecast(price_series, horizon)

                fig = go.Figure()
                
                fig.add_trace(go.Scatter(x=hist_df['ds'], y=hist_df['y'], name="Historical", line=dict(color="black")))
                
                future_mask = forecast['ds'] > hist_df['ds'].max()
                future_df = forecast[future_mask]
                
                fig.add_trace(go.Scatter(x=future_df['ds'], y=future_df['yhat'], name="Forecast", line=dict(color="blue")))
                
                fig.add_trace(go.Scatter(x=future_df['ds'], y=future_df['yhat_upper'], line=dict(width=0), showlegend=False))
                fig.add_trace(go.Scatter(x=future_df['ds'], y=future_df['yhat_lower'], fill='tonexty', 
                                         fillcolor='rgba(173, 216, 230, 0.3)', line=dict(width=0), name="Confidence Interval"))

                fig.update_layout(template="plotly_white", height=500, xaxis_title="Date", yaxis_title="Portfolio Value ($)")
                
                st.plotly_chart(fig, use_container_width=True, key=f"chart_{name.replace(' ', '_')}")

                # Metrics
                last_price = price_series.iloc[-1]
                pred_price = future_df['yhat'].iloc[-1]
                p_min = future_df['yhat_lower'].iloc[-1]
                p_max = future_df['yhat_upper'].iloc[-1]

                st.write("### Prediction Statistics")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Current Price", f"{last_price:.2f}")
                c2.metric("Predicted Price", f"{pred_price:.2f}", f"{((pred_price/last_price)-1)*100:.2f}%")
                c3.metric("Min Forecast", f"{p_min:.2f}")
                c4.metric("Max Forecast", f"{p_max:.2f}")

                # Recommandation gauge
                perc_delta = ((pred_price - last_price) / last_price) * 100
                level = max(min(50 + perc_delta * 5, 100), 0)

                if level >= 80: rec, col = "Strong Buy", "darkgreen"
                elif level >= 60: rec, col = "Buy", "green"
                elif level >= 40: rec, col = "Hold", "orange"
                elif level >= 20: rec, col = "Sell", "red"
                else: rec, col = "Strong Sell", "darkred"

                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge", value=level,
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
                fig_gauge.update_layout(height=350, margin=dict(t=50, b=0))

                st.plotly_chart(fig_gauge, use_container_width=True, key=f"gauge_{name.replace(' ', '_')}")

                # Download
                csv = forecast.to_csv(index=False)
                st.download_button(
                    label="Download Full Forecast Data (CSV)",
                    data=csv,
                    file_name=f"forecast_{name.lower().replace(' ', '_')}.csv",
                    mime='text/csv',
                    key=f"btn_{name.replace(' ', '_')}" 
                )

    except Exception as e:
        st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()