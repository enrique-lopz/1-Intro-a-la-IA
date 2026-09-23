
# Proyecto RAG

### Instalando el entorno virtual: 
Si usas Windows:
``` bash
cd Proyecto_final/RAG-app
python -m venv venv #Crear el entorno
venv\Scripts\activate #Activar el entorno
python -m pip install -r requirements.txt
```

Si usas macOS o Linux:
``` bash
cd Proyecto_final/RAG-app
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

Para reanudar el trabajo solo reactivar el entorno virtual, en Windows: `venv\Scripts\activate` y en MacOS: `source venv/bin/activate`

### Activar Uvicorn
``` bash
uvicorn app.main:app --reload --port 8000
```
Para detenerlo, haz clic dentro de la terminal en VS Code y presiona las teclas `Ctrl + C`.

