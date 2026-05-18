# SIU-2-FRONTEND

# Crear y activar entorno virtual (Windows)
python -m venv .venv .venv\Scripts\activate

# Crear y activar entorno virtual (Linux/macOS)
python3 -m venv .venv source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Correr app
flask run