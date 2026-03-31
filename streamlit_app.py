import streamlit as st
from core.database import init_db
from app.views import dashboard, clientes, importador, pipeline, configuracion

st.set_page_config(page_title="WOM CRM Pro", layout="wide", page_icon="🚀")

# Inicializar DB
init_db()

# Sidebar Profesional
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/b/be/WOM_Logo.png", width=100)
st.sidebar.title("CRM Engine v1.0")
page = st.sidebar.selectbox("Menú Principal", 
    ["📊 Dashboard", "👥 Contactos", "📈 Pipeline", "📥 Importar", "⚙️ Configuración"])

if page == "📊 Dashboard": dashboard.show()
elif page == "👥 Contactos": clientes.show()
elif page == "📈 Pipeline": pipeline.show()
elif page == "📥 Importar": importador.show()
elif page == "⚙️ Configuración": configuracion.show()
