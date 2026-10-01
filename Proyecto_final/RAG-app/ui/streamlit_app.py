import streamlit as st
import requests

# URL de tu API local
API_URL = "http://localhost:8000"

st.title("Sistema RAG - Maestría en Inteligencia Artificial")
st.markdown("Interfaz gráfica para consultar documentos indexados.")

# --- Barra lateral: Carga e Ingesta de Documentos ---
with st.sidebar:
    st.header("1. Cargar Documentos")
    st.info("Sube uno o varios archivos de texto (.txt) o PDF (.pdf) para indexarlos en ChromaDB.")
    
    archivos_subidos = st.file_uploader(
        "Sube uno o varios archivos (.txt o .pdf)", 
        type=["txt", "pdf"],
        accept_multiple_files=True
    )
    
    if st.button("Indexar Documentos"):
        if not archivos_subidos:
            st.warning("Por favor selecciona al menos un archivo antes de indexar.")
        else:
            try:
                with st.spinner("Procesando, extrayendo texto e indexando en ChromaDB..."):
                    # Llamada HTTP POST multipart con la lista de archivos a /ingest-files
                    archivos_multipart = [
                        ("files", (arch.name, arch.getvalue(), arch.type or "application/octet-stream"))
                        for arch in archivos_subidos
                    ]
                    res = requests.post(f"{API_URL}/ingest-files", files=archivos_multipart)
                    
                if res.status_code == 200:
                    datos = res.json()
                    st.success(
                        f"¡Indexación exitosa! {datos['documentos_indexados']} documento(s) indexado(s) "
                        f"({datos['chunks_indexados']} chunks creados en ChromaDB)."
                    )
                    
                    if datos.get("archivos_exitosos"):
                        st.markdown("**Archivos indexados correctamente:**")
                        for arch in datos["archivos_exitosos"]:
                            st.markdown(f"- ✅ `{arch}`")
                    
                    if datos.get("archivos_omitidos"):
                        st.warning("⚠️ **Archivos omitidos:**")
                        for omitido in datos["archivos_omitidos"]:
                            st.markdown(f"- **`{omitido['nombre']}`**: {omitido['motivo']}")
                else:
                    try:
                        detalle = res.json().get("detail", res.text)
                    except Exception:
                        detalle = res.text
                    st.error(f"Error de la API: {detalle}")
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