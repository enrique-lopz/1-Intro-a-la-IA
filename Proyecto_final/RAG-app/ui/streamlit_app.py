import streamlit as st
import requests

# URL de tu API local
API_URL = "http://localhost:8000"

st.title("Sistema RAG - Maestría en Inteligencia Artificial")
st.markdown("Interfaz gráfica para consultar documentos indexados.")

# --- Barra lateral: Carga e Ingesta de Documentos ---
with st.sidebar:
    st.header("1. Cargar Documentos")
    st.info("Sube un archivo de texto para indexarlo en ChromaDB.")
    
    archivo_subido = st.file_uploader("Sube un archivo (.txt)", type=["txt"])
    
    if st.button("Indexar Documento") and archivo_subido is not None:
        # Extraemos el texto del archivo
        contenido = archivo_subido.read().decode("utf-8")
        payload = {
            "nombre_archivo": archivo_subido.name,
            "contenido_texto": contenido
        }
        
        try:
            with st.spinner("Procesando, particionando e indexando..."):
                # Llamada HTTP POST al endpoint /ingest
                res = requests.post(f"{API_URL}/ingest", json=payload)
                
            if res.status_code == 200:
                datos = res.json()
                st.success(f"¡Indexación exitosa! {datos['chunks_indexados']} chunks creados en ChromaDB.")
            else:
                st.error(f"Error de la API: {res.text}")
        except requests.exceptions.ConnectionError:
            st.error("Error: No se pudo conectar con la API. ¿Está FastAPI corriendo en el puerto 8000?")

# --- Área principal: Consulta y Generación ---
st.header("2. Consultar al Sistema")
pregunta = st.chat_input("Escribe tu pregunta aquí...")

# Estados de error visibles requeridos por el proyecto
if pregunta:
    st.chat_message("user").write(pregunta)
    
    try:
        with st.spinner("Buscando evidencia y redactando respuesta con Gemini..."):
            # Llamada HTTP POST al endpoint /query
            res = requests.post(f"{API_URL}/query", json={"question": pregunta, "top_k": 3})
        
        if res.status_code == 200:
            datos = res.json()
            
            with st.chat_message("assistant"):
                # Mostrar la respuesta generada
                st.write(datos["answer"])
                
                # Mostrar aviso si el modelo se abstuvo
                if datos["abstained"]:
                    st.warning("El sistema se abstuvo de responder por falta de evidencia en el dominio.")
                
                # Desplegable para ver la evidencia (chunks, origen y score)
                if datos["citations"]:
                    with st.expander("Ver evidencia recuperada (Chunks)"):
                        for idx, cita in enumerate(datos["citations"]):
                            st.markdown(f"**Cita [{idx + 1}]**")
                            st.markdown(f"- **Archivo Origen:** `{cita['source']}`")
                            st.markdown(f"- **Similitud Matemática (Score):** `{cita['score']:.4f}`")
                            st.markdown(f"- **Fragmento de texto:** *\"{cita['text']}\"*")
                            st.divider()
        else:
            st.error("Error al procesar la consulta.")
    except requests.exceptions.ConnectionError:
        st.error("Error: No se pudo conectar con la API. ¿Está FastAPI corriendo en el puerto 8000?")