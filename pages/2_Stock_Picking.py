# pages/2_Stock_Picking.py

import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objs as go

def main():
    if 'watchlist' not in st.session_state:
        st.session_state.watchlist = []
    
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

    df = pd.read_csv("Data/data_trading.csv")
    
    st.title("Stock Picking")
    description = "Build your portfolio with high-quality data from Yahoo Finance. Search by name or benchmark to access deep-dive company profiles, including historical price charts, key financial ratios, and economic health indicators. Add top picks to your Watchlist for seamless tracking and future analysis."

    justified_description = f"""
    <div style='text-align: justify; text-justify: inter-word;'>
        {description}
    </div>
    """
    st.markdown(justified_description, unsafe_allow_html=True)

    st.write("")


    # Index filter on main page
    st.header("Filter by Index")
    indices = df['Ind'].unique().tolist()
    selected_indices = st.multiselect(
        "Choose one or more indices",
        options=indices,
        default=indices 
    )##

    if selected_indices:
        filtered_companies = df[df['Ind'].isin(selected_indices)]
    else:
        filtered_companies = df.copy()

    if filtered_companies.empty:
        st.warning("No companies found for the selected indices.")

    # Company selection
    companies = filtered_companies["Company"].tolist()
    selected_company = st.selectbox("Choose a company:", companies)

    # Display the associated ticker
    ticker = filtered_companies[filtered_companies["Company"] == selected_company]["Ticker"].values[0]
    
    period_options = ['1 month', '3 months', '6 months', '1 year', '2 years', '5 years', 'Max']
    period_mapping = {
            '1 month': '1mo',
            '3 months': '3mo',
            '6 months': '6mo',
            '1 year': '1y',
            '2 years': '2y',
            '5 years': '5y',
            'Max': 'max'
        }
    period_choice = st.selectbox("Select the period:", period_options, index=3)
    period = period_mapping[period_choice]
    
    if ticker and ticker != "Ticker not found":
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(period=period)
    
            info = stock.info
    
            if not data.empty:
                # Stock information
                st.subheader(f"Information about {ticker.upper()}")
    
                col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                with col1:
                    st.metric("Company", info.get('longName', 'N/A'))
                    st.metric("Sector", info.get('sector', 'N/A'))
                with col2:
                    st.metric("Industry", info.get('industry', 'N/A'))
                    market_cap = info.get('marketCap', None)

                    if market_cap:
                        if market_cap >= 1e12:
                            market_cap_formatted = f"{market_cap / 1e12:.2f} T"
                        elif market_cap >= 1e9:
                            market_cap_formatted = f"{market_cap / 1e9:.2f} B"
                        elif market_cap >= 1e6:
                            market_cap_formatted = f"{market_cap / 1e6:.2f} M"
                        else:
                            market_cap_formatted = f"${market_cap:,}"
                        st.metric("Market Capitalization", f"${market_cap_formatted}")
                    else:
                        st.metric("Market Capitalization", 'N/A')
                with col3:
                    trailing_pe = info.get('trailingPE', 'N/A')
                    st.metric("P/E Ratio", f"{trailing_pe}" if trailing_pe != 'N/A' else 'N/A')
                    dividend_yield = info.get('dividendYield', None)
                    if dividend_yield is not None:
                        st.metric("Dividend Yield", f"{dividend_yield * 100:.2f}%")
                    else:
                        st.metric("Dividend Yield", 'N/A')
                with col4:

                    # Watchlist button
                    if ticker.upper() in st.session_state.watchlist:
                        watchlist_label = "★"  
                        watchlist_action = "remove"
                        tooltip = "Remove from Watchlist"
                    else:
                        watchlist_label = "☆"  
                        watchlist_action = "add"
                        tooltip = "Add to Watchlist"
    
                    if st.button(watchlist_label, key=f"watchlist_{ticker.upper()}"):
                        if ticker.upper() in st.session_state.watchlist:
                            st.session_state.watchlist.remove(ticker.upper())
                            st.success(f"{ticker.upper()} has been removed from your watchlist.")
                        else:
                            st.session_state.watchlist.append(ticker.upper())
                            st.success(f"{ticker.upper()} has been added to your watchlist.")
    
                # Company summary
                st.markdown("### Company Summary")
                summary = info.get('longBusinessSummary', 'No summary available.')
                justified_summary = f"""
                <div style='text-align: justify; text-justify: inter-word;'>
                    {summary}
                </div>
                """
                st.markdown(justified_summary, unsafe_allow_html=True)
    
                fig = go.Figure(data=[go.Candlestick(
                    x=data.index,
                    open=data['Open'],
                    high=data['High'],
                    low=data['Low'],
                    close=data['Close'],
                    increasing_line_color='#2e7d32',  # Dark green
                    decreasing_line_color='#c62828'   # Dark red
                )])
    
                fig.update_layout(
                    title=f"Stock price for {ticker.upper()} over {period_choice}",
                    xaxis_title='Date',
                    yaxis_title='Prix',
                    width=800,   
                    height=700,
                    xaxis_rangeslider_visible=True,
                    template='plotly_white',
                    bargap=0
                )

                st.plotly_chart(fig, use_container_width=True)
    
                st.subheader("Financial Ratios")
    
                # Ratios and their descriptions
                ratios = {
                    "P/E Ratio": {
                        "value": info.get('trailingPE', 'N/A'),
                        "description": "Price to Earnings Ratio. Indicates how much investors are willing to pay relative to current earnings."
                    },
                    "ROE": {
                        "value": f"{info.get('returnOnEquity', 'N/A')*100:.2f}%" if info.get('returnOnEquity') else 'N/A',
                        "description": "Return on Equity. Measures profitability relative to shareholder equity."
                    },
                    "PEG Ratio": {
                        "value": info.get('pegRatio', 'N/A'),
                        "description": "Price/Earnings to Growth Ratio. Evaluates P/E ratio based on earnings growth."
                    },
                    "Debt/Equity": {
                        "value": info.get('debtToEquity', 'N/A'),
                        "description": "Debt to Equity Ratio. Compares total debt to shareholder equity."
                    }
                }
    
                # Use st.columns to align metrics
                ratio_cols = st.columns(len(ratios))
                for col, (ratio, details) in zip(ratio_cols, ratios.items()):
                    with col:
                        st.metric(label=ratio, value=details["value"])
                        st.caption(details["description"])
    
                # RECENT NEWS - CHECK IF WE WANT TO INCLUDE OR NOT
                # st.markdown("### Recent News")
                # news = stock.news
                # if news:
                #     for article in news[:5]:  # Display the latest 5 news
                #         title = article.get('title', 'No Title')
                #         link = article.get('link', '#')
                #         summary = article.get('summary', 'No summary available.')
                #         st.markdown(f"**[{title}]({link})**")
                #         st.write(summary)
                #         st.write("---")
                # else:
                #     st.write("No news available for this stock.")
    
            else:
                st.error("Data for this ticker is not available.")
        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
