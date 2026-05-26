from __future__ import annotations

import streamlit as st

from operational_app.common import confirm_action, db_session, safe_run, show_warning
from src.crud import admissoes as crud_admissoes
from src.crud import cargos as crud_cargos
from src.crud import centros_custo as crud_centros
from src.crud import colaboradores as crud_colaboradores
from src.crud import departamentos as crud_departamentos


CHECKLIST_LABELS = [
    "cpf",
    "rg",
    "comprovante_residencia",
    "dados_bancarios",
    "ctps_digital",
    "pis_pasep",
    "exame_admissional",
    "contrato_assinado",
    "ficha_registro",
    "termo_beneficios",
]


def render(user: dict):
    st.subheader("Admissoes")
    cadastro_tab, gestao_tab = st.tabs(["Nova pre-admissao", "Acompanhar"])
    with cadastro_tab:
        with db_session() as db:
            cargos = crud_cargos.listar(db)
            departamentos = crud_departamentos.listar(db)
            centros = crud_centros.listar(db)
        if not cargos or not departamentos or not centros:
            show_warning("Cadastre cargos, departamentos e centros de custo antes de criar admissoes.")
            return
        with st.form("nova_pre_admissao"):
            nome = st.text_input("Nome completo")
            cpf = st.text_input("CPF")
            rg = st.text_input("RG")
            email = st.text_input("E-mail")
            data_admissao = st.date_input("Data de admissao")
            salario = st.text_input("Salario base")
            regime = st.selectbox("Regime contratual", ["CLT", "PJ", "Temporario", "Estagio"])
            cargo_id = st.selectbox("Cargo", {f"{item.id} - {item.nome}": item.id for item in cargos})
            departamento_id = st.selectbox("Departamento", {f"{item.id} - {item.nome}": item.id for item in departamentos})
            centro_custo_id = st.selectbox("Centro de custo", {f"{item.id} - {item.nome}": item.id for item in centros})
            checklist = {item: st.checkbox(item.replace("_", " ").title(), value=item in {"cpf", "rg"}) for item in CHECKLIST_LABELS}
            salvar = st.form_submit_button("Criar pre-admissao")
        if salvar and nome:
            safe_run(
                lambda: _criar_pre_admissao(
                    user,
                    nome,
                    cpf,
                    rg,
                    email,
                    regime,
                    salario,
                    data_admissao,
                    cargo_id,
                    departamento_id,
                    centro_custo_id,
                    checklist,
                ),
                success_message="Pre-admissao criada.",
                error_prefix="Nao foi possivel criar a pre-admissao.",
            )
    with gestao_tab:
        with db_session() as db:
            admissoes = crud_admissoes.listar(db)
            colaboradores = {item.id: item for item in crud_colaboradores.listar(db)}
        st.dataframe(
            [
                {
                    "id": adm.id,
                    "colaborador": colaboradores.get(adm.colaborador_id).nome_completo if colaboradores.get(adm.colaborador_id) else adm.colaborador_id,
                    "data_admissao": adm.data_admissao,
                    "status": adm.status,
                }
                for adm in admissoes
            ],
            use_container_width=True,
        )
        if not admissoes:
            return
        selecionado = st.selectbox("Admissao", [f"{item.id} - {colaboradores.get(item.colaborador_id).nome_completo if colaboradores.get(item.colaborador_id) else item.colaborador_id}" for item in admissoes])
        admissao_id = int(selecionado.split(" - ")[0])
        col1, col2 = st.columns(2)
        if col1.button("Atualizar checklist"):
            safe_run(lambda: _marcar_checklist(user, admissao_id), success_message="Checklist atualizado.")
        if col2.button("Concluir admissao"):
            if confirm_action("Confirmo a conclusao da admissao", f"confirm_admissao_{admissao_id}"):
                safe_run(lambda: _concluir(user, admissao_id), success_message="Admissao concluida.")
        if st.button("Cancelar admissao"):
            if confirm_action("Confirmo o cancelamento da admissao", f"cancel_admissao_{admissao_id}"):
                safe_run(lambda: _cancelar(user, admissao_id), success_message="Admissao cancelada.")


def _criar_pre_admissao(user, nome, cpf, rg, email, regime, salario, data_admissao, cargo_id, departamento_id, centro_custo_id, checklist):
    with db_session() as db:
        crud_admissoes.criar_pre_admissao(
            db,
            {
                "nome_completo": nome,
                "cpf": cpf,
                "rg": rg,
                "email": email,
                "regime_contratual": regime,
                "salario_base": salario,
                "data_admissao": data_admissao,
                "cargo_id": cargo_id,
                "departamento_id": departamento_id,
                "centro_custo_id": centro_custo_id,
            },
            {"data_admissao": data_admissao, "checklist_json": checklist},
            user["id"],
        )


def _marcar_checklist(user, admissao_id):
    with db_session() as db:
        admissao = crud_admissoes.buscar_por_id(db, admissao_id)
        checklist = dict(admissao.checklist_json or {})
        checklist.update({item: True for item in CHECKLIST_LABELS})
        crud_admissoes.editar(db, admissao_id, {"checklist_json": checklist}, user["id"])


def _concluir(user, admissao_id):
    with db_session() as db:
        crud_admissoes.concluir(db, admissao_id, user["id"])


def _cancelar(user, admissao_id):
    with db_session() as db:
        crud_admissoes.cancelar(db, admissao_id, user["id"])
