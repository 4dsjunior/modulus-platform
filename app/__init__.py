from flask import Flask, redirect, url_for
from dotenv import load_dotenv
import os
from supabase import create_client, Client
from datetime import timedelta

# Carrega as variáveis do arquivo .env
load_dotenv()

# Cliente Global do Supabase
supabase: Client = None

def create_app():
    global supabase
    
    app = Flask(__name__)
    
    # IMPORTANTE: A Secret Key é necessária para a sessão funcionar
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'chave-padrao-desenvolvimento')

    # --- CONFIGURAÇÃO DE SEGURANÇA DA SESSÃO ---
    # Define que a sessão expira automaticamente em 30 minutos de inatividade
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)
    
    # Protege contra scripts maliciosos tentando ler o cookie via JavaScript
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    
    # (Opcional) Em produção (HTTPS), descomente a linha abaixo para obrigar conexão segura
    # app.config['SESSION_COOKIE_SECURE'] = True 
    # -------------------------------------------

    # 1. Iniciar Supabase
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        print("AVISO: Variáveis do Supabase não encontradas no .env")
    else:
        supabase = create_client(url, key)

    # 2. Registrar o Módulo de Auth
    from app.core.auth import auth_bp
    app.register_blueprint(auth_bp)

    # 3. Rota Raiz (Redireciona sempre para login)
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    return app