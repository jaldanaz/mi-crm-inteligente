import streamlit as st
import pandas as pd
from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import Optional
from rapidfuzz import fuzz
import datetime

# 1. CONFIGURACIÓN DE LA BASE DE DATOS
class Contacto(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    email: str = Field(index=True, unique=True)
    telefono: Optional[str] = None
    empresa: Optional[str] = None
    fecha_registro: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

sqlite_url = "sqlite:///crm_data.db"
engine = create_engine(sqlite_url)
SQLModel.metadata.create_all(engine)

# 2. INTERFAZ DE USUARIO (UI)
st.set_page_config(page_title="CRM Inteligente WOM", layout="wide")

st.sidebar.title("Navegación")
menu = st.sidebar.radio("Ir a:", ["Dashboard", "Clientes", "Importar Datos", "Configuración"])

# --- VISTA: DASHBOARD ---
if menu == "Dashboard":
    st.title("📊 Resumen Ejecutivo")
    with Session(engine) as session:
        total = len(session.exec(select(Contacto)).all())
    
    col1, col2 = st.columns(2)
    col1.metric("Total de Contactos", total)
    col2.metric("Nuevos hoy", 0) # Lógica para implementar después

# --- VISTA: CLIENTES ---
elif menu == "Clientes":
    st.title("👥 Gestión de Contactos")
    with Session(engine) as session:
        contactos = session.exec(select(Contacto)).all()
        if contactos:
            df = pd.DataFrame([c.dict() for c in contactos])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Aún no hay contactos registrados.")

# --- VISTA: IMPORTAR (Deduplicación) ---
elif menu == "Importar Datos":
    st.title("📥 Importación Inteligente")
    archivo = st.file_uploader("Sube tu Excel o CSV de clientes", type=["xlsx", "csv"])
    
    if archivo:
        df_nuevo = pd.read_excel(archivo) if archivo.name.endswith('xlsx') else pd.read_csv(archivo)
        st.write("Vista previa:", df_nuevo.head(3))
        
        if st.button("Procesar e Importar"):
            with Session(engine) as session:
                for _, row in df_nuevo.iterrows():
                    # Lógica simple de deduplicación por Email
                    existente = session.exec(select(Contacto).where(Contacto.email == row['email'])).first()
                    if not existente:
                        nuevo = Contacto(
                            nombre=row['nombre'],
                            email=row['email'],
                            empresa=row.get('empresa', 'N/A')
                        )
                        session.add(nuevo)
                session.commit()
            st.success("¡Datos importados con éxito! (Se omitieron duplicados exactos)")

# --- VISTA: CONFIGURACIÓN ---
elif menu == "Configuración":
    st.title("⚙️ Ajustes")
    st.write("Aquí conectarás tu Google Calendar pronto.")
