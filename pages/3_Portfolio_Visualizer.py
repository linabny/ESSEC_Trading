# Portfolio_visualizer.py

import pandas as pd
import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
import numpy as np 
from utils.graph_utils import plot_performance, plot_pie
from utils.optimizer_utils import calculate_portfolio_performance
from utils.styles_utils import apply_styles 

def get_company_name(ticker):
    try:
        company = yf.Ticker(ticker).info.get('longName', 'N/A')
    except:
        company = 'N/A'
    return company

def validate_ticker(ticker):
    """Validate if ticker exists and has data available"""
    try:
        data = yf.download(ticker, period='1d', progress=False)
        if data.empty: # type: ignore
            return False
        return True
    except:
        return False

# Initialize lists in session_state
if 'tickers' not in st.session_state:
    st.session_state.tickers = ['']
if 'weights' not in st.session_state:
    st.session_state.weights = [0.0]
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = []
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0  # Initialize current_index for the home page

# Function to add an asset
def add_asset():
    st.session_state.tickers.append('')
    st.session_state.weights.append(0.0)

# Function to remove an asset
def remove_asset(index):
    del st.session_state.tickers[index]
    del st.session_state.weights[index]
 
st.markdown("""
<link href="https://unpkg.com/aos@2.3.4/dist/aos.css" rel="stylesheet">
<script src="https://unpkg.com/aos@2.3.4/dist/aos.js"></script>
<script>
  AOS.init({
    duration: 1200,
  });
</script>
""", unsafe_allow_html=True)


df_companies = pd.read_csv("Data/data_trading.csv")

