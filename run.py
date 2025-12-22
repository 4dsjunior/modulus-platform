from app import create_app

app = create_app()

if __name__ == '__main__':
    # Debug=True permite que o site recarregue sozinho quando você muda o código
    app.run(debug=True, port=5000)