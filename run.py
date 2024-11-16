from app import create_app

# Cria a aplicação usando a função create_app
app = create_app()

if __name__ == "__main__":
    # Inicializa o servidor Flask
    app.run(debug=True)
