from waitress import serve
from app import create_app

app = create_app()

if __name__ == "__main__":
    print("Iniciando servidor TGC Logística en http://0.0.0.0:5000 ...")
    serve(app, host="0.0.0.0", port=5000)
