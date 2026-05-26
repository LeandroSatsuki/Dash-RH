from __future__ import annotations

import streamlit as st

from operational_app.common import db_session, format_currency, safe_run, show_warning
from src.crud import beneficios as crud_beneficios
from src.crud import colaboradores as crud_colaboradores


BENEFICIOS_PADRAO = ["vale_refeicao", "vale_alimentacao", "vale_transporte", "plano_saude", "plano_odontologico", "seguro_vida", "cesta_basica", "auxilio_combustivel", "ajuda_custo"]


def render(user: dict):
    st.subheader("Beneficios")
    cadastro_tab, vinculo_tab, analise_tab = st.tabs(["Cadastro", "Vinculos", "Analise"])
    with cadastro_tab:
        with st.form("novo_beneficio"):
            nome = st.selectbox("Nome", BENEFICIOS_PADRAO)
            tipo = st.text_input("Tipo", value="beneficio")
            operadora = st.text_input("Operadora")
            salvar = st.form_submit_button("Cadastrar beneficio")
        if salvar:
            safe_run(
                lambda: _criar_beneficio(user, nome, tipo, operadora),
                success_message="Beneficio cadastrado.",
                error_prefix="Nao foi possivel cadastrar beneficio.",
            )
    with vinculo_tab:
        with db_session() as db:
            beneficios = crud_beneficios.listar(db)
            colaboradores = crud_colaboradores.listar(db)
            vinculos = crud_beneficios.listar_vinculos(db)
        map_beneficios = {f"{item.id} - {item.nome}": item.id for item in beneficios}
        map_colabs = {f"{item.id} - {item.nome_completo}": item.id for item in colaboradores}
        if not map_beneficios or not map_colabs:
            show_warning("Cadastre beneficios e colaboradores para criar vinculos.")
            return
        with st.form("vinculo_beneficio"):
            colaborador = st.selectbox("Colaborador", list(map_colabs.keys()))
            beneficio = st.selectbox("Beneficio", list(map_beneficios.keys()))
            valor_empresa = st.text_input("Valor empresa", value="0,00")
            valor_colaborador = st.text_input("Valor colaborador", value="0,00")
            dependentes = st.number_input("Dependentes", min_value=0, value=0)
            data_inicio = st.date_input("Data inicio")
            salvar = st.form_submit_button("Vincular beneficio")
        if salvar:
            safe_run(
                lambda: _vincular(user, map_colabs[colaborador], map_beneficios[beneficio], valor_empresa, valor_colaborador, dependentes, data_inicio),
                success_message="Beneficio vinculado.",
                error_prefix="Nao foi possivel vincular beneficio.",
            )
        st.dataframe(
            [
                {
                    "id": item.id,
                    "colaborador_id": item.colaborador_id,
                    "beneficio_id": item.beneficio_id,
                    "valor_empresa": format_currency(item.valor_empresa),
                    "valor_colaborador": format_currency(item.valor_colaborador),
                    "dependentes": item.dependentes,
                    "status": item.status,
                }
                for item in vinculos
            ],
            use_container_width=True,
        )
        ativos = [item for item in vinculos if item.status == "ativo"]
        if ativos:
            vinculo_id = int(st.selectbox("Encerrar vinculo", [f"{item.id} - {item.colaborador_id}/{item.beneficio_id}" for item in ativos]).split(" - ")[0])
            if st.button("Encerrar beneficio"):
                safe_run(lambda: _encerrar(user, vinculo_id), success_message="Beneficio encerrado.")
    with analise_tab:
        with db_session() as db:
            vinculos = crud_beneficios.listar_vinculos(db)
            sem_beneficio = crud_beneficios.colaboradores_sem_beneficio(db, {"vale_refeicao", "vale_alimentacao"})
        custo_total = sum(float(item.valor_empresa or 0) for item in vinculos if item.status == "ativo")
        st.metric("Custo mensal estimado", format_currency(custo_total))
        st.metric("Colaboradores sem beneficio obrigatorio", len(sem_beneficio))


def _criar_beneficio(user, nome, tipo, operadora):
    with db_session() as db:
        crud_beneficios.criar(db, {"nome": nome, "tipo": tipo, "operadora": operadora, "status": "ativo"}, user["id"])


def _vincular(user, colaborador_id, beneficio_id, valor_empresa, valor_colaborador, dependentes, data_inicio):
    with db_session() as db:
        crud_beneficios.vincular_ao_colaborador(
            db,
            {
                "colaborador_id": colaborador_id,
                "beneficio_id": beneficio_id,
                "valor_empresa": valor_empresa,
                "valor_colaborador": valor_colaborador,
                "dependentes": dependentes,
                "data_inicio": data_inicio,
                "status": "ativo",
            },
            user["id"],
        )


def _encerrar(user, vinculo_id):
    with db_session() as db:
        crud_beneficios.encerrar_vinculo(db, vinculo_id, user["id"])
