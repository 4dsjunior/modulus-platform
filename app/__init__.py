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
    
    # --- 1. CONFIGURAÇÕES DE SEGURANÇA DE SESSÃO (MANTIDO) ---
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'desenvolvimento')
    
    # Tempo de inatividade (5 minutos)
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)
    
    # Sessão expira ao fechar o navegador
    app.config['SESSION_PERMANENT'] = False
    
    # Proteção de cookies
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

    # --- 2. INICIALIZAÇÃO DO SUPABASE (MANTIDO) ---
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
    from app.modules.activities.routes import activities_bp
    
    # AQUI ESTÁ A CORREÇÃO DO ERRO 404:
    # Adicionamos url_prefix='/auth' para que a rota final seja /auth/login
    app.register_blueprint(auth_bp, url_prefix='/auth') 
    
    app.register_blueprint(academia_bp)
    app.register_blueprint(admin_bp) # Se quiser padronizar, pode usar url_prefix='/admin' aqui também
    app.register_blueprint(activities_bp)

    # --- 4. MIDDLEWARE DE SESSÃO ATIVA (MANTIDO) ---
    @app.before_request
    def manage_session():
        # Faz com que cada clique do usuário resete o cronômetro de 5 minutos
        session.permanent = True
        session.modified = True

    # --- 5. ROTA RAIZ (MANTIDO) ---
    @app.route('/')
    def index():
        # Redireciona para o login correto
        return redirect(url_for('auth.login'))

    return app