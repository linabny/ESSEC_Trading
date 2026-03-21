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

intro = "Welcome to ESSEC Trading, the platform designed to transform your financial strategies into true success.\n\nCombining cutting-edge technology with accessibility, ESSEC Trading puts powerful and intuitive tools in your hands, perfect for both novice and expert investors looking to maximize their potential. Designed to provide a smooth experience, this dynamic platform, developed with Streamlit, stands out with its modern and user-friendly interface, making each feature simple to access and pleasant to use.\n\nThrough innovative modules such as Stock Picking, Portfolio Visualizer, Portfolio Optimizer, and Beta Forecast, it offers you a complete toolkit to analyze, create, simulate, and optimize your investments with precision. Drawing on reliable data from recognized sources such as Yahoo Finance, ESSEC Trading guarantees up-to-date and relevant information, helping you make informed decisions. Through the integration of modern financial theories and advanced simulations, you can explore new opportunities and refine your portfolios in an environment entirely designed to meet your needs.\n\nJoin ESSEC Trading now and give a new dimension to your investments.\n\nESSEC Trading: a new way of investing."

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
        {"name": "Beta Forecast", "description": "Our innovation space, anticipate stock prices with advanced forecasts to optimize your investment decisions.", "icon": "💰"}
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
