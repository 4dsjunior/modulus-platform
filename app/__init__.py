from flask import Flask, redirect, url_for, session
from dotenv import load_dotenv
import os
from supabase import create_client, Client
from datetime import timedelta

load_dotenv()

# Instância global do Supabase (Anon Key)
supabase: Client = None

def create_app():
    global supabase
    app = Flask(__name__)
    
    # --- 1. CONFIGURAÇÕES DE SEGURANÇA DE SESSÃO ---
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'desenvolvimento')
    
    # Tempo de inatividade (5 minutos)
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)
    
    # Sessão expira ao fechar o navegador
    app.config['SESSION_PERMANENT'] = False
    
    # Proteção de cookies (impede acesso via JS e ataques de interceptação)
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

    # --- 2. INICIALIZAÇÃO DO SUPABASE ---
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        print("AVISO: Variáveis do Supabase (URL/KEY) ausentes no .env")
    else:
        supabase = create_client(url, key)

    # --- 3. REGISTRO DE MÓDULOS (BLUEPRINTS) ---
    from app.core.auth import auth_bp
    from app.modules.academia.routes import academia_bp
    from app.core.admin import admin_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(academia_bp)
    app.register_blueprint(admin_bp)

    # --- 4. MIDDLEWARE DE SESSÃO ATIVA ---
    @app.before_request
    def manage_session():
        # Faz com que cada clique do usuário resete o cronômetro de 5 minutos
        session.permanent = True
        session.modified = True

    # --- 5. ROTA RAIZ ---
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    return app