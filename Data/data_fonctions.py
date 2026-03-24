import pandas as pd
import folium
import urllib.request


def get_company_list(url, index_name):
    """
    Retrieves the list of companies from a specified stock index from Wikipedia.

    Parameters:
    - url (str): URL of the Wikipedia page containing the list of companies in the stock index.
    - index_name (str): Name of the stock index.

    Returns:
    - DataFrame containing the list of companies for the specified stock index.
    """
    # Dictionary to map index names to their table indices on Wikipedia
    index_table_map = {
        'CAC 40': 4,      # 5th table for CAC 40
        'S&P 500': 0,     # 1st table for S&P 500
        'DAX': 4,         # 5th table for DAX
        'FTSE MIB': 1,    # 2nd table for FTSE MIB
        'FTSE 100': 6,    # 7th table for FTSE 100
        'IBEX 35': 2      # 2nd table for IBEX 35
    }

    if index_name in index_table_map:
        try:
            # Add User-Agent header to avoid HTTP 403 Forbidden from Wikipedia
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as response:
                df = pd.read_html(response)[index_table_map[index_name]]
            return df
        except Exception as e:
            raise Exception(f"An error occurred while retrieving data from {url}: {e}")
    else:
        raise ValueError(f"The index name '{index_name}' is not recognized. Please use one of the following: {list(index_table_map.keys()) + ['Russell 2000']}")


def clean_snp500(df_snp500):
    """
    Retrieves and cleans data from a stock index.

    Parameters:
    - df_snp500 (DataFrame): DataFrame containing the stock index data.

    Returns:
    - DataFrame containing the cleaned stock index data.
    """
    df_snp500 = df_snp500.drop(columns=[
        'GICS Sector', 'GICS Sub-Industry', 'Headquarters Location', 'Date added', 'CIK', 'Founded'
        ])
    df_snp500.rename(columns={'Symbol': 'Ticker', 'Security': 'Company'}, inplace=True)
    df_snp500 = df_snp500.dropna(subset=['Company'])
    df_snp500.loc[60, 'Ticker'] = 'BRK-B'
    df_snp500.loc[75, 'Ticker'] = 'BF-B'
    df_snp500['Ind'] = 'S&P 500'

    return df_snp500


def clean_cac40(df_cac40):
    """
    Retrieves and cleans data from a stock index.

    Parameters:
    - df_cac40 (DataFrame): DataFrame containing the stock index data.

    Returns:
    - DataFrame containing the cleaned stock index data.
    """
    df_cac40 = df_cac40.drop(columns=[
        'Sector', 'GICS Sub-Industry',
        ])
    cols = df_cac40.columns.tolist()        # Get the list of column names
    cols = [cols[1]] + cols[:1] + cols[2:]  # Reorder the columns
    df_cac40 = df_cac40[cols]               # Reapply the column order to the DataFrame
    df_cac40['Ind'] = 'CAC 40'

    return df_cac40


def clean_dax(df_dax):
    """
    Retrieves and cleans data from a stock index.

    Parameters:
    - df_dax (DataFrame): DataFrame containing the stock index data.

    Returns:
    - DataFrame containing the cleaned stock index data.
    """
    df_dax = df_dax.drop(columns=[
        'Logo', 'Prime Standard Sector', 'Index weighting (%)1', 'Employees', 'Founded'
        ])
    cols = df_dax.columns.tolist()
    cols = [cols[1]] + cols[:1]
    df_dax = df_dax[cols]
    df_dax['Ind'] = 'DAX'

    return df_dax


def clean_ftsemib(df_ftsemib):
    """
    Retrieves and cleans data from a stock index.

    Parameters:
    - df_ftsemib (DataFrame): DataFrame containing the stock index data.

    Returns:
    - DataFrame containing the cleaned stock index data.
    """
    df_ftsemib = df_ftsemib.drop(columns=[
        'ISIN', 'ICB Sector'
        ])
    cols = df_ftsemib.columns.tolist()
    cols = [cols[1]] + cols[:1]
    df_ftsemib = df_ftsemib[cols]
    df_ftsemib['Ind'] = 'FTSE MIB'

    return df_ftsemib


def clean_ftse100(df_ftse100):
    """
    Retrieves and cleans data from a stock index.

    Parameters:
    - df_ftse100 (DataFrame): DataFrame containing the stock index data.

    Returns:
    - DataFrame containing the cleaned stock index data.
    """
    df_ftse100 = df_ftse100.drop(columns=[
        'FTSE industry classification benchmark sector[38]'
        ])
    df_ftse100['Ticker'] = df_ftse100['Ticker'] + '.L'
    cols = df_ftse100.columns.tolist()
    cols = [cols[1]] + cols[:1]
    df_ftse100 = df_ftse100[cols]
    df_ftse100['Ind'] = 'FTSE 100'

    return df_ftse100


def clean_ibex35(df_ibex35):
    """
    Retrieves and cleans data from a stock index.

    Parameters:
    - df_ibex35 (DataFrame): DataFrame containing the stock index data.

    Returns:
    - DataFrame containing the cleaned stock index data.
    """
    df_ibex35 = df_ibex35.drop(columns=[
        'Sector'
        ])
    df_ibex35['Ind'] = 'IBEX 35'

    return df_ibex35


def map_index(df):
    """
    Associates stock indices with their countries, calculates the distribution of companies by country,
    and generates an interactive map with the visualized data.

    Arguments:
    - df (pandas.DataFrame): DataFrame containing the indices.

    Returns:
    - folium.Map: Interactive map with markers for companies by country.
    """
    # Define the dictionary of indices to countries
    index_to_country = {
        'S&P 500': 'United States',
        'CAC 40': 'France',
        'DAX': 'Germany',
        'FTSE MIB': 'Italy',
        'FTSE 100': 'United Kingdom',
        'IBEX 35': 'Spain'
    }

    # Define coordinates for the capitals of these countries
    country_coordinates = {
        'United States': (38.9072, -77.0369),  # Washington, D.C.
        'France': (48.8566, 2.3522),           # Paris
        'Germany': (52.5200, 13.4050),         # Berlin
        'Italy': (41.9028, 12.4964),           # Rome
        'United Kingdom': (51.5074, -0.1278),  # London
        'Spain': (40.4168, -3.7038)            # Madrid
    }

    # Add a 'Country' column based on the index
    df['Country'] = [index_to_country[ind] for ind in df['Ind']]

    # Count the number of companies per country
    country_counts = df['Country'].value_counts().reset_index()
    country_counts.columns = ['Country', 'Count']

    # Create a map
    map = folium.Map(location=[48.8566, 2.3522], zoom_start=3)

    # Add data by country 
    for _, row in country_counts.iterrows():
        country = row['Country']
        count = row['Count']
        if country in country_coordinates:
            folium.CircleMarker(
                location=country_coordinates[country],
                radius=10,
                popup=f"{country}: {count} companies",
                color='blue',
                fill=True,
                fill_color='blue'
            ).add_to(map)

    # Save the map
    map.save('index.html')

    return map
