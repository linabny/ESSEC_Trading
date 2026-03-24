# Portfolio_Forecast.py

import streamlit as st 
import yfinance as yf
import pandas as pd 
from prophet import Prophet
import plotly.graph_objects as go 
import datetime as dt
import numpy as np
from utils.optimizer_utils import calculate_efficient_frontier, get_risk_free_rate


def calculate_portfolio_price(tickers, weights, start_date, end_date):
    """Calculate historical portfolio price based on weights"""
    stock_data = yf.download(tickers, start=start_date, end=end_date)['Close']
    
    # Handle case with single ticker
    if len(tickers) == 1:
        stock_data = stock_data.to_frame()
    
    # Normalize weights to sum to 1
    weights = np.array(weights) / np.sum(weights)
    
    # Calculate portfolio value (assuming $1 initial investment)
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
        "Portfolio Forecast extends the forecasting capabilities to your entire portfolios. "
        "This feature allows you to make accurate predictions of portfolio performance based on "
        "the Prophet library. You can forecast the price of three different portfolio strategies: "
        "the original portfolio you created, a minimum volatility portfolio optimized for risk reduction, "
        "and a maximum Sharpe ratio portfolio optimized for risk-adjusted returns. "
        "Set your forecast horizon (from 30 to 365 days) to receive predictions with confidence intervals "
        "and strategic recommendations for each portfolio."
    )

    justified_description = f"""
    <div style='text-align: justify; text-justify: inter-word;'>
        {description}
    </div>
    """
    st.markdown(justified_description, unsafe_allow_html=True)

    st.write("")

    # Check if portfolio exists
    if 'portfolio' not in st.session_state or st.session_state['portfolio'].empty:
        st.info(
            "Please create a portfolio in the **Portfolio Visualizer** section "
            "before proceeding with portfolio forecasting."
        )
        return

    # Get portfolio data
    portfolio_data = st.session_state['portfolio']
    tickers = portfolio_data['Ticker'].tolist()
    weights = np.array(portfolio_data['Weight (%)'].tolist()) / 100

    # Allow user to choose the forecast period
    horizon = st.slider("Forecast Horizon (in days):", min_value=30, max_value=365, value=90)

    # Get current date
    current_date = str(dt.date.today())

    try:
        # Download historical data for portfolio optimization
        stock_data = yf.download(tickers, period='10y')['Close']
        
        if len(tickers) == 1:
            stock_data = stock_data.to_frame()
        
        returns = stock_data.pct_change().mean() * 252
        cov_matrix = stock_data.pct_change().cov() * 252
        risk_free_rate = get_risk_free_rate()

        # Calculate efficient frontier to get optimal weights
        portfolios, min_vol_pf, max_sharpe_pf, _ = calculate_efficient_frontier(
            returns=returns,
            cov_matrix=cov_matrix,
            risk_free_rate=risk_free_rate,
            portfolio_weights=weights
        )

        # Extract weights for the three portfolios
        original_weights = weights
        min_vol_weights = min_vol_pf.iloc[0:-3].values
        max_sharpe_weights = max_sharpe_pf.iloc[0:-3].values

        # Dictionary to store forecasts
        portfolios_dict = {
            "Original Portfolio": original_weights,
            "Minimum Volatility Portfolio": min_vol_weights,
            "Maximum Sharpe Portfolio": max_sharpe_weights
        }

        # Calculate historical prices for each portfolio
        hist_start_date = "2015-01-01"
        portfolio_prices = {}

        for portfolio_name, portfolio_weights in portfolios_dict.items():
            portfolio_price = calculate_portfolio_price(tickers, portfolio_weights, hist_start_date, current_date)
            portfolio_prices[portfolio_name] = portfolio_price

        # Prepare data and make forecasts for each portfolio
        forecasts = {}
        predictions_data = {}

        for portfolio_name, portfolio_price in portfolio_prices.items():
            # Prepare data for Prophet
            data = pd.DataFrame({
                'ds': portfolio_price.index,
                'y': portfolio_price.values
            })
            data['ds'] = data['ds'].dt.tz_localize(None)

            # Train Prophet model
            model = Prophet()
            model.fit(data)

            # Make forecast
            future = model.make_future_dataframe(periods=horizon)
            forecast = model.predict(future)

            forecasts[portfolio_name] = forecast
            predictions_data[portfolio_name] = {
                'historical': data,
                'forecast': forecast,
                'last_price': portfolio_price.iloc[-1]
            }

        # Create tabs for each portfolio
        tab1, tab2, tab3 = st.tabs(["Original Portfolio", "Minimum Volatility Portfolio", "Maximum Sharpe Portfolio"])

        portfolio_names = ["Original Portfolio", "Minimum Volatility Portfolio", "Maximum Sharpe Portfolio"]
        tabs = [tab1, tab2, tab3]

        for tab, portfolio_name in zip(tabs, portfolio_names):
            with tab:
                st.write(f"### {portfolio_name}")

                # Display portfolio composition
                if portfolio_name == "Original Portfolio":
                    current_weights = original_weights
                elif portfolio_name == "Minimum Volatility Portfolio":
                    current_weights = min_vol_weights
                else:
                    current_weights = max_sharpe_weights

                composition_df = pd.DataFrame({
                    'Ticker': tickers,
                    'Weight (%)': current_weights * 100
                }).sort_values(by='Weight (%)', ascending=False)

                st.write("Portfolio Composition:")
                st.dataframe(composition_df, use_container_width=True)

                # Get forecast data
                hist_data = predictions_data[portfolio_name]['historical']
                forecast_data = predictions_data[portfolio_name]['forecast']
                last_price = predictions_data[portfolio_name]['last_price']

                # Create figure
                fig = go.Figure()

                # Add historical data
                fig.add_trace(go.Scatter(
                    x=hist_data['ds'], y=hist_data['y'],
                    mode='lines',
                    name="Historical Data",
                    line=dict(color="black")
                ))

                # Add forecast
                fig.add_trace(go.Scatter(
                    x=forecast_data['ds'], y=forecast_data['yhat'],
                    mode='lines',
                    name="Predictions",
                    line=dict(color="blue")
                ))

                # Add confidence intervals
                fig.add_trace(go.Scatter(
                    x=forecast_data['ds'], y=forecast_data['yhat_upper'],
                    fill=None,
                    mode='lines',
                    line=dict(color='lightblue', dash='dot'),
                    name="Upper Interval"
                ))
                fig.add_trace(go.Scatter(
                    x=forecast_data['ds'], y=forecast_data['yhat_lower'],
                    fill='tonexty',
                    mode='lines',
                    line=dict(color='lightblue', dash='dot'),
                    name="Lower Interval"
                ))

                fig.update_layout(
                    title=f"Portfolio Price Prediction - {portfolio_name}",
                    height=600,
                    width=1000,
                    xaxis_title="Date",
                    yaxis_title="Portfolio Value ($)",
                    template="plotly_white"
                )

                st.plotly_chart(fig, use_container_width=True)

                # Get prediction metrics
                last_forecast_date = forecast_data['ds'].iloc[-1]
                last_forecast_date_str = last_forecast_date.strftime('%Y-%m-%d')

                borne_inf = forecast_data.loc[forecast_data['ds'] == last_forecast_date_str]['yhat_lower'].values[0]
                borne_sup = forecast_data.loc[forecast_data['ds'] == last_forecast_date_str]['yhat_upper'].values[0]
                prediction = forecast_data.loc[forecast_data['ds'] == last_forecast_date_str]['yhat'].values[0]

                st.write(f"### Prediction Statistics at {horizon} days")
                metrics_labels = [
                    "Current Price", "Predicted Price", "Minimum Predicted Price", "Maximum Predicted Price"
                ]
                metrics_values = [
                    f"{last_price:.2f}", f"{prediction:.2f}", f"{borne_inf:.2f}", f"{borne_sup:.2f}"
                ]

                num_metrics = len(metrics_labels)
                cols = st.columns(num_metrics)

                for col, label, value in zip(cols, metrics_labels, metrics_values):
                    with col:
                        st.metric(label, value)

                # Calculate percentage variation
                percentage_delta = ((prediction - last_price) / last_price) * 100

                # Map variation to scale 0-100
                level = max(min(50 + percentage_delta * 5, 100), 0)

                # Determine recommendation
                if 80 <= level <= 100:
                    recommendation = "Strong Buy"
                    text_color = "darkgreen"
                elif 60 <= level < 80:
                    recommendation = "Buy"
                    text_color = "green"
                elif 40 <= level < 60:
                    recommendation = "Hold"
                    text_color = "orange"
                elif 20 <= level < 40:
                    recommendation = "Sell"
                    text_color = "red"
                else:
                    recommendation = "Strong Sell"
                    text_color = "darkred"

                num_levels = 100

                # Create gauge
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge",
                    value=level,
                    title={'text': "Recommendation"},
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
                            'value': level
                        }
                    }
                ))

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

                # Download button
                csv = forecast_data.to_csv(index=False)
                st.download_button(
                    label=f"Download Forecasts as CSV",
                    data=csv,
                    file_name=f"forecasts_{portfolio_name.replace(' ', '_')}.csv",
                    mime='text/csv'
                )

    except Exception as e:
        st.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
