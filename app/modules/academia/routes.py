from flask import Blueprint, render_template, session, redirect, url_for

# Configura o Blueprint. 
# template_folder='templates' diz para ele procurar HTMLs dentro da pasta templates do módulo
academia_bp = Blueprint('academia', __name__, url_prefix='/academia', template_folder='templates')

@academia_bp.before_request
def check_auth():
    """Protege TODAS as rotas deste módulo. Se não tiver token, manda pro login."""
    if 'user_token' not in session:
        return redirect(url_for('auth.login'))

@academia_bp.route('/dashboard')
def dashboard():
    return render_template('academia/dashboard.html')