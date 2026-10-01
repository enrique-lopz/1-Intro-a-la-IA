from typing import Union
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel

from app.chunk import chunk_text
from app.embed import get_embedding, get_embeddings_batch
from app.store import agregar_chunks, consultar_similares
from app.generate import generar_respuesta
from app.pdf_utils import extraer_texto_pdf

app = FastAPI(title="API del Sistema RAG")


class Documento(BaseModel):
    nombre_archivo: str
    contenido_texto: str

class Pregunta(BaseModel):
    question: str
    top_k: int = 3

@app.get("/health")
def health_check():
    """Confirma que la API está viva."""
    return {"status": "ok", "message": "La API está viva y funcionando"}

@app.post("/ingest")
def ingestar_documentos(payload: Union[Documento, list[Documento]]):
    """
    Recibe uno o varios documentos, los divide en fragmentos, obtiene sus vectores 
    en lotes y los guarda en la base de datos vectorial ChromaDB.
    Filtra e informa documentos omitidos si están vacíos o sin texto.
    """
    try:
        docs = [payload] if isinstance(payload, Documento) else payload
        if not docs:
            raise HTTPException(status_code=400, detail="No se proporcionaron documentos para ingestar.")

        todos_los_chunks = []
        todos_los_ids = []
        todos_los_metadatos = []
        archivos_exitosos = []
        archivos_omitidos = []

        for doc in docs:
            texto = doc.contenido_texto.strip() if doc.contenido_texto else ""
            if not texto:
                archivos_omitidos.append({
                    "nombre": doc.nombre_archivo,
                    "motivo": "El documento está vacío o no contiene texto legible."
                })
                continue

            chunks = chunk_text(texto)
            if not chunks:
                archivos_omitidos.append({
                    "nombre": doc.nombre_archivo,
                    "motivo": "No se generaron fragmentos (chunks) a partir del texto."
                })
                continue

            # Preparar identificadores únicos y metadatos con origen específico
            for i, chunk in enumerate(chunks):
                todos_los_chunks.append(chunk)
                todos_los_ids.append(f"{doc.nombre_archivo}_chunk_{i}")
                todos_los_metadatos.append({"source": doc.nombre_archivo})

            archivos_exitosos.append(doc.nombre_archivo)

        # Si ninguno de los documentos fue válido
        if not todos_los_chunks:
            motivos = "; ".join([f"{o['nombre']}: {o['motivo']}" for o in archivos_omitidos])
            raise HTTPException(
                status_code=400, 
                detail=f"Ninguno de los documentos contiene texto válido para indexar. Detalles: {motivos}"
            )

        # 2. Incrustar con Google AI en lotes con pausas preventivas y exponential backoff
        embeddings = get_embeddings_batch(todos_los_chunks, batch_size=20, pausa_segundos=1.5)
            
        # 3. Persistir en Chroma: Guardamos o actualizamos en la base de datos
        agregar_chunks(ids=todos_los_ids, documentos=todos_los_chunks, embeddings=embeddings, metadatos=todos_los_metadatos)
        
        # 4. Responder con resumen detallado de la indexación
        return {
            "mensaje": "Indexación exitosa",
            "documentos_indexados": len(archivos_exitosos),
            "chunks_indexados": len(todos_los_chunks),
            "archivos_exitosos": archivos_exitosos,
            "archivos_omitidos": archivos_omitidos
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Alias para mantener retrocompatibilidad con referencias internas
ingestar_documento = ingestar_documentos

@app.post("/ingest-files")
async def ingestar_archivos(files: list[UploadFile] = File(...)):
    """
    Recibe múltiples archivos (.pdf, .txt o .md), procesa los válidos,
    extrae texto e indexa todos sus fragmentos en ChromaDB, reportando
    cuáles se indexaron y cuáles se omitieron.
    """
    try:
        if not files:
            raise HTTPException(status_code=400, detail="No se seleccionó ningún archivo para subir.")

        docs_validos = []
        archivos_omitidos = []

        for file in files:
            nombre = file.filename or "documento"
            extension = nombre.lower().split(".")[-1] if "." in nombre else ""

            contenido_bytes = await file.read()
            if not contenido_bytes:
                archivos_omitidos.append({
                    "nombre": nombre,
                    "motivo": "El archivo está completamente vacío (0 bytes)."
                })
                continue

            if extension == "pdf":
                try:
                    texto = extraer_texto_pdf(contenido_bytes)
                    docs_validos.append(Documento(nombre_archivo=nombre, contenido_texto=texto))
                except ValueError as ve:
                    archivos_omitidos.append({
                        "nombre": nombre,
                        "motivo": str(ve)
                    })
            elif extension in ["txt", "md"]:
                try:
                    texto = contenido_bytes.decode("utf-8")
                except UnicodeDecodeError:
                    try:
                        texto = contenido_bytes.decode("latin-1")
                    except Exception as de:
                        archivos_omitidos.append({
                            "nombre": nombre,
                            "motivo": f"Error de decodificación: {str(de)}"
                        })
                        continue

                if not texto.strip():
                    archivos_omitidos.append({
                        "nombre": nombre,
                        "motivo": "El archivo de texto está vacío."
                    })
                    continue

                docs_validos.append(Documento(nombre_archivo=nombre, contenido_texto=texto))
            else:
                archivos_omitidos.append({
                    "nombre": nombre,
                    "motivo": f"Extensión '.{extension}' no soportada (solo .pdf, .txt, .md)."
                })

        if not docs_validos:
            motivos = "; ".join([f"{o['nombre']}: {o['motivo']}" for o in archivos_omitidos])
            raise HTTPException(
                status_code=400,
                detail=f"Ninguno de los archivos subidos contiene texto indexable. Detalles: {motivos}"
            )

        resultado = ingestar_documentos(docs_validos)
        # Combinar omitidos detectados durante la lectura de archivos físicos
        resultado["archivos_omitidos"].extend(archivos_omitidos)
        return resultado

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado al procesar archivos: {str(e)}")

@app.post("/ingest-file")
async def ingestar_archivo(file: UploadFile = File(...)):
    """
    Endpoint retrocompatible para la ingesta de un único archivo (.pdf, .txt o .md).
    """
    return await ingestar_archivos([file])

@app.post("/query")
def consultar_documentos(req: Pregunta):
    """
    Recibe una pregunta, busca fragmentos relevantes en ChromaDB, 
    y genera una respuesta anclada usando Gemini.
    """
    try:
        # 1. Obtener el vector de la pregunta
        vector_pregunta = get_embedding(req.question)
        
        # 2. Buscar en ChromaDB (incluyendo las distancias para el score)
        resultados = consultar_similares(vector_pregunta, top_k=req.top_k)
        
        textos_recuperados = []
        citas = []
        
        # 3. Extraer los datos si hubo resultados
        if resultados.get('documents') and resultados['documents'][0]:
            for i in range(len(resultados['documents'][0])):
                texto = resultados['documents'][0][i]
                metadato = resultados['metadatas'][0][i]
                chunk_id = resultados['ids'][0][i]
                
                # ChromaDB devuelve distancias (L2 al cuadrado para vectores normalizados).
                # Convertimos la distancia a similitud matemática coseno estimada: similitud = 1 - (distancia / 2)
                distancia = resultados['distances'][0][i] if 'distances' in resultados and resultados['distances'] else 2.0
                score = round(max(0.0, 1.0 - (distancia / 2.0)), 4)
                
                textos_recuperados.append(texto)
                citas.append({
                    "id": chunk_id,
                    "source": metadato.get("source", "desconocido"),
                    "text": texto,
                    "score": score
                })
        
        # 4. Generar la respuesta final con Gemini (aplicando la regla de abstención por score y contenido)
        scores_recuperados = [c["score"] for c in citas]
        respuesta_final, se_abstuvo = generar_respuesta(
            req.question, 
            textos_recuperados, 
            scores=scores_recuperados
        )
        
        # 5. Devolver exactamente la estructura que pide el proyecto
        return {
            "answer": respuesta_final,
            "citations": citas,
            "abstained": se_abstuvo
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))