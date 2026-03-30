# Libraries for the 'Portfolio Optimizer' page

import pandas as pd
import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
import numpy as np
from utils.graph_utils import plot_performance, plot_pie
from utils.optimizer_utils import calculate_portfolio_performance, get_risk_free_rate
from utils.optimizer_utils import calculate_efficient_frontier, plot_efficient_frontier, plot_portfolio_performance
from utils.styles_utils import apply_styles

# Efficient Frontier coded using: https://youtu.be/Isutk-wqJfE?si=a2HVgMUsLGivkm0E

description_page = (
    "Analyze and refine your Visualizer portfolio using Modern Portfolio Theory. Generate the Efficient Frontier to find your ideal balance of risk and return. Automatically calculate optimal allocations to minimize volatility or maximize the Sharpe ratio, backed by 10-year historical performance charts."
)


def main():

    # Apply centralized styles
    apply_styles()

    # Header of the page
    st.title("Portfolio Optimizer")
    justified_description = f"""
    <div style='text-align: justify; text-justify: inter-word;'>
        {description_page}
    </div>
    """
    st.markdown(justified_description, unsafe_allow_html=True)

    risk_free_rate = get_risk_free_rate()
    st.write(
        f"*User Note*: by default, the data history used is set to 10 years. "
        f"The risk-free rate considered is that "
        f"of the US 10-year bond yield, obtained from the FRED API i.e. *r* = "
        f"{risk_free_rate:.3%}."
    )
    # User has entered a portfolio in the 'Portfolio Visualizer' page
    if 'portfolio' in st.session_state and not st.session_state['portfolio'].empty:

        data = st.session_state['portfolio']
        portfolio_df = data

        for i in range(len(portfolio_df)):
            portfolio_df.loc[i, 'Industry'] = yf.Ticker(portfolio_df.loc[i, 'Ticker']).info.get('industry', 'N/A')
        grouped_by_industry = portfolio_df.groupby('Industry')['Weight (%)'].apply(np.sum).reset_index()

        st.write("### Current Portfolio")

        fig_table = go.Figure(data=[go.Table(
            header=dict(
                values=list(portfolio_df.columns),
                fill_color='#0611ab',
                font=dict(color='white', size=14),
                align='center',
                height=40
            ),
            cells=dict(
                values=[portfolio_df.Ticker, portfolio_df["Company Name"], portfolio_df['Weight (%)'], portfolio_df['Industry']],
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
        st.plotly_chart(fig_table, use_container_width=True, key="optimization_portfolio_table")

        total_weight = data['Weight (%)'].sum()
        avg_weight = data['Weight (%)'].mean()
        max_weight = data['Weight (%)'].max()
        min_weight = data['Weight (%)'].min()

        # Expected return (annualized)
        tickers = data['Ticker'].tolist()
        weights = np.array(data['Weight (%)'].tolist()) / 100

        if len(tickers) > 0:
            try:
                portfolio_cumulative, portfolio_returns = calculate_portfolio_performance(
                    tickers,
                    weights,
                    period='1y'
                )
                expected_return = portfolio_returns.mean() * 252  # 252 trading days per year

                # Volatility (annualized)
                volatility = portfolio_returns.std() * np.sqrt(252)

                # Sharpe Ratio (with risk-free rate)
                if volatility != 0:
                    sharpe_ratio = (expected_return - risk_free_rate) / volatility
                else:
                    sharpe_ratio = np.nan

                st.write("### Portfolio Statistics")
                metrics_labels = [
                    "Total Weight", "Average Weight", "Maximum Weight", "Minimum Weight",
                    "Expected Return", "Volatility", "Sharpe Ratio"
                ]
                metrics_val = [
                    f"{total_weight:.0f}%", f"{avg_weight:.2f}%", f"{max_weight:.2f}%",
                    f"{min_weight:.2f}%", f"{expected_return*100:.2f}%",
                    f"{volatility*100:.2f}%", f"{sharpe_ratio:.2f}"
                ]
                metrics_des = [
                    "The sum of weights should be 100%.", "", "", "",
                    "Annualized expected return.", "Annualized portfolio volatility.",
                    "Sharpe Ratio (risk-adjusted return)."
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
                    st.write("### Portfolio Distribution by Industry")
                    grouped_sorted = grouped_by_industry.sort_values(by='Weight (%)', ascending=False)
                    plot_pie(grouped_sorted, 'Industry')  # Graphics function module

                with graph_cols[1]:
                    st.write("### Portfolio Weight Distribution")
                    portfolio_df_sorted = portfolio_df.sort_values(by='Weight (%)', ascending=False)
                    plot_pie(portfolio_df_sorted, 'Ticker')  # Graphics function module

                st.write("### Portfolio Historical Performance")
                plot_performance(portfolio_cumulative)

                st.session_state['portfolio'] = data
                # st.success("✅ The portfolio has been saved for later use.")

            except ValueError as ve:
                st.error(f"Error calculating portfolio performance: {ve}")
            except Exception as e:
                st.error(f"An error occurred during optimization: {e}")

        st.write("### Portfolio Optimization with MPT")

        data = st.session_state['portfolio']
        tickers = data['Ticker'].tolist()
        weights = np.array(data['Weight (%)'].tolist()) / 100
        stock_data = yf.download(tickers, period='10y')['Close'] # type: ignore
        returns = stock_data.pct_change().mean() * 252
        cov_matrix = stock_data.pct_change().cov() * 252 # type: ignore
        individual_volatility = np.sqrt(np.diag(cov_matrix))

        # Simulate portfolios
        portfolios, min_vol_pf, max_sharpe_pf, current_portfolio_metrics = calculate_efficient_frontier(
            returns=returns,
            cov_matrix=cov_matrix,
            risk_free_rate=risk_free_rate,
            portfolio_weights=weights
        )

        # Call the plot_efficient_frontier function to create the chart
        fig = plot_efficient_frontier(
            portfolios=portfolios,
            min_volatility_portfolio=min_vol_pf,
            max_sharpe_portfolio=max_sharpe_pf,
            current_portfolio_metrics=current_portfolio_metrics,
            individual_volatility=individual_volatility,
            individual_returns=returns,
            asset_names=tickers
        )

        # Display the chart
        st.plotly_chart(fig)

        # Add details of optimal portfolios
        sep = st.columns(2)

        # Skip line 0, keep weights
        weights_min_volatility = min_vol_pf.iloc[0:-3].values
        weights_max_sharpe = max_sharpe_pf.iloc[0:-3].values

        # Prepare data for pie chart
        min_volatility_portfolio_df = pd.DataFrame({
            # Associates tickers with weights
            'Ticker': tickers[:len(weights_min_volatility)],
            # Converts weights to percentages
            'Weight (%)': weights_min_volatility * 100
        }).sort_values(by='Weight (%)', ascending=False)
        max_sharpe_portfolio_df = pd.DataFrame({
            'Ticker': tickers[:len(weights_max_sharpe)],
            'Weight (%)': weights_max_sharpe * 100
        }).sort_values(by='Weight (%)', ascending=False)

        with sep[0]:
            st.write("### Minimum Volatility Portfolio")
            plot_pie(min_volatility_portfolio_df, 'Ticker')

        with sep[1]:
            st.write("### Maximum Sharpe Ratio Portfolio")
            plot_pie(max_sharpe_portfolio_df, 'Ticker')

        st.write("### 10-Year Portfolio Performance Comparison")
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
            "Please create a portfolio in the **Portfolio Visualizer** section "
            "before proceeding with optimization."
        )


if __name__ == "__main__":
    main()
