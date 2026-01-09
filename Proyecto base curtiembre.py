import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

def conectar_google_sheets():
    # Definir los permisos que necesitamos
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    # Cargar las credenciales desde el archivo que subiste a GitHub
    creds = ServiceAccountCredentials.from_json_keyfile_name("creed.json", scope)
    client = gspread.authorize(creds)
    
    # Abrir la planilla "pendientes" y tomar la primera hoja
    spreadsheet = client.open("pendientes")
    sheet = spreadsheet.get_worksheet(0)
    return sheet

st.title("Control de Pendientes - Curtiembre")

try:
    # Conectar y traer los datos
    hoja = conectar_google_sheets()
    datos = hoja.get_all_records()
    
    if datos:
        df = pd.DataFrame(datos)
        st.write("### Listado actual de la planilla:")
        st.dataframe(df)
    else:
        st.warning("La planilla parece estar vacía.")

except Exception as e:
    st.error(f"Hubo un problema al conectar: {e}")