def main():
    
    # Apply centralized styles
    apply_styles()

    st.title("Portfolio visualizer")

    description = "Build and visualize your custom portfolio. Filter by benchmarks, search by name, or select from your watchlist. Simply assign weights to see real-time YTD performance, key statistics, and asset distribution. Your portfolio is automatically saved for seamless use in the Optimizer."

    justified_description = f"""
    <div style='text-align: justify; text-justify: inter-word;'>
        {description}
    </div>
    """
    st.markdown(justified_description, unsafe_allow_html=True)

    st.write("")

    st.write("Please enter the assets you want to include in your portfolio and their associated weights.")

    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = pd.DataFrame(columns=['Ticker', 'Company Name', 'Weight (%)'])

    #Index filter on the main page
    st.header("Filter by Index")
    indices = df_companies['Ind'].unique().tolist()
    selected_indices = st.multiselect(
        "Choose one or more indices",
        options=indices,
        default=indices 
    )

    if selected_indices:
        filtered_companies = df_companies[df_companies['Ind'].isin(selected_indices)]
    else:
        filtered_companies = df_companies.copy()

    if filtered_companies.empty:
        st.warning("No companies found for the selected indices.")
    
    #Callback function to define the index to delete
    def remove_asset_callback(index):
        if 0 <= index < len(st.session_state.tickers):
            remove_asset(index)

    #Function to add an asset
    def add_asset_callback():
        add_asset()

    #Button to add an asset
    st.button("➕ Add an asset", on_click=add_asset_callback)

    for i in range(len(st.session_state.tickers)):
        ticker = st.session_state.tickers[i]
        matching_rows = filtered_companies[filtered_companies["Ticker"] == ticker]
        
        # Set default selectbox position to matching company if available
        # Otherwise position on empty option (""), but keep the ticker value
        default_index = 0
        companies_list = [""] + filtered_companies["Company"].tolist()
        if not matching_rows.empty:
            company = matching_rows["Company"].iloc[0]
            if company in companies_list:
                default_index = companies_list.index(company)

        cols = st.columns([2, 2, 1])

        with cols[0]:
            selected_company = st.selectbox(
                f"Company {i+1}",
                options=companies_list,
                index=default_index,
                key=f"company_{i}"
            )
            if selected_company:
                new_ticker = filtered_companies.loc[
                    filtered_companies["Company"] == selected_company, "Ticker"
                ].values[0]
                st.session_state.tickers[i] = new_ticker

        with cols[1]:
            weight = st.number_input(
                f"Weight {i+1} (%)",
                key=f"weight_{i}",
                min_value=0.0,
                max_value=100.0,
                value=st.session_state.weights[i],
                step=0.1
            )
            st.session_state.weights[i] = weight

        with cols[2]:
            st.button("🗑️ Delete", key=f"remove_{i}", on_click=remove_asset_callback, args=(i,))

    st.write("### Add stocks from your Watchlist")
    if st.session_state.watchlist:
        watchlist_selection = st.selectbox("Select a stock from your watchlist:", st.session_state.watchlist, key="watchlist_select")

        def add_from_watchlist():
            selected_ticker = watchlist_selection.upper()
            if selected_ticker in st.session_state.tickers:
                st.warning(f"The stock **{selected_ticker}** is already in your portfolio.")
            else:
                st.session_state.tickers.append(selected_ticker)
                st.session_state.weights.append(0.0)
                st.success(f"The stock **{selected_ticker}** has been added to your portfolio. Please set its weight.")

        st.button("➕ Add from Watchlist", on_click=add_from_watchlist)
    else:
        st.info("Your watchlist is empty. Go to the **Stock Picking** section to add stocks to your watchlist.")

    #Real-time display of the sum of weights
    total_weight = sum(st.session_state.weights)
    st.markdown(f"**Current Total Weight: {total_weight:.2f}%**")
    if not np.isclose(total_weight, 100.0):
        st.warning("⚠️ The sum of weights must equal 100%.")
    else:
        st.success("✅ The sum of weights equals 100%.")

    #Portfolio validation button
    if st.button("✅ Validate Portfolio"):
        tickers = []
        weights = []
        for i in range(len(st.session_state.tickers)):
            ticker = st.session_state.tickers[i].strip().upper()
            weight = st.session_state.weights[i]  
            if ticker:
                tickers.append(ticker)
                weights.append(weight)

        st.session_state.tickers = tickers
        st.session_state.weights = weights

        duplicates = set([ticker for ticker in tickers if tickers.count(ticker) > 1])
        if duplicates:
            st.error(f"The following tickers appear multiple times in your portfolio: {', '.join(duplicates)}. Please modify their weights or change the ticker.")
            st.stop()

        #Portfolio dataframe
        df = pd.DataFrame({
            'Ticker': tickers,
            'Weight (%)': weights
        })

        total_weight = df['Weight (%)'].sum()
        if total_weight == 0:
            st.error("The sum of weights is 0%. Please enter valid weights.")
            st.stop()

        try:
            df['Weight (%)'] = df['Weight (%)'].astype(float)
        except ValueError:
            st.error("Please enter valid numerical values for the weights.")
            st.stop()

        #Verify positive weights
        if (df['Weight (%)'] <= 0).any():
            st.error("All weights must be strictly positive.")
            st.stop()
        else:
            #Verify sum to 100%
            if not np.isclose(total_weight, 100.0):
                st.warning(f"⚠️ The sum of weights is {total_weight:.2f}%. It must equal 100%.")
                normalize = st.checkbox("Do you want to normalize the weights automatically?", key="normalize_validation")
                if normalize:
                    df['Weight (%)'] = df['Weight (%)'] * 100 / total_weight
                    total_weight = df['Weight (%)'].sum()
                    st.success("The weights have been normalized.")
            #else:
                #st.success("✅ La somme des poids est égale à 100%.")

        valid_tickers = []
        invalid_tickers = []
        company_names = []

        for ticker in df['Ticker']:
            if ticker:
                try:
                    if not validate_ticker(ticker):
                        invalid_tickers.append(ticker)
                        continue
                    company_name = get_company_name(ticker)
                    if company_name != 'N/A':
                        valid_tickers.append(ticker.upper())
                        company_names.append(company_name)
                    else:
                        valid_tickers.append(ticker.upper())
                        company_names.append(ticker.upper())
                except Exception as e:
                    invalid_tickers.append(ticker)
                    st.error(f"Error verifying ticker {ticker}: {e}")

        if invalid_tickers:
            st.error(f"The following tickers are not valid or data is not available: {', '.join(invalid_tickers)}")
            st.stop()
        elif not valid_tickers:
            st.error("No valid ticker was provided.")
            st.stop()
        else:
            portfolio = {
                'Ticker': valid_tickers,
                'Company Name': company_names,
                'Weight (%)': [df.loc[df['Ticker'] == ticker, 'Weight (%)'].values[0] for ticker in valid_tickers] # type: ignore
            }
            portfolio_df = pd.DataFrame(portfolio)
            for i in range(len(portfolio_df)):
                portfolio_df.loc[i, 'Industry'] = yf.Ticker(portfolio_df.loc[i, 'Ticker']).info.get('industry', 'N/A')
            grouped_by_industry = portfolio_df.groupby('Industry')['Weight (%)'].apply(np.sum).reset_index() # type: ignore

            #Portfolio metrics
            total_weight = portfolio_df['Weight (%)'].sum()
            average_weight = portfolio_df['Weight (%)'].mean()
            max_weight = portfolio_df['Weight (%)'].max()
            min_weight = portfolio_df['Weight (%)'].min()

            #Expected annualized return
            portfolio_cumulative, portfolio_returns = calculate_portfolio_performance(
                valid_tickers,
                np.array(portfolio_df['Weight (%)'].tolist()) / 100,
                period='1y'
            )
            expected_return = portfolio_returns.mean() * 252  # 252 trading days per year

            #Annualized volatility
            volatility = portfolio_returns.std() * np.sqrt(252)

            #Sharpe Ratio (with a risk-free rate of 2%)
            risk_free_rate = 0.02
            sharpe_ratio = (expected_return - risk_free_rate) / volatility if volatility != 0 else np.nan

            st.write("### Your portfolio:")
            st.write("#### Summary Table")

            fig_table = go.Figure(data=[go.Table(
                header=dict(
                    values=list(portfolio_df.columns),
                    fill_color='#0611ab',
                    font=dict(color='white', size=14),
                    align='center',
                    height=40
                ),
                cells=dict(
                    values=[portfolio_df[col] for col in portfolio_df.columns],
                    fill_color=['#f8f9fa']*len(portfolio_df),
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
            st.plotly_chart(fig_table, use_container_width=True, key="visualizer_portfolio_table")

            #Portfolio Statistics
            st.write("### Portfolio Statistics")
            metrics_labels = [
                "Total Weight", "Average Weight", "Maximum Weight", "Minimum Weight",
                "Expected Return", "Volatility", "Sharpe Ratio"
            ]
            metrics_values = [
                f"{total_weight:.0f}%", f"{average_weight:.1f}%", f"{max_weight:.1f}%", f"{min_weight:.1f}%",
            
                f"{expected_return*100:.1f}%", f"{volatility*100:.1f}%", f"{sharpe_ratio:.2f}"
            ]
            metrics_descriptions = [
                "The sum of weights must be 100%.", "", "", "",
                "Expected annualized return.", "Annualized portfolio volatility.",
                "Sharpe Ratio (risk-adjusted return)."
            ]

            num_metrics = len(metrics_labels)
            cols = st.columns(num_metrics)

            for col, label, value, description in zip(cols, metrics_labels, metrics_values, metrics_descriptions):
                with col:
                    st.metric(label, value)
                    if description:
                        st.caption(description)

            graph_cols = st.columns(2)

            with graph_cols[0]:
                st.write("### Portfolio distribution by industry")
                grouped_sorted = grouped_by_industry.sort_values(by='Weight (%)', ascending=False)
                plot_pie(grouped_sorted, 'Industry')  #Graphics functions module

            with graph_cols[1]:
                    st.write("### Weight distribution in the portfolio")
                    portfolio_df_sorted = portfolio_df.sort_values(by='Weight (%)', ascending=False)
                    plot_pie(portfolio_df_sorted, 'Ticker')  #Graphics functions module

            st.write("### Historical portfolio performance")
            plot_performance(portfolio_cumulative)

            #We store the portfolio for the optimization section
            st.session_state['portfolio'] = portfolio_df
            st.success("✅ The portfolio has been saved for later use.")

if __name__ == "__main__":
    main()
