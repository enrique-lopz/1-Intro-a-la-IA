import io
from pypdf import PdfReader


def extraer_texto_pdf(contenido_bytes: bytes) -> str:
    """
    Extrae el texto de un documento PDF proporcionado como secuencia de bytes.
    
    Parámetros:
    - contenido_bytes: Bytes del archivo PDF cargado en memoria.
    
    Retorna:
    - Texto completo extraído como string.
    
    Lanza:
    - ValueError si el PDF está protegido o no contiene texto legible (ej. escaneado).
    """
    try:
        archivo_en_memoria = io.BytesIO(contenido_bytes)
        lector = PdfReader(archivo_en_memoria)
        
        # Validar si el archivo está encriptado con contraseña
        if lector.is_encrypted:
            try:
                lector.decrypt("")
            except Exception:
                raise ValueError("El archivo PDF está protegido con contraseña y no se puede leer.")
                
        paginas_texto = []
        for i, pagina in enumerate(lector.pages):
            texto_pagina = pagina.extract_text()
            if texto_pagina and texto_pagina.strip():
                paginas_texto.append(texto_pagina.strip())
                
        texto_final = "\n\n".join(paginas_texto).strip()
        
        if not texto_final:
            raise ValueError(
                "El archivo PDF no contiene texto legible (es posible que sea un documento "
                "escaneado compuesto únicamente por imágenes, lo cual requiere OCR)."
            )
            
        return texto_final
        
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"Error al procesar el archivo PDF: {str(e)}")


# --- Prueba local ---
if __name__ == "__main__":
    print("Probando utilidades de extracción PDF con pypdf...")
    from pypdf import PdfWriter
    
    # Crear un PDF sintético en memoria para prueba
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    # Escribir a bytes
    buffer = io.BytesIO()
    writer.write(buffer)
    pdf_vacio_bytes = buffer.getvalue()
    
    try:
        extraer_texto_pdf(pdf_vacio_bytes)
        print("ERROR: Debería haber fallado con PDF vacío")
    except ValueError as e:
        print(f"Prueba PDF vacío pasada con éxito: {e}")

