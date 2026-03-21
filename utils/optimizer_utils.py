# Utils for 'Portfolio Optimizer' page

import pandas as pd
import yfinance as yf
import plotly.graph_objs as go
import requests
import numpy as np


def calculate_portfolio_performance(tickers, weights, period='1y'):
    """
    Calculates the performance of a portfolio over a given period.

    :param tickers: List of ticker symbols for assets.
    :param weights: Weights of the assets in the portfolio.
    :param period: Period for downloading data (default '1y').
    :return: Tuple (cumulative portfolio returns, daily portfolio returns).
    """
    # Download adjusted closing prices for tickers
    data = yf.download(tickers, period=period)['Close']

    # Handle the case where only one ticker is provided (data becomes a Series instead of DataFrame)
    if isinstance(data, pd.Series):
        data = data.to_frame()

    # Calculate daily returns
    returns = data.pct_change().dropna()

    # Calculate weighted portfolio returns
    weighted_returns = returns.multiply(weights, axis=1)
    # Sum of weighted returns for each day
    portfolio_returns = weighted_returns.sum(axis=1)

    # Calculate cumulative portfolio returns
    portfolio_cumulative = (1 + portfolio_returns).cumprod()

    return portfolio_cumulative, portfolio_returns


def get_risk_free_rate(api_key="f1f1a2d3abcf1f08e76d3bc4fc1efd19"):
    """
    Retrieves the risk-free rate (10-year bond yield) from the FRED API.

    If an error occurs, returns a default rate of 2%.

    :param api_key: API key for accessing the FRED API.
    :return: Risk-free rate as a float (e.g., 0.02 for 2%).
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
        response.raise_for_status()  # Check for HTTP errors
        data = response.json()
        # Return the first available rate, converted to decimal
        return float(data['observations'][0]['value']) / 100
    except Exception:
        # Return a default rate of 2% on error
        return 0.02


def calculate_portfolio_metrics(weights, returns, cov_matrix, risk_free_rate):
    """
    Calculates portfolio metrics: expected return, volatility, and Sharpe ratio.

    :param weights: List or array of asset weights in the portfolio.
    :param returns: List or array of expected asset returns.
    :param cov_matrix: Covariance matrix of assets.
    :param risk_free_rate: Risk-free rate (float).
    :return: Tuple (expected return, volatility, Sharpe ratio).
    """
    weights = np.array(weights)  # Convert to NumPy array
    portfolio_return = np.dot(returns, weights)  # Expected portfolio return

    # Calculate variance and volatility
    portfolio_variance = np.dot(weights, np.dot(cov_matrix, weights))
    portfolio_volatility = np.sqrt(portfolio_variance)

    # Calculate Sharpe ratio
    if portfolio_volatility:
        sharpe_ratio = (portfolio_return - risk_free_rate) / portfolio_volatility
    else:
        0

    return portfolio_return, portfolio_volatility, sharpe_ratio


def simulate_portfolios(returns, cov_matrix, risk_free_rate, num_portfolios=10000):
    """
    Generates random portfolios to simulate the efficient frontier.

    :param returns: List or array of expected asset returns.
    :param cov_matrix: Covariance matrix of assets.
    :param risk_free_rate: Risk-free rate (float).
    :param num_portfolios: Number of portfolios to simulate (int).
    :return: NumPy array containing weights, returns, volatilities, and Sharpe ratios for each portfolio.
    """
    num_assets = len(returns)
    results = np.zeros((num_portfolios, num_assets + 3))  # Columns: weights + metrics

    for i in range(num_portfolios):
        weights = np.random.random(num_assets)     # Generate random weights
        weights /= weights.sum()                   # Normalize to 1

        # Calculate metrics for the portfolio
        portfolio_return, portfolio_volatility, sharpe_ratio = calculate_portfolio_metrics(
            weights, returns, cov_matrix, risk_free_rate
        )

        # Store results
        results[i, :num_assets] = weights
        results[i, num_assets:] = portfolio_return, portfolio_volatility, sharpe_ratio

    return results


def calculate_efficient_frontier(returns, cov_matrix, risk_free_rate, portfolio_weights):
    """
    Performs calculations for the efficient frontier.

    :param returns: Average returns of assets.
    :param cov_matrix: Covariance matrix of assets.
    :param risk_free_rate: Risk-free rate.
    :param portfolio_weights: Portfolio weights.
    :return: A tuple containing the DataFrame of simulated portfolios,
             the minimum volatility portfolio, and the maximum Sharpe portfolio.
    """
    # Simulate portfolios
    num_assets = len(returns)
    num_portfolios = 10000
    results = np.zeros((num_portfolios, num_assets + 3))  # Columns: weights + metrics

    for i in range(num_portfolios):
        weights = np.random.random(num_assets)
        weights /= weights.sum()  # Normalize to 1
        portfolio_return, portfolio_volatility, sharpe_ratio = calculate_portfolio_metrics(
            weights, returns, cov_matrix, risk_free_rate
        )
        results[i, :num_assets] = weights
        results[i, num_assets:] = portfolio_return, portfolio_volatility, sharpe_ratio

    # Convert to DataFrame
    columns = (
        [f'Weight {i+1}' for i in range(num_assets)]
        + ['Return', 'Volatility', 'Sharpe Ratio']
    )
    portfolios = pd.DataFrame(results, columns=columns)

    # Find optimal portfolios
    min_volatility_idx = portfolios['Volatility'].idxmin()
    max_sharpe_idx = portfolios['Sharpe Ratio'].idxmax()

    min_volatility_portfolio = portfolios.iloc[min_volatility_idx]
    max_sharpe_portfolio = portfolios.iloc[max_sharpe_idx]

    # Calculate current portfolio metrics
    portfolio_return, portfolio_volatility, sharpe_ratio = calculate_portfolio_metrics(
        portfolio_weights, returns, cov_matrix, risk_free_rate
    )
    current_portfolio_metrics = {
        "Return": portfolio_return * 100,
        "Volatility": portfolio_volatility * 100,
        "Sharpe Ratio": sharpe_ratio
    }

    return portfolios, min_volatility_portfolio, max_sharpe_portfolio, current_portfolio_metrics


# Efficient frontier improved with help from ChatGPT
def plot_efficient_frontier(portfolios, min_volatility_portfolio, max_sharpe_portfolio, current_portfolio_metrics,
            individual_volatility, individual_returns, asset_names):
    """
    Plots the efficient frontier with simulated portfolios.

    :param portfolios: DataFrame of simulated portfolios.
    :param min_volatility_portfolio: Minimum volatility portfolio.
    :param max_sharpe_portfolio: Portfolio with maximum Sharpe ratio.
    :param current_portfolio_metrics: Dictionary containing current portfolio metrics.
    :param individual_volatility: Individual asset volatility.
    :param individual_returns: Individual asset returns.
    :param asset_names: List of asset names.
    :return: Plotly Figure object.
    """
    fig = go.Figure()

    # Plot simulated portfolios
    fig.add_trace(go.Scatter(
        x=portfolios['Volatility'] * 100,
        y=portfolios['Return'] * 100,
        mode='markers',
        marker=dict(
            size=5,
            color=portfolios['Sharpe Ratio'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title='Sharpe Ratio')
        ),
        text=portfolios['Sharpe Ratio'],
        name='Simulated Portfolios'
    ))

    # Add current portfolio
    fig.add_trace(go.Scatter(
        x=[current_portfolio_metrics["Volatility"]],
        y=[current_portfolio_metrics["Return"]],
        mode='markers+text',
        marker=dict(color='black', size=12, symbol='hexagram'),
        text=['Current Portfolio'],
        textposition="top center",
        name='Current Portfolio'
    ))

    # Add individual assets
    fig.add_trace(go.Scatter(
        x=individual_volatility * 100,
        y=individual_returns * 100,
        mode='markers+text',
        marker=dict(color='blue', size=8),
        text=asset_names,
        textposition="top center",
        name='Assets'
    ))

    # Add minimum volatility portfolio
    fig.add_trace(go.Scatter(
        x=[min_volatility_portfolio['Volatility'] * 100],
        y=[min_volatility_portfolio['Return'] * 100],
        mode='markers+text',
        marker=dict(color='magenta', size=12, symbol='star-diamond'),
        text=['Min Vol'],
        textposition="top center",
        name='Minimum Volatility Portfolio'
    ))

    # Add maximum Sharpe portfolio
    fig.add_trace(go.Scatter(
        x=[max_sharpe_portfolio['Volatility'] * 100],
        y=[max_sharpe_portfolio['Return'] * 100],
        mode='markers+text',
        marker=dict(color='red', size=12, symbol='star-diamond'),
        text=['Max Sharpe'],
        textposition="top center",
        name='Maximum Sharpe Portfolio'
    ))

    # Update layout
    fig.update_layout(
        title='Efficient frontier with portfolios and assets',
        xaxis_title='Volatility (%)',
        yaxis_title='Expected Return (%)',
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
    Plots the cumulative performance of portfolios over a given period.

    :param tickers: List of ticker symbols for portfolio assets.
    :param weights: Weights of the original portfolio.
    :param min_vol_weights: Weights of the minimum volatility portfolio.
    :param max_sharpe_weights: Weights of the maximum Sharpe portfolio.
    :param period: Period for calculations (default '10y').
    :return: Plotly Figure object.
    """
    # Calculate cumulative performance
    # Original portfolio
    original_cumulative, _ = calculate_portfolio_performance(tickers, weights, period=period)

    # Minimum volatility portfolio
    min_vol_cumulative, _ = calculate_portfolio_performance(tickers, min_vol_weights, period=period)

    # Maximum Sharpe portfolio
    max_sharpe_cumulative, _ = calculate_portfolio_performance(tickers, max_sharpe_weights, period=period)

    # Plot cumulative performance
    fig = go.Figure()

    # Original portfolio performance
    fig.add_trace(go.Scatter(
        x=original_cumulative.index,
        y=original_cumulative.values,
        mode='lines',  # Lines without markers
        name='Original Portfolio',
        line=dict(color='#0611ab', width=3)
    ))

    # Minimum volatility portfolio performance
    fig.add_trace(go.Scatter(
        x=min_vol_cumulative.index,
        y=min_vol_cumulative.values,
        mode='lines',  # Lines without markers
        name='Minimum Volatility Portfolio',
        line=dict(color='green', width=3)
    ))

    # Maximum Sharpe portfolio performance
    fig.add_trace(go.Scatter(
        x=max_sharpe_cumulative.index,
        y=max_sharpe_cumulative.values,
        mode='lines',  # Lines without markers
        name='Maximum Sharpe Portfolio',
        line=dict(color='gold', width=3)
    ))

    # Update chart layout
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Cumulative Value',
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
