from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app import supabase

# Criamos o Blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Se já estiver logado, redireciona para o Dashboard da Academia
    if 'user_token' in session:
        return redirect(url_for('academia.dashboard'))

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
            session.permanent = True 
            session['user_token'] = response.session.access_token
            session['user_email'] = response.user.email
            session['user_id'] = response.user.id
            
            # 3. Redireciona para o Dashboard da Academia
            return redirect(url_for('academia.dashboard'))

        except Exception as e:
            # Erro: Senha errada ou usuário não existe
            flash("E-mail ou senha incorretos.")
            print(f"Erro de Login: {e}") 
            return redirect(url_for('auth.login'))

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    try:
        supabase.auth.sign_out()
    except:
        pass
    return redirect(url_for('auth.login'))