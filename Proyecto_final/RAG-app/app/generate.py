import os
from dotenv import load_dotenv
from google import genai

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Inicializamos el cliente 
cliente = genai.Client()

# Umbral mínimo de similitud por defecto para considerar evidencia relevante
UMBRAL_MINIMO_SCORE = 0.65

def generar_respuesta(
    pregunta: str, 
    fragmentos: list[str], 
    scores: list[float] | None = None, 
    umbral_score: float = UMBRAL_MINIMO_SCORE
) -> tuple[str, bool]:
    """
    Envía los fragmentos recuperados a Gemini para generar una respuesta anclada.
    Si se especifican scores y ninguno supera el umbral mínimo (o no hay fragmentos),
    se abstiene inmediatamente sin llamar a Gemini.
    
    Retorna una tupla con el texto de la respuesta y un booleano indicando si se abstuvo.
    """
    # 1. Validación de fragmentos vacíos
    if not fragmentos:
        return "No tengo evidencia suficiente.", True

    # 2. Validación de umbral de score mínimo (si se proveen scores)
    if scores is not None and len(scores) > 0:
        max_score = max(scores)
        if max_score < umbral_score:
            # Ningún fragmento alcanza el score mínimo: abstención directa sin llamar a Gemini
            return "No tengo evidencia suficiente. (umbral de similitud no alcanzado)", True

        # Filtrar únicamente los fragmentos que superan el umbral para no contaminar el contexto
        if len(scores) == len(fragmentos):
            fragmentos_validos = [
                f for f, s in zip(fragmentos, scores) if s >= umbral_score
            ]
            if not fragmentos_validos:
                return "No tengo evidencia suficiente.(not fragmentos válidos)", True
            fragmentos = fragmentos_validos

    # 3. Construir el contexto numerado para que Gemini pueda citarlo
    contexto_texto = ""
    for i, texto in enumerate(fragmentos):
        # Sumamos 1 al índice para que las citas empiecen en [1] en lugar de [0]
        contexto_texto += f"[{i+1}] {texto}\n\n"
        
    # 4. Diseñar el prompt con reglas estrictas de abstención y citado
    prompt = f"""
    Eres un asistente estricto. Tu tarea es responder a la pregunta del usuario utilizando ÚNICAMENTE la evidencia proporcionada a continuación.
    
    Reglas:
    1. Responde en español.
    2. Debes incluir citas numeradas (ejemplo: [1], [2]) correspondientes a los fragmentos de donde sacaste la información.
    3. Si la respuesta a la pregunta NO se encuentra en la evidencia, DEBES abstenerte de responder. En ese caso, escribe exactamente la frase: "No tengo evidencia suficiente." No uses tu conocimiento previo ni inventes información.
    
    Evidencia:
    {contexto_texto}
    
    Pregunta: {pregunta}
    """
    
    try:
        # 5. Llamar al modelo de Gemini usando el nuevo cliente (con fallback si hay sobrecarga 503)
        try:
            respuesta = cliente.models.generate_content(
                model='gemini-3.5-flash',
                contents=prompt
            )
        except Exception as e_flash:
            if "503" in str(e_flash) or "UNAVAILABLE" in str(e_flash):
                respuesta = cliente.models.generate_content(
                    model='gemini-3.6-flash',
                    contents=prompt
                )
            else:
                raise e_flash

        texto_final = respuesta.text.strip()
        
        # 6. Evaluar si el modelo decidió abstenerse basándonos en la frase clave
        se_abstuvo = "no tengo evidencia suficiente" in texto_final.lower()
        
        return texto_final, se_abstuvo
        
    except Exception as e:
        # Si falla la API de Google, nos abstenemos por seguridad
        return f"Error en la generación: {str(e)}", True

# --- Prueba local ---
if __name__ == "__main__":
    print("Probando generación con Gemini y validación de umbrales...\n")
    
    mis_fragmentos = [
        "El sistema RAG evita alucinaciones al basarse en evidencia recuperada.",
        "FastAPI es el framework utilizado para construir la API."
    ]
    
    # Prueba 1: Pregunta dentro del dominio con scores altos (pasa a Gemini)
    preg_valida = "¿Cómo evita alucinaciones el sistema RAG?"
    scores_altos = [0.85, 0.72]
    resp1, abs1 = generar_respuesta(preg_valida, mis_fragmentos, scores=scores_altos)
    print(f"Prueba 1 (Score alto >= {UMBRAL_MINIMO_SCORE}):")
    print(f"Pregunta: {preg_valida}")
    print(f"Scores: {scores_altos}")
    print(f"Respuesta: {resp1} | ¿Se abstuvo?: {abs1}\n")
    
    # Prueba 2: Pregunta fuera del dominio con scores bajos (no llama a Gemini, abstención inmediata)
    preg_invalida = "¿Cuál es la capital de Francia?"
    scores_bajos = [0.42, 0.38]
    resp2, abs2 = generar_respuesta(preg_invalida, mis_fragmentos, scores=scores_bajos)
    print(f"Prueba 2 (Score bajo < {UMBRAL_MINIMO_SCORE}, abstención temprana sin invocar Gemini):")
    print(f"Pregunta: {preg_invalida}")
    print(f"Scores: {scores_bajos}")
    print(f"Respuesta: {resp2} | ¿Se abstuvo?: {abs2}\n")

    # Prueba 3: Sin lista de scores (retrocompatibilidad)
    resp3, abs3 = generar_respuesta(preg_valida, mis_fragmentos)
    print(f"Prueba 3 (Sin scores - compatibilidad previa):")
    print(f"Pregunta: {preg_valida}")
    print(f"Respuesta: {resp3} | ¿Se abstuvo?: {abs3}")