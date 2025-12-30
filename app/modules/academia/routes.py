from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from supabase import create_client, Client
import os

# ===================================================================
# CONFIGURAÇÃO DE CLIENTES SUPABASE
# ===================================================================

# Cliente Normal (Anon Key) - Respeita RLS para operações de usuário
from app import supabase

# Cliente Admin (Service Role) - Bypass de RLS para verificações de sistema
admin_supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")  # Chave com privilégios de super admin
)

# ===================================================================
# DEFINIÇÃO DO BLUEPRINT
# ===================================================================

academia_bp = Blueprint('academia', __name__, url_prefix='/academia', template_folder='templates')

# ===================================================================
# FUNÇÃO AUXILIAR DE SEGURANÇA
# ===================================================================

def verificar_licenca_tenant(tenant_id):
    """
    Verifica o status da licença do tenant usando Service Role (bypass RLS).
    
    Returns:
        str: 'active', 'suspended', 'archived' ou 'suspended' em caso de erro
    
    Princípio Fail-Safe: Se houver qualquer erro, assume 'suspended' para bloquear acesso.
    """
    if not tenant_id:
        return 'suspended'
    
    try:
        response = admin_supabase.table('tenants')\
            .select('status')\
            .eq('id', tenant_id)\
            .single()\
            .execute()
        
        if response.data:
            status = response.data.get('status', 'suspended')
            print(f"✅ Licença verificada: Tenant {tenant_id} = {status}")
            return status
        else:
            print(f"⚠️ Tenant {tenant_id} não encontrado no banco.")
            return 'suspended'
            
    except Exception as e:
        print(f"❌ ERRO CRÍTICO ao verificar licença do tenant {tenant_id}: {e}")
        # Fail-Safe: Bloqueia acesso em caso de erro
        return 'suspended'

# ===================================================================
# ROTAS PRINCIPAIS
# ===================================================================

@academia_bp.route('/dashboard')
def dashboard():
    """
    Renderiza o Dashboard principal do módulo Academia.
    """
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    # Contexto placeholder (será populado com dados reais nas próximas fases)
    context = {
        'total_alunos': 0,        
        'receita_prevista': 0.00, 
        'inadimplencia': 0.00
    }

    return render_template('academia/dashboard.html', **context)


@academia_bp.route('/alunos')
def gerenciar_alunos():
    """
    Lista todos os alunos da unidade (tenant) selecionada.
    
    SEGURANÇA:
    - Verifica status da licença usando Service Role (bypass RLS)
    - Bloqueia interface se licença estiver suspensa ou inativa
    - Busca alunos respeitando RLS (somente do tenant do usuário)
    """
    # 1. Validação de Autenticação
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    # 2. Validação de Contexto (Tenant selecionado)
    tenant_id = session.get('tenant_id')
    if not tenant_id:
        flash("Selecione uma unidade para continuar.", "warning")
        return redirect(url_for('academia.dashboard'))

    # 3. Verificação de Licença (SOLUÇÃO DO ERRO PGRST116)
    tenant_status = verificar_licenca_tenant(tenant_id)

    # 4. Busca de Alunos (Cliente Normal - Respeita RLS)
    students = []
    try:
        resp_students = supabase.table('students')\
            .select('*')\
            .eq('tenant_id', tenant_id)\
            .execute()
        
        students = resp_students.data if resp_students.data else []
        print(f"📊 Encontrados {len(students)} alunos para o tenant {tenant_id}")
        
    except Exception as e:
        print(f"❌ Erro ao buscar alunos: {e}")
        flash("Erro ao carregar lista de alunos.", "danger")

    # 5. Renderização
    return render_template('academia/alunos.html', 
                         students=students, 
                         tenant_status=tenant_status)


# ===================================================================
# ROTAS DE AÇÃO (CRUD DE ALUNOS)
# ===================================================================

@academia_bp.route('/alunos/novo', methods=['GET', 'POST'])
def form_aluno():
    """
    Formulário de cadastro de novo aluno.
    
    TODO: Implementar lógica de INSERT no Supabase na Fase 3.
    """
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    tenant_id = session.get('tenant_id')
    if not tenant_id:
        flash("Selecione uma unidade para continuar.", "warning")
        return redirect(url_for('academia.dashboard'))
    
    # Verifica licença antes de permitir cadastro
    tenant_status = verificar_licenca_tenant(tenant_id)
    if tenant_status != 'active':
        flash("Sua licença está suspensa. Não é possível cadastrar alunos.", "error")
        return redirect(url_for('academia.gerenciar_alunos'))
    
    if request.method == 'POST':
        # TODO: Implementar INSERT
        # Por enquanto, simula sucesso
        flash("Cadastro de aluno simulado com sucesso.", "success")
        return redirect(url_for('academia.gerenciar_alunos'))

    return render_template('academia/form_aluno.html')


@academia_bp.route('/alunos/suspender/<student_id>', methods=['POST'])
def suspender_aluno(student_id):
    """
    Suspende um aluno (muda status para 'suspenso').
    
    TODO: Implementar lógica de UPDATE no Supabase na Fase 3.
    """
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    tenant_id = session.get('tenant_id')
    if not tenant_id:
        flash("Contexto inválido.", "error")
        return redirect(url_for('academia.dashboard'))
    
    # Verifica licença
    tenant_status = verificar_licenca_tenant(tenant_id)
    if tenant_status != 'active':
        flash("Sua licença está suspensa. Não é possível realizar alterações.", "error")
        return redirect(url_for('academia.gerenciar_alunos'))

    try:
        # TODO: Descomentar quando implementar UPDATE
        # supabase.table('students').update({'status': 'suspenso'}).eq('id', student_id).execute()
        flash(f"Aluno suspenso com sucesso.", "success")
    except Exception as e:
        print(f"❌ Erro ao suspender aluno: {e}")
        flash(f"Erro ao suspender aluno: {e}", "danger")

    return redirect(url_for('academia.gerenciar_alunos'))


# ===================================================================
# ROTA DE CONFIGURAÇÕES
# ===================================================================

@academia_bp.route('/configuracoes')
def settings():
    """
    Página de configurações da unidade (modalidades, planos, etc).
    """
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    tenant_id = session.get('tenant_id')
    if not tenant_id:
        flash("Selecione uma unidade para continuar.", "warning")
        return redirect(url_for('academia.dashboard'))
    
    return render_template('academia/settings.html')