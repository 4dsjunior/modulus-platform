from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from app import supabase
import os
from supabase import create_client

# Instância Admin (Service Role)
admin_supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def log_action(action, target_id, details):
    """Regista acções críticas na tabela audit_logs (Requisito 6.1)"""
    try:
        admin_supabase.table("audit_logs").insert({
            "performed_by": session.get('user_id'),
            "action": action,
            "target_user_id": target_id, # Usado aqui como ID do Alvo (User ou Tenant)
            "details": details
        }).execute()
    except Exception as e:
        print(f"Erro ao gerar log de auditoria: {e}")

@admin_bp.before_request
def restrict_to_superadmin():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    res = supabase.table("profiles").select("is_super_admin").eq("id", session['user_id']).single().execute()
    if not res.data or not res.data.get('is_super_admin'):
        flash("Acesso restrito.")
        return redirect(url_for('academia.dashboard'))

@admin_bp.route('/clientes')
def gerenciar_clientes():
    tenants = admin_supabase.table("tenants").select("*").order("name").execute()
    return render_template('admin/clientes.html', tenants=tenants.data if tenants.data else [])

@admin_bp.route('/clientes/novo', methods=['GET', 'POST'])
def criar_cliente():
    if request.method == 'POST':
        name = request.form.get('name')
        slug = request.form.get('slug')
        module_id = request.form.get('module_id')
        email = request.form.get('email')
        password = request.form.get('password')

        try:
            # 1. Tenant
            t_res = admin_supabase.table("tenants").insert({"name": name, "slug": slug, "status": "active"}).execute()
            if not t_res.data: raise Exception("Falha ao criar Tenant.")
            t_id = t_res.data[0]['id']

            # 2. Auth User
            auth_res = admin_supabase.auth.admin.create_user({
                "email": email, "password": password, "email_confirm": True,
                "user_metadata": {"full_name": name}
            })
            if not auth_res.user: raise Exception("Falha ao criar acesso (Auth).")
            u_id = auth_res.user.id

            # 3. Member & Module (Requisito 3 do Relatório)
            admin_supabase.table("tenant_members").insert({"tenant_id": t_id, "user_id": u_id, "role": "owner"}).execute()
            admin_supabase.table("tenant_modules").insert({"tenant_id": t_id, "module_id": module_id, "is_enabled": True}).execute()

            # 4. Auditoria (Requisito 6.1)
            log_action("CREATE_TENANT", u_id, {"tenant_name": name, "module": module_id})

            flash(f"Sucesso: Academia '{name}' configurada correctamente!") # Requisito 6.3
            return redirect(url_for('admin.gerenciar_clientes')) # Requisito 6.4

        except Exception as e:
            # Requisito 6.4: Retornar erro padronizado
            error_msg = f"Erro na Criação: {str(e)}"
            flash(error_msg)
            return redirect(url_for('admin.criar_cliente'))

    modules_res = supabase.table("modules").select("*").execute()
    return render_template('admin/form_cliente.html', modules=modules_res.data)

@admin_bp.route('/clientes/status/<tenant_id>/<novo_status>', methods=['POST'])
def alterar_status(tenant_id, novo_status):
    """Fluxo Unificado de Suspensão e Reativação (Requisito 6.2)"""
    try:
        # Validação de estado
        valid_status = ['active', 'suspended', 'archived']
        if novo_status not in valid_status:
            raise Exception("Estado inválido.")

        res = admin_supabase.table("tenants").update({"status": novo_status}).eq("id", tenant_id).execute()
        
        if res.data:
            # Auditoria obrigatória
            log_action(f"CHANGE_STATUS_{novo_status.upper()}", None, {"tenant_id": tenant_id})
            flash(f"Status atualizado para {novo_status.upper()} com sucesso.")
        else:
            raise Exception("Tenant não encontrado.")

    except Exception as e:
        flash(f"Erro ao alterar status: {str(e)}")
    
    return redirect(url_for('admin.gerenciar_clientes'))