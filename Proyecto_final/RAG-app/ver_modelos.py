import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

# La nueva versión requiere instanciar un objeto Client
client = genai.Client()

print("Modelos disponibles:")
# El listado de modelos ahora se consulta a través del cliente
for m in client.models.list():
    print(m.name)