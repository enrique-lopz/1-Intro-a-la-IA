import os
import math
from dotenv import load_dotenv
# 1. Importación corregida para el nuevo SDK 'google-genai'
from google import genai

# Cargar las variables guardadas en tu archivo .env
load_dotenv()

# 2. Instanciamos el cliente en lugar de usar genai.configure()
# El nuevo SDK busca la variable GEMINI_API_KEY por defecto. 
# Como tu proyecto exige usar "GOOGLE_API_KEY", se la pasamos explícitamente.
cliente = genai.Client()

def get_embedding(text: str) -> list[float]:
    """
    Envía texto a Google AI y devuelve su vector (lista de flotantes).
    """
    # 3. La nueva forma de llamar al modelo de embeddings
    respuesta = cliente.models.embed_content(
        model="gemini-embedding-001",
        contents=text
    )
    # 4. Accedemos a los valores del vector en la nueva estructura de respuesta
    return respuesta.embeddings[0].values

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