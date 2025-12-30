from flask import Blueprint, render_template, session, redirect, url_for

# Definição do Blueprint
# url_prefix='/academia' mantém as rotas organizadas sob o mesmo prefixo
academia_bp = Blueprint('academia', __name__, url_prefix='/academia', template_folder='templates')

@academia_bp.route('/dashboard')
def dashboard():
    """
    Renderiza o painel principal (Dashboard) da unidade selecionada.
    """
    # 1. Segurança: Verifica se está logado
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    # 2. Contexto de Dados (Mantido do legado positivo)
    context = {
        'total_alunos': 0,        
        'receita_prevista': 0.00, 
        'inadimplencia': 0.00
    }

    return render_template('academia/dashboard.html', **context)

@academia_bp.route('/alunos')
def gerenciar_alunos():
    """
    Renderiza a lista de alunos. 
    Esta rota é essencial para que o link 'Alunos' no Sidebar funcione.
    """
    # 1. Segurança
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
        
    # 2. Renderização do template correspondente
    return render_template('academia/alunos.html')

@academia_bp.route('/configuracoes')
def settings():
    """
    Renderiza a tela de Configurações.
    """
    # 1. Segurança
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    # 2. Renderização
    return render_template('academia/settings.html')