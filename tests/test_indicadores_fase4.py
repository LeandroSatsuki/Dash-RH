from datetime import date, timedelta

from src.crud import banco_horas as crud_banco_horas
from src.crud import colaboradores as crud_colaboradores
from src.crud import documentos_obrigatorios as crud_docs
from src.crud import jornadas as crud_jornadas
from src.crud import ponto as crud_ponto
from src.crud import sst as crud_sst
from src.services.indicadores import indicadores_operacionais


def test_indicadores_fase4_incluem_ponto_documentos_e_sst(db):
    colaborador = crud_colaboradores.criar(
        db,
        {"nome_completo": "Indicador Demo", "cpf": "90000000042", "regime_contratual": "CLT", "status": "ativo", "salario_base": 1000},
        1,
    )
    jornada = crud_jornadas.criar_jornada(db, {"nome": "Indicador Jornada"}, 1)
    crud_jornadas.criar_turno(db, jornada.id, {"dia_semana": date.today().weekday(), "hora_entrada": "08:00", "hora_saida": "17:00"}, 1)
    crud_jornadas.vincular_jornada_colaborador(db, colaborador.id, {"jornada_id": jornada.id, "data_inicio": date.today() - timedelta(days=1)}, 1)
    crud_ponto.criar_marcacao(db, {"colaborador_id": colaborador.id, "data": date.today(), "tipo": "entrada", "horario": "08:00", "origem": "manual"}, 1)
    crud_ponto.criar_marcacao(db, {"colaborador_id": colaborador.id, "data": date.today(), "tipo": "saida", "horario": "17:30", "origem": "manual"}, 1)
    crud_ponto.apurar_periodo(db, data_inicio=date.today(), data_fim=date.today(), usuario_id=1, atualizar_banco_horas=True)
    tipo = crud_docs.criar_tipo_documento(db, {"nome": "doc_indicador", "ativo": True}, 1)
    crud_docs.criar_regra(db, {"tipo_documento_id": tipo.id, "regime_contratual": "CLT", "obrigatorio": True}, 1)
    crud_docs.gerar_pendencias(db, 1)
    treinamento = crud_sst.criar_treinamento(db, {"nome": "Treinamento", "validade_meses": 12, "ativo": True}, 1)
    crud_sst.vincular_treinamento(db, {"colaborador_id": colaborador.id, "treinamento_id": treinamento.id, "data_realizacao": date.today(), "data_validade": date.today() - timedelta(days=1), "status": "ativo"}, 1)
    indicadores = indicadores_operacionais(db)
    assert "horas_previstas" in indicadores["kpis"]
    assert "documentos_pendentes" in indicadores["kpis"]
    assert "treinamentos_vencidos" in indicadores["kpis"]
    assert "horas_extras_por_departamento" in indicadores["graficos"]
