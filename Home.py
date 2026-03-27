import streamlit as st

# ALL CSS AND HTML CONTENT IN THIS PROJECT WAS ENTIRELY CREATED BY CHATGPT
# Streamlit code was created with the help of https://docs.streamlit.io/ documentation

st.set_page_config(
    page_title="ESSEC Trading",
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

# Library for "hover" animation of buttons
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
            <span class="trading">ESSEC Trading</span>
        </h1>
    ''', unsafe_allow_html=True)
st.markdown('<h2 class="subtitle">A new way of investing</h2>', unsafe_allow_html=True)

st.markdown('<div class="section" data-aos="fade-up">', unsafe_allow_html=True)

intro = "Welcome to ESSEC Trading.\n\nTransform your financial strategies into success with our intuitive, high-performance platform.\nLeverage professional-grade modules—Stock Picking, Portfolio Optimizer, and Stock/Portfolio Forecast—to analyze, simulate, and refine your investments using real-time Yahoo Finance data."


justified_intro = f"""
    <div style='text-align: justify; text-justify: inter-word;'>
        {intro}
    </div>
    """
st.markdown(justified_intro, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section" data-aos="fade-up">', unsafe_allow_html=True)
st.markdown('<h2>Services</h2>', unsafe_allow_html=True)
services = [
        {"name": "Stock Picking", "description": "The solution for building a tailor-made portfolio, with reliable data for informed decisions.", "icon": "📈"},
        {"name": "Portfolio Visualizer", "description": "Analyze your portfolio with clear visual tools and powerful insights to maximize your performance.", "icon": "📊"},
        {"name": "Portfolio Optimizer", "description": "Optimize your portfolio through the efficient frontier, to maximize your returns and reduce your risks.", "icon": "⚙️"},
        {"name": "Stock Forecast", "description": "Our innovation space, anticipate stock prices with advanced forecasts to optimize your investment decisions.", "icon": "💰"},
        {"name": "Portfolio Forecast", "description": "Our innovation space, anticipate stock prices with advanced forecasts to optimize your investment decisions.", "icon": "💼"}
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
                        <!-- Removed "Choose" button -->
                        <!--<button class='button'>Choose</button>-->
                    </div>
                    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)  
st.markdown('</div>', unsafe_allow_html=True)  
