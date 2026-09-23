

def chunk_text(text: str, chunk_size: int = 300, overlap: int = 50) -> list[str]:
    """
    Divide un texto largo en fragmentos (chunks) más pequeños basados en la cantidad de palabras,
    manteniendo un solape (overlap) entre ellos para no perder el contexto.
    
    Parámetros:
    - text: El texto completo extraído del documento (.txt o .md).
    - chunk_size: Número máximo de palabras por chunk.
    - overlap: Número de palabras que se repetirán entre un chunk y el siguiente.
    
    Retorna:
    - Una lista de strings, donde cada string es un chunk.
    """
    # Separamos todo el texto en una lista de palabras
    words = text.split()
    chunks = []
    
    # Validamos que el solape no sea mayor o igual al tamaño del chunk
    if overlap >= chunk_size:
        raise ValueError("El solape (overlap) debe ser menor que el tamaño del chunk (chunk_size).")
    
    # Avanzamos por la lista de palabras dando "saltos"
    # El tamaño del salto es (chunk_size - overlap)
    step = chunk_size - overlap
    
    for i in range(0, len(words), step):
        # Tomamos una rebanada de palabras desde 'i' hasta 'i + chunk_size'
        chunk_words = words[i : i + chunk_size]
        
        # Volvemos a unir las palabras con espacios y lo guardamos
        chunk_text = " ".join(chunk_words)
        chunks.append(chunk_text)
        
        # Si este chunk ya llegó al final de las palabras, terminamos el ciclo
        if i + chunk_size >= len(words):
            break
            
    return chunks

# --- Pequeña prueba local (Opcional) ---
if __name__ == "__main__":
    texto_prueba = "Este es un texto de prueba para ver como funciona la division de palabras en nuestro sistema RAG. Queremos asegurar que el contexto no se pierda."
    # Hacemos chunks muy pequeños solo para probar que funcione
    resultado = chunk_text(texto_prueba, chunk_size=10, overlap=3)
    
    for idx, chunk in enumerate(resultado):
        print(f"Chunk {idx + 1}: {chunk}")