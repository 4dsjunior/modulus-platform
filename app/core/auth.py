from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from supabase import create_client, Client
import os
import gotrue.errors

auth_bp = Blueprint('auth', __name__)

supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")
try:
    supabase: Client = create_client(supabase_url, supabase_key)
except:
    supabase = None

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            # 1. Autenticação Supabase
            auth_response = supabase.auth.sign_in_with_password({"email": email, "password": password})
            user = auth_response.user

            session.clear()
            session.permanent = True
            session['user_id'] = user.id
            session['user_email'] = user.email
            session['access_token'] = auth_response.session.access_token

            # 2. Check Superadmin (Prioridade 1)
            profile_resp = supabase.table('profiles').select('is_super_admin').eq('id', user.id).maybe_single().execute()
            
            if profile_resp.data and profile_resp.data.get('is_super_admin') is True:
                session['is_super_admin'] = True
                session['role'] = 'super_admin'
                return redirect(url_for('admin.gerenciar_clientes'))

            # 3. Mapeamento de Contextos para Clientes
            # Busca todas as unidades e módulos ativos de uma só vez
            rpc_query = supabase.table('tenant_members')\
                .select('tenant_id, role, tenants(name, tenant_modules(module_id, modules(name))))')\
                .eq('user_id', user.id)\
                .execute()

            raw_data = rpc_query.data
            if not raw_data:
                flash('Sua conta não possui unidades vinculadas.', 'warning')
                return redirect(url_for('auth.login'))

            # Organiza o mapa de contextos para o Sidebar
            user_contexts = []
            for item in raw_data:
                tenant_id = item['tenant_id']
                tenant_name = item['tenants']['name']
                role = item['role']
                
                for mod_rel in item['tenants']['tenant_modules']:
                    user_contexts.append({
                        'tenant_id': tenant_id,
                        'tenant_name': tenant_name,
                        'module_id': mod_rel['module_id'],
                        'module_name': mod_rel['modules']['name'],
                        'role': role
                    })

            if not user_contexts:
                flash('Nenhum módulo ativo encontrado para suas unidades.', 'info')
                return redirect(url_for('auth.login'))

            # Guarda a lista completa para os dropdowns do Sidebar
            session['user_contexts'] = user_contexts
            session['role'] = 'cliente' # Default role para cliente

            # Lógica de Pré-seleção (Caso único)
            if len(user_contexts) == 1:
                ctx = user_contexts[0]
                session['tenant_id'] = ctx['tenant_id']
                session['tenant_name'] = ctx['tenant_name']
                session['module_id'] = ctx['module_id']
                return redirect(url_for(f"{ctx['module_id']}.dashboard"))

            # Caso múltiplos: Vai para o dashboard mas sem tenant/module selecionado (Estado Neutro)
            session['tenant_id'] = None
            session['module_id'] = None
            return redirect(url_for('academia.dashboard'))

        except Exception as e:
            print(f"Erro Login: {e}")
            flash("Falha na autenticação.", 'error')

    return render_template('login.html')

@auth_bp.route('/set_context', methods=['POST'])
def set_context():
    """Rota chamada pelo Sidebar para trocar de Unidade ou Módulo"""
    data = request.get_json()
    t_id = data.get('tenant_id')
    m_id = data.get('module_id')
    
    # Validação de segurança: Verifica se o contexto escolhido está na lista permitida
    allowed = session.get('user_contexts', [])
    valid_ctx = next((c for c in allowed if c['tenant_id'] == t_id and c['module_id'] == m_id), None)
    
    if valid_ctx:
        session['tenant_id'] = valid_ctx['tenant_id']
        session['tenant_name'] = valid_ctx['tenant_name']
        session['module_id'] = valid_ctx['module_id']
        return jsonify({"success": True, "redirect": url_for(f"{m_id}.dashboard")})
    
    return jsonify({"success": False, "error": "Contexto inválido"}), 403

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))