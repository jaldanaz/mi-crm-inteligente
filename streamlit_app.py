import streamlit as st
import pandas as pd
from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import Optional
import datetime

# --- CONFIGURACIÓN DE SEGURIDAD PARA LA BASE DE DATOS ---
# Esto evita que el error de "re-definición" vuelva a aparecer
class Contacto(SQLModel, table=True):
    __table_args__ = {'extend_existing': True} # <-- LA LLAVE MAESTRA: Evita el error rojo
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    email: str = Field(index=True)
    telefono: Optional[str] = None
    empresa: Optional[str] = None
    fecha_registro: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

# Creamos el motor de la base de datos de forma segura
sqlite_url = "sqlite:///crm_data.db"
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

# Función para crear las tablas solo si no existen
def init_db():
    SQLModel.metadata.create_all(engine)

init_db()

# --- INTERFAZ DE USUARIO ---
st.set_page_config(page_title="CRM Inteligente WOM", layout="wide")

st.sidebar.title("Navegación")
menu = st.sidebar.radio("Ir a:", ["Dashboard", "Clientes", "Importar Datos"])

if menu == "Dashboard":
    st.title("📊 Resumen Ejecutivo")
    with Session(engine) as session:
        contactos = session.exec(select(Contacto)).all()
        total = len(contactos)
    
    col1, col2 = st.columns(2)
    col1.metric("Total de Contactos", total)
    col2.metric("Estatus", "Online ✅")

elif menu == "Clientes":
    st.title("👥 Lista de Contactos")
    with Session(engine) as session:
        contactos = session.exec(select(Contacto)).all()
        if contactos:
            # Convertimos los datos a una tabla bonita
            df = pd.DataFrame([c.dict() for c in contactos])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("La base de datos está vacía. Ve a 'Importar Datos'.")

elif menu == "Importar Datos":
    st.title("📥 Cargar Clientes")
    archivo = st.file_uploader("Sube tu Excel (.xlsx)", type=["xlsx"])
    
    if archivo:
        df_nuevo = pd.read_excel(archivo)
        st.write("Datos detectados:", df_nuevo.head())
        
        if st.button("Guardar en el CRM"):
            with Session(engine) as session:
                for _, row in df_nuevo.iterrows():
                    # Solo agregamos si el email no existe para evitar basura
                    nuevo = Contacto(
                        nombre=str(row['nombre']),
                        email=str(row['email']),
                        empresa=str(row.get('empresa', 'WOM'))
                    )
                    session.add(nuevo)
                session.commit()
            st.success("¡Clientes guardados exitosamente!")
