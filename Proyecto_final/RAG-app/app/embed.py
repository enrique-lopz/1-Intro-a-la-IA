import os
import math
import time
from dotenv import load_dotenv
# 1. Importación corregida para el nuevo SDK 'google-genai'
from google import genai

# Cargar las variables guardadas en tu archivo .env
load_dotenv()

# 2. Instanciamos el cliente en lugar de usar genai.configure()
# El nuevo SDK busca la variable GEMINI_API_KEY por defecto. 
# Como tu proyecto exige usar "GOOGLE_API_KEY", se la pasamos explícitamente.
cliente = genai.Client()

def get_embeddings_batch(
    texts: list[str], 
    batch_size: int = 20, 
    pausa_segundos: float = 1.5, 
    max_reintentos: int = 4
) -> list[list[float]]:
    """
    Obtiene los vectores de incrustación (embeddings) para una lista de textos
    procesándolos en lotes (batches), con pausas preventivas entre lotes y 
    mecanismo de reintento exponencial (exponential backoff) en caso de error 429.
    """
    if not texts:
        return []
        
    todos_los_embeddings = []
    total_lotes = (len(texts) + batch_size - 1) // batch_size
    
    for indice_lote, i in enumerate(range(0, len(texts), batch_size)):
        lote = texts[i : i + batch_size]
        
        # Reintentos con exponential backoff en caso de cuota 429
        respuesta = None
        for intento in range(max_reintentos):
            try:
                respuesta = cliente.models.embed_content(
                    model="gemini-embedding-001",
                    contents=lote
                )
                break
            except Exception as e:
                es_error_cuota = "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e)
                if es_error_cuota and intento < max_reintentos - 1:
                    # Espera progresiva de 5s, 10s, 20s para permitir que la ventana de 15 RPM se restablezca
                    tiempo_espera = 5 * (2 ** intento)
                    print(f"Aviso: Límite de cuota alcanzado (429). Esperando {tiempo_espera}s antes de reintentar (intento {intento + 1}/{max_reintentos})...")
                    time.sleep(tiempo_espera)
                else:
                    raise e
                    
        # Extraemos los vectores del lote
        for emb in respuesta.embeddings:
            todos_los_embeddings.append(emb.values)
            
        # Pausa preventiva entre lotes (si no es el último lote) para no saturar los 15 RPM
        if indice_lote < total_lotes - 1 and pausa_segundos > 0:
            time.sleep(pausa_segundos)
            
    return todos_los_embeddings

def get_embedding(text: str) -> list[float]:
    """
    Envía un solo texto a Google AI y devuelve su vector (lista de flotantes).
    """
    vectores = get_embeddings_batch([text], batch_size=1, pausa_segundos=0.0)
    return vectores[0]

def calcular_similitud_coseno(vec1: list[float], vec2: list[float]) -> float:
    """
    Calcula la cercanía matemática entre dos vectores. 
    Mientras más se acerque a 1.0, más similares son los textos.
    """
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = math.sqrt(sum(a * a for a in vec1))
    magnitude2 = math.sqrt(sum(b * b for b in vec2))
    return dot_product / (magnitude1 * magnitude2)

# --- Prueba de validación ---
if __name__ == "__main__":
    print("Conectando con Google AI para generar vectores...")
    
    # 1. Dos frases similares y una ajena
    frase1 = "El perro corre feliz por el parque."
    frase2 = "Un canino juega alegremente en el jardín."
    frase3 = "Las tasas de interés de los bancos subieron un 5%."
    
    # 2. Obtenemos los vectores
    emb1 = get_embedding(frase1)
    emb2 = get_embedding(frase2)
    emb3 = get_embedding(frase3)
    
    # 3. Calculamos distancias matemáticas
    similitud_parecidas = calcular_similitud_coseno(emb1, emb2)
    similitud_distintas = calcular_similitud_coseno(emb1, emb3)
    
    print(f"Similitud entre frases parecidas: {similitud_parecidas:.4f}")
    print(f"Similitud con la frase ajena: {similitud_distintas:.4f}")