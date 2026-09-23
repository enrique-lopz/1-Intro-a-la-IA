from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.chunk import chunk_text
from app.embed import get_embedding
from app.store import agregar_chunks, consultar_similares
from app.generate import generar_respuesta

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
def ingestar_documento(doc: Documento):
    """
    Recibe un documento, lo divide en fragmentos, obtiene sus vectores 
    y lo guarda en la base de datos vectorial.
    """
    try:
        # 1. Dividimos el texto del documento en chunks
        chunks = chunk_text(doc.contenido_texto)
        
        # Validamos que el documento no esté vacío
        if not chunks:
            raise HTTPException(status_code=400, detail="El documento está vacío o no generó chunks.")

        # Preparar las listas para ChromaDB
        ids = []
        embeddings = []
        metadatos = []
        
        # 2. Incrustar con Google AI: Iteramos sobre cada chunk para obtener su vector
        for i, chunk_texto in enumerate(chunks):
            # Creamos un identificador único (ej. "manual.txt_chunk_0")
            chunk_id = f"{doc.nombre_archivo}_chunk_{i}"
            ids.append(chunk_id)
            
            # Pedimos el vector a Google AI
            vector = get_embedding(chunk_texto)
            embeddings.append(vector)
            
            # 3. Guardar metadatos: Registramos el archivo de origen (source)
            metadatos.append({"source": doc.nombre_archivo})
            
        # 4. Persistir en Chroma: Guardamos todo en la base de datos
        agregar_chunks(ids=ids, documentos=chunks, embeddings=embeddings, metadatos=metadatos)
        
        # 5. Responder: Devolvemos el conteo de indexación
        return {
            "mensaje": "Indexación exitosa",
            "documentos_indexados": 1,
            "chunks_indexados": len(chunks)
        }
        
    except Exception as e:
        # Manejo de errores por si falla la cuota de Google AI o la conexión
        raise HTTPException(status_code=500, detail=str(e))

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