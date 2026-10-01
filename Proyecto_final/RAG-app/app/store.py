import chromadb
import os

# 1. Configuramos el cliente para que guarde los datos en la carpeta "chroma/" en la raíz del proyecto
# Esto asegura la persistencia en disco 
PERSIST_DIRECTORY = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma")
chroma_client = chromadb.PersistentClient(path=PERSIST_DIRECTORY)

# 2. Creamos o recuperamos la colección donde guardaremos los documentos
# Le indicamos explícitamente que no use ningún embedder propio, ya que nosotros le pasaremos los vectores generados por Google AI
coleccion = chroma_client.get_or_create_collection(name="documentos_rag", metadata={"hnsw:space": "cosine"})

def agregar_chunks(ids: list[str], documentos: list[str], embeddings: list[list[float]], metadatos: list[dict]):
    """
    Agrega o actualiza los chunks de texto, vectores de Google AI y metadatos en ChromaDB.
    """
    coleccion.upsert(
        ids=ids,                  # Identificador único para cada chunk (ej. "doc1_chunk1")
        documents=documentos,     # El texto real del chunk
        embeddings=embeddings,    # Los vectores generados por Google AI
        metadatas=metadatos       # Diccionario con información extra (ej. {"source": "archivo.txt"})
    )

def consultar_similares(vector_pregunta: list[float], top_k: int = 3) -> dict:
    """
    Busca los 'top_k' chunks más parecidos matemáticamente al vector de la pregunta.
    """
    resultados = coleccion.query(
        query_embeddings=[vector_pregunta],
        n_results=top_k
    )
    return resultados

# --- Prueba local ---
if __name__ == "__main__":
    print("Iniciando prueba de base de datos vectorial ChromaDB...")
    
    # Datos de mentira para probar
    mis_ids = ["chunk_1", "chunk_2"]
    mis_textos = ["El perro corre feliz.", "Las tasas de interés subieron."]
    # Vectores inventados para que ChromaDB no marque error (en la vida real vienen de Google AI)
    mis_vectores = [[0.1, 0.2, 0.3], [0.9, 0.8, 0.7]]
    mis_metadatos = [{"source": "mascotas.txt"}, {"source": "economia.txt"}]
    
    # Agregamos a la base de datos
    agregar_chunks(mis_ids, mis_textos, mis_vectores, mis_metadatos)
    print("¡Chunks guardados correctamente en la carpeta chroma/!")
    
    # Hacemos una búsqueda falsa simulando un vector parecido al del perrito
    vector_busqueda = [0.15, 0.25, 0.35]
    resultados = consultar_similares(vector_busqueda, top_k=1)
    
    print("\nResultado de la búsqueda:")
    print(f"Texto recuperado: {resultados['documents'][0][0]}")
    print(f"Archivo origen: {resultados['metadatas'][0][0]['source']}")