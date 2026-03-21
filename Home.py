import streamlit as st

#L'ENSEMBLE DU CSS ET HTML CONTENU DANS LE PROJET ONT ETE ENTIEREMENT REALISE PAR CHATGPT
#Le code Streamlit a été réalisé à l'aide de la documentation https://docs.streamlit.io/

st.set_page_config(
    page_title="π²Trading",
    page_icon="💹",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_css_file(css_file_path):
    with open(css_file_path, "r", encoding="utf-8") as f:
        css_content = f.read()
    return css_content

css_content = load_css_file("style/styles.css")

st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)

#Bibliothèque pour l'animation de "survol" des boutons
st.markdown("""
<link href="https://unpkg.com/aos@2.3.4/dist/aos.css" rel="stylesheet">
<script src="https://unpkg.com/aos@2.3.4/dist/aos.js"></script>
<script>
  AOS.init({
    duration: 1200,
  });
</script>
""", unsafe_allow_html=True)

st.markdown('''
        <h1 class="title">
            <span class="pi">π</span><span class="superscript">²</span>
            <span class="trading">Trading</span>
        </h1>
    ''', unsafe_allow_html=True)
st.markdown('<h2 class="subtitle">A new way of investing</h2>', unsafe_allow_html=True)

st.markdown('<div class="section" data-aos="fade-up">', unsafe_allow_html=True)

intro = "Bienvenue sur π² Trading, la plateforme conçue pour transformer vos stratégies financières en véritables succès.\n\nAlliant technologie de pointe et accessibilité, π² Trading met entre vos mains des outils performants et intuitifs, parfaits pour les investisseurs débutants comme pour les experts souhaitant maximiser leur potentiel. Pensée pour offrir une expérience fluide, cette plateforme dynamique, développée sur Streamlit, se distingue par son interface moderne et conviviale, rendant chaque fonctionnalité simple d'accès et agréable à utiliser.\n\nÀ travers des modules innovants comme Stock Picking, Portfolio Visualizer, Portfolio Optimizer et Beta π², elle vous propose une boîte à outils complète pour analyser, créer, simuler et optimiser vos investissements avec précision. En s'appuyant sur des données fiables issues de sources reconnues telles que finance, π² Trading garantit une information à jour et pertinente, vous aidant à prendre des décisions éclairées. Grâce à l'intégration des théories financières modernes et des simulations avancées, vous pouvez explorer de nouvelles opportunités et perfectionner vos portefeuilles dans un environnement entièrement pensé pour répondre à vos besoins.\n\nRejoignez π² Trading dès maintenant et donnez une nouvelle dimension à vos investissements.\n\nπ² Trading : a new way of investing."

justified_intro = f"""
    <div style='text-align: justify; text-justify: inter-word;'>
        {intro}
    </div>
    """
st.markdown(justified_intro, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section" data-aos="fade-up">', unsafe_allow_html=True)
st.markdown("<h2>Services</h2>", unsafe_allow_html=True)
services = [
        {"name": "Stock Picking", "description": "La solution pour construire un portefeuille sur-mesure, avec des données fiables pour des décisions éclairées.", "icon": "📈"},
        {"name": "Portfolio Visualizer", "description": "Analysez votre portefeuille avec des outils visuels clairs et des insights puissants pour maximiser vos performances.", "icon": "📊"},
        {"name": "Portfolio Optimizer", "description": "Optimisez votre portefeuille grâce à la frontière d’efficience, pour maximiser vos rendements et réduire vos risques.", "icon": "⚙️"},
        {"name": "Beta Forecast", "description": "Notre espace innovation, anticipez les prix d'actions grâce à des prévisions avancées pour optimiser vos décisions d'investissement.", "icon": "💰"}
    ]

num_services = len(services)
for i in range(0, num_services, 2):
    st.markdown('<div style="margin-bottom: 1px;">', unsafe_allow_html=True)
    cols = st.columns(2)
    for j in range(2):
        if i + j < num_services:
            service = services[i + j]
            with cols[j]:
                st.markdown(f"""
                    <div class='service-box'>
                        <div class='service-icon'>{service['icon']}</div>
                        <h3>{service['name']}</h3>
                        <p>{service['description']}</p>
                        <!-- Suppression du bouton "Choose" -->
                        <!--<button class='button'>Choose</button>-->
                    </div>
                    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)  
st.markdown('</div>', unsafe_allow_html=True)  
