import pandas as pd
import folium


def obtenir_liste_entreprises(url, nom_indice):
    """
    Récupère la liste des entreprises d'un indice boursier spécifié depuis Wikipedia.

    Paramètres :
    - url (str) : URL de la page Wikipedia contenant la liste des entreprises de l'indice boursier.
    - nom_indice (str) : Nom de l'indice boursier.

    Retour :
    - DataFrame contenant la liste des entreprises pour l'indice boursier spécifié.
    """
    # Dictionnaire pour mapper les noms des indices aux indices de leurs tables sur Wikipedia
    index_table_map = {
        'CAC 40': 4,      # 5è tableau pour le CAC 40
        'S&P 500': 0,     # 1er tableau pour le S&P 500
        'DAX': 4,         # 5è tableau pour le DAX
        'FTSE MIB': 1,    # 2è tableau pour le FTSE MIB
        'FTSE 100': 4,    # 4è tableau pour le FTSE 100
        'IBEX 35': 2      # 2è tableau pour le IBEX 35
    }

    if nom_indice in index_table_map:
        try:
            df = pd.read_html(url)[index_table_map[nom_indice]]
            return df
        except Exception as e:
            raise Exception(f"Une erreur s'est produite lors de la récupération des données depuis {url} : {e}")
    else:
        raise ValueError(f"Le nom de l'indice '{nom_indice}' n'est pas reconnu. Veuillez utiliser l'un des suivants : {list(index_table_map.keys()) + ['Russell 2000']}")


def nettoyage_snp500(df_snp500):
    """
    Récupère les données d'un indice boursier et les nettoie.

    Paramètres :
    - df_snp500 (DataFrame) : DataFrame contenant les données de l'indice boursier.

    Retour :
    - DataFrame contenant les données de l'indice boursier nettoyées.
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


def nettoyage_cac40(df_cac40):
    """
    Récupère les données d'un indice boursier et les nettoie.

    Paramètres :
    - df_cac40 (DataFrame) : DataFrame contenant les données de l'indice boursier.

    Retour :
    - DataFrame contenant les données de l'indice boursier nettoyées.
    """
    df_cac40 = df_cac40.drop(columns=[
        'Sector', 'GICS Sub-Industry',
        ])
    cols = df_cac40.columns.tolist()        # Récupère la liste des noms de colonnes
    cols = [cols[1]] + cols[:1] + cols[2:]  # Réarrange les colonnes
    df_cac40 = df_cac40[cols]               # Réapplique l'ordre des colonnes au DataFrame
    df_cac40['Ind'] = 'CAC 40'

    return df_cac40


def nettoyage_dax(df_dax):
    """
    Récupère les données d'un indice boursier et les nettoie.

    Paramètres :
    - df_dax (DataFrame) : DataFrame contenant les données de l'indice boursier.

    Retour :
    - DataFrame contenant les données de l'indice boursier nettoyées.
    """
    df_dax = df_dax.drop(columns=[
        'Logo', 'Prime Standard Sector', 'Index weighting (%)1', 'Employees', 'Founded'
        ])
    cols = df_dax.columns.tolist()
    cols = [cols[1]] + cols[:1]
    df_dax = df_dax[cols]
    df_dax['Ind'] = 'DAX'

    return df_dax


def nettoyage_ftsemib(df_ftsemib):
    """
    Récupère les données d'un indice boursier et les nettoie.

    Paramètres :
    - df_ftsemib (DataFrame) : DataFrame contenant les données de l'indice boursier.

    Retour :
    - DataFrame contenant les données de l'indice boursier nettoyées.
    """
    df_ftsemib = df_ftsemib.drop(columns=[
        'ISIN', 'ICB Sector'
        ])
    cols = df_ftsemib.columns.tolist()
    cols = [cols[1]] + cols[:1]
    df_ftsemib = df_ftsemib[cols]
    df_ftsemib['Ind'] = 'FTSE MIB'

    return df_ftsemib


def nettoyage_ftse100(df_ftse100):
    """
    Récupère les données d'un indice boursier et les nettoie.

    Paramètres :
    - df_ftse100 (DataFrame) : DataFrame contenant les données de l'indice boursier.

    Retour :
    - DataFrame contenant les données de l'indice boursier nettoyées.
    """
    df_ftse100 = df_ftse100.drop(columns=[
        'FTSE industry classification benchmark sector[24]'
        ])
    df_ftse100['Ticker'] = df_ftse100['Ticker'] + '.L'
    cols = df_ftse100.columns.tolist()
    cols = [cols[1]] + cols[:1]
    df_ftse100 = df_ftse100[cols]
    df_ftse100['Ind'] = 'FTSE 100'

    return df_ftse100


def nettoyage_ibex35(df_ibex35):
    """
    Récupère les données d'un indice boursier et les nettoie.

    Paramètres :
    - df_ibex35 (DataFrame) : DataFrame contenant les données de l'indice boursier.

    Retour :
    - DataFrame contenant les données de l'indice boursier nettoyées.
    """
    df_ibex35 = df_ibex35.drop(columns=[
        'Sector'
        ])
    df_ibex35['Ind'] = 'IBEX 35'

    return df_ibex35


def map_index(df):
    """
    Associe des indices boursiers à leurs pays, calcule la répartition des entreprises par pays,
    et génère une carte interactive avec les données visualisées.

    Arguments:
    - df (pandas.DataFrame): DataFrame contenant les indices.

    Retourne:
    - folium.Map: Carte interactive avec les marqueurs des entreprises par pays.
    """
    # Définir le dictionnaire des indices aux pays
    index_to_country = {
        'S&P 500': 'United States',
        'CAC 40': 'France',
        'DAX': 'Germany',
        'FTSE MIB': 'Italy',
        'FTSE 100': 'United Kingdom',
        'IBEX 35': 'Spain'
    }

    # Définir les coordonnées pour les capitales de ces pays
    country_coordinates = {
        'United States': (38.9072, -77.0369),  # Washington, D.C.
        'France': (48.8566, 2.3522),           # Paris
        'Germany': (52.5200, 13.4050),         # Berlin
        'Italy': (41.9028, 12.4964),           # Rome
        'United Kingdom': (51.5074, -0.1278),  # Londres
        'Spain': (40.4168, -3.7038)            # Madrid
    }

    # Ajouter une colonne 'Country' basée sur l'indice
    df['Country'] = [index_to_country[ind] for ind in df['Ind']]

    # Compter le nombre d'entreprises par pays
    country_counts = df['Country'].value_counts().reset_index()
    country_counts.columns = ['Country', 'Count']

    # Créer une carte (GPT)
    map = folium.Map(location=[48.8566, 2.3522], zoom_start=3)

    # Ajouter des données par pays (GPT)
    for _, row in country_counts.iterrows():
        country = row['Country']
        count = row['Count']
        if country in country_coordinates:
            folium.CircleMarker(
                location=country_coordinates[country],
                radius=10,
                popup=f"{country}: {count} entreprises",
                color='blue',
                fill=True,
                fill_color='blue'
            ).add_to(map)

    # Afficher la carte
    map.save('index.html')

    return map
