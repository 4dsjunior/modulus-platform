from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from app import supabase

academia_bp = Blueprint('academia', __name__, url_prefix='/academia', template_folder='templates')

@academia_bp.before_request
def check_auth():
    if 'user_token' not in session:
        return redirect(url_for('auth.login'))

@academia_bp.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    
    # 1. Verifica se o usuário é Super Admin primeiro
    profile = supabase.table("profiles").select("is_super_admin").eq("id", user_id).single().execute()
    is_admin = profile.data.get('is_super_admin', False) if profile.data else False

    if is_admin:
        # Se for Super Admin, redireciona para a gestão de clientes conforme seu novo fluxo
        return redirect(url_for('admin.gerenciar_clientes'))

    # 2. Se for Cliente (Dono de Academia), busca os dados do Tenant
    member_query = supabase.table("tenant_members")\
        .select("tenant_id, tenants(status)")\
        .eq("user_id", user_id)\
        .execute()
    
    if not member_query.data:
        # Se o cliente não tiver academia vinculada, redireciona para um aviso ou logout
        flash("Sua conta ainda não está vinculada a uma academia. Entre em contato com o suporte.")
        return redirect(url_for('auth.logout'))

    member = member_query.data[0]
    tenant_id = member['tenant_id']
    tenant_status = member['tenants']['status']
    
    # Busca contagem de alunos
    res = supabase.table("students").select("*", count="exact").eq("tenant_id", tenant_id).execute()
    total_alunos = res.count if res.count else 0

    return render_template('academia/dashboard.html', 
                           total_alunos=total_alunos, 
                           tenant_status=tenant_status)