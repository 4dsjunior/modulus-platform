from flask import Blueprint, request, jsonify, session
from supabase import create_client, Client
import os
import json

# Configuração do Supabase
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")

try:
    if not supabase_url or not supabase_key:
        # Em produção, isso deve impedir o app de rodar se faltar config
        print("CRITICAL: SUPABASE_URL or SUPABASE_KEY not set in environment.")
        supabase = None
    else:
        supabase: Client = create_client(supabase_url, supabase_key)
except Exception as e:
    print(f"Error initializing Supabase client: {e}")
    supabase = None

activities_bp = Blueprint('activities_bp', __name__)

def get_current_tenant_id():
    """
    Recupera o ID do tenant da sessão segura do Flask.
    Retorna None se o usuário não estiver logado.
    """
    return session.get('tenant_id')

@activities_bp.route('/activities/create', methods=['POST'])
def create_activity():
    """
    Cria uma atividade completa (Atividade + Horários + Planos) 
    usando a transação atômica (RPC) definida no banco.
    """
    # 1. Validação de Infraestrutura
    if not supabase:
        return jsonify({"error": "Database connection error"}), 500

    # 2. Validação de Segurança (Sessão)
    tenant_id = get_current_tenant_id()
    if not tenant_id:
        return jsonify({"error": "Unauthorized: Session expired or invalid"}), 401

    # 3. Validação de Entrada (Payload)
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400

    # Mapeamento estrito para os parâmetros da função SQL (RPC)
    # Isso garante que enviamos exatamente o que o banco espera
    rpc_params = {
        "p_tenant_id": tenant_id,
        "p_name": data.get("name"),
        "p_is_active": data.get("is_active", True),
        "p_schedules": data.get("schedules", []),      # Lista de objetos
        "p_pricing_plans": data.get("pricing_plans", []) # Lista de objetos
    }

    try:
        # 4. Execução da Transação Atômica
        # Chama a função 'create_full_activity_transaction' no Supabase
        response = supabase.rpc('create_full_activity_transaction', rpc_params).execute()
        
        # O retorno data contém o ID da atividade criada (definido no SQL)
        new_activity_id = response.data

        return jsonify({
            "message": "Activity created successfully", 
            "activity_id": new_activity_id
        }), 201

    except Exception as e:
        # Captura erros de banco (ex: violação de constraint, erro de tipo)
        print(f"Error in create_activity RPC: {str(e)}")
        return jsonify({"error": f"Failed to save data: {str(e)}"}), 500


@activities_bp.route('/activities', methods=['GET'])
def get_activities():
    """
    Lista todas as atividades do tenant logado, 
    trazendo dados aninhados (schedules e pricing_plans).
    """
    if not supabase:
        return jsonify({"error": "Database connection error"}), 500

    tenant_id = get_current_tenant_id()
    if not tenant_id:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        # Consulta hierárquica (Query Builder)
        # Traz activity_schedules e pricing_plans aninhados no JSON
        response = supabase.table('activities')\
            .select('*, activity_schedules(*), pricing_plans(*)')\
            .eq('tenant_id', tenant_id)\
            .order('name')\
            .execute()

        return jsonify(response.data), 200

    except Exception as e:
        print(f"Error fetching activities: {str(e)}")
        return jsonify({"error": str(e)}), 500