from flask import Blueprint, render_template, session, redirect, url_for

# Definição do Blueprint
# url_prefix='/academia' significa que as rotas serão: 
# /academia/dashboard e /academia/configuracoes
academia_bp = Blueprint('academia', __name__, url_prefix='/academia', template_folder='templates')

@academia_bp.route('/dashboard')
def dashboard():
    """
    Renderiza o painel principal (Dashboard).
    """
    # 1. Segurança: Verifica se está logado
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    # 2. Contexto de Dados (Placeholders)
    # Isso evita o erro 'variable undefined' no template dashboard.html
    # Futuramente, substituiremos esses 0 por queries reais ao Supabase
    context = {
        'total_alunos': 0,        # Necessário para o card "Alunos Ativos"
        'receita_prevista': 0.00, 
        'inadimplencia': 0.00
    }

    return render_template('academia/dashboard.html', **context)


@academia_bp.route('/configuracoes')
def settings():
    """
    Renderiza a nova tela de Configurações (Atividades, Planos, Financeiro).
    O HTML retornado (settings.html) vai consumir a API /activities/create via JS.
    """
    # 1. Segurança
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    # 2. Renderização
    return render_template('academia/settings.html')