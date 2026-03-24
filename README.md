# ESSEC Trading

## Project Overview

**ESSEC Trading** is a comprehensive investment and portfolio management platform built with Streamlit. It combines cutting-edge financial tools with an intuitive, user-friendly interface to help both novice and expert investors maximize their potential. The platform leverages reliable data from Yahoo Finance and integrates modern financial theories with advanced simulations to transform your financial strategies into success.

A new way of investing.

---

## Installation

Before running the application, you need to install the required dependencies.

Open your terminal and run:

```bash
python -m pip install -r requirements.txt
```

This will install all necessary packages including pandas, yfinance, streamlit, numpy, plotly, and other required libraries.

---

## Running the Application

Once the dependencies are installed, launch the platform by running:

```bash
python -m streamlit run Home.py
```

The application will start on your local server, typically at `http://localhost:8501`.

---

## Project Structure

### Main Files

- **`Home.py`** - The main entry point of the application. Displays the welcome page with an introduction to ESSEC Trading and navigation to all modules.

- **`data.ipynb`** - Jupyter notebook for data analysis and exploration, containing code for loading and processing trading data.

- **`requirements.txt`** - Lists all Python dependencies needed to run the project.

### Pages (Multi-page Application)

Located in the `pages/` folder, these modules provide specific functionalities:

- **`2_Stock_Picking.py`** - Stock selection and analysis module. Helps you identify and evaluate individual stocks based on various financial metrics and criteria.

- **`3_Portfolio_Visualizer.py`** - Portfolio visualization tool. Displays and analyzes your investment portfolio with interactive charts, performance metrics, and asset allocation breakdowns.

- **`4_Portfolio_Optimizer.py`** - Portfolio optimization module. Uses advanced algorithms to optimize your portfolio allocation for maximum returns or minimal risk based on your preferences.

- **`5_Beta_Forecast.py`** - Beta forecasting module. Predicts beta coefficients and market risk metrics to help you understand portfolio volatility and systematic risk.

### Data Folder (`Data/`)

- **`data_fonctions.py`** - Utility functions for data processing, retrieval, and manipulation. Contains reusable code for loading and transforming financial data.

- **`data_trading.csv`** - Sample or reference trading data in CSV format used by the application.

- **`index.html`** - HTML template or support file for data visualization or web components.

### Utils Folder (`utils/`)

- **`graph_utils.py`** - Utility functions for creating and customizing interactive visualizations and charts using Plotly and other charting libraries.

- **`optimizer_utils.py`** - Helper functions for portfolio optimization calculations and algorithms, supporting the Portfolio Optimizer module.

### Styling

- **`style/styles.css`** - Custom CSS stylesheets that define the visual appearance and layout of the application, ensuring a modern and attractive user interface.

---

## Features

✓ **Stock Picking** - Analyze and select individual stocks  
✓ **Portfolio Visualization** - View and analyze portfolio performance  
✓ **Portfolio Optimization** - Optimize asset allocation  
✓ **Beta Forecasting** - Predict market risk metrics  

---

## Technologies Used

- **Streamlit** - Web application framework
- **pandas** - Data manipulation and analysis
- **yfinance** - Yahoo Finance data retrieval
- **Plotly** - Interactive visualizations
- **NumPy** - Numerical computations
- **Prophet** - Time series forecasting
- **Folium** - Geographic mapping

---

## License

This project was developed at ESSEC Business School.

---

Enjoy exploring the ESSEC Trading platform and enhancing your investment strategies!
