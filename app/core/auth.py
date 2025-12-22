from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app import supabase

# Criamos o Blueprint (um pedaço modular da aplicação)
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Se o usuário já estiver logado (e a sessão for válida), avisa ou redireciona
    if 'user_token' in session:
        return "<h1>Você já está logado! (Em breve redirecionará para o Dashboard)</h1>"

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            # 1. Tenta autenticar no Supabase
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            # 2. SUCESSO: Configura a sessão
            
            # Torna a sessão permanente para obedecer ao tempo limite de 30min definido no __init__.py
            session.permanent = True 
            
            # Guarda os dados essenciais
            session['user_token'] = response.session.access_token
            session['user_email'] = response.user.email
            session['user_id'] = response.user.id
            
            # 3. Retorno temporário (logo substituiremos pela rota do Dashboard)
            return "<h1>Login Sucesso! Sessão segura ativa por 5min.</h1>"

        except Exception as e:
            # Erro: Senha errada ou usuário não existe
            flash("E-mail ou senha incorretos.")
            print(f"Erro de Login: {e}") # Log no terminal para debug
            return redirect(url_for('auth.login'))

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    # Limpa a sessão do Flask
    session.clear()
    
    # Desloga do Supabase também
    try:
        supabase.auth.sign_out()
    except:
        pass # Ignora erro se já estiver deslogado lá
        
    return redirect(url_for('auth.login'))