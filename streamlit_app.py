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

# --- VISTA: IMPORTAR DATOS (Versión Pro) ---
elif menu == "Importar Datos":
    st.title("📥 Importación Inteligente de Clientes")
    st.info("Asegúrate de que tu Excel tenga las columnas: 'nombre' y 'email'")
    
    archivo = st.file_uploader("Sube tu Excel (.xlsx)", type=["xlsx"])
    
    if archivo:
        df_nuevo = pd.read_excel(archivo)
        
        # Limpieza inicial: quitamos filas totalmente vacías
        df_nuevo = df_nuevo.dropna(subset=['nombre', 'email'])
        
        st.write(f"📊 Total de registros detectados en el archivo: {len(df_nuevo)}")
        
        if st.button("🚀 Iniciar Carga"):
            exitos = 0
            duplicados = 0
            errores = 0
            
            with Session(engine) as session:
                for _, row in df_nuevo.iterrows():
                    try:
                        # Limpiamos espacios en blanco alrededor de los textos
                        email_limpio = str(row['email']).strip().lower()
                        nombre_limpio = str(row['nombre']).strip()
                        
                        # Verificamos si YA existe en la base de datos
                        # (Esto evita el error rojo de SQLAlchemy)
                        stmt = select(Contacto).where(Contacto.email == email_limpio)
                        existente = session.exec(stmt).first()
                        
                        if existente:
                            duplicados += 1
                            continue # Se salta al siguiente
                            
                        nuevo = Contacto(
                            nombre=nombre_limpio,
                            email=email_limpio,
                            empresa=str(row.get('empresa', 'WOM')).strip()
                        )
                        session.add(nuevo)
                        exitos += 1
                        
                    except Exception as e:
                        errores += 1
                        st.error(f"Error en fila {nombre_limpio}: {e}")
                
                session.commit()
            
            # --- REPORTE FINAL ---
            st.success(f"✅ Proceso terminado")
            col1, col2, col3 = st.columns(3)
            col1.metric("Cargados", exitos)
            col2.metric("Duplicados/Omitidos", duplicados)
            col3.metric("Errores", errores)
            
            if exitos > 0:
                st.balloons()
