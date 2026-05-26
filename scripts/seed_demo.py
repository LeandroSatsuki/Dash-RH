from __future__ import annotations

import os
import random
import sys
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sqlalchemy import select

from src.crud import admissoes as crud_admissoes
from src.crud import afastamentos as crud_afastamentos
from src.crud import beneficios as crud_beneficios
from src.crud import banco_horas as crud_banco_horas
from src.crud import cargos as crud_cargos
from src.crud import centros_custo as crud_centros
from src.crud import colaboradores as crud_colaboradores
from src.crud import departamentos as crud_departamentos
from src.crud import desligamentos as crud_desligamentos
from src.crud import documentos_obrigatorios as crud_documentos_obrigatorios
from src.crud import ferias as crud_ferias
from src.crud import folha as crud_folha
from src.crud import jornadas as crud_jornadas
from src.crud import ponto as crud_ponto
from src.crud import sst as crud_sst
from src.db.database import SessionLocal
from src.db.init_db import init_db
from src.db.models import Auditoria, Beneficio, Colaborador, Documento, Empresa
from src.services import alerts
from src.services.audit_service import log_action
from src.services.file_storage import save_upload
from src.utils.config import is_production


def ensure_not_production() -> None:
    if is_production():
        raise RuntimeError("O seed demo e bloqueado em producao.")


def fake_cpf(index: int) -> str:
    return f"{90000000000 + index:011d}"


def seed_demo() -> dict:
    ensure_not_production()
    random.seed(42)
    init_db()
    summary = {}
    with SessionLocal() as db:
        if db.scalar(select(Empresa).limit(1)) is None:
            empresa = Empresa(razao_social="Empresa Demo RH LTDA", nome_fantasia="Demo RH", cnpj="00000000000000", status="ativa")
            db.add(empresa)
            db.commit()
            db.refresh(empresa)
        departamentos = _ensure_departamentos(db)
        cargos = _ensure_cargos(db, departamentos)
        centros = _ensure_centros(db)
        colaboradores = _ensure_colaboradores(db, cargos, departamentos, centros)
        jornadas = _ensure_jornadas(db)
        _ensure_vinculos_jornada(db, colaboradores, jornadas)
        _ensure_admissoes(db, colaboradores[:5])
        _ensure_ferias(db, colaboradores[5:13])
        _ensure_afastamentos(db, colaboradores[13:18])
        beneficios = _ensure_beneficios(db)
        _ensure_vinculos(db, colaboradores[:15], beneficios)
        competencias = _ensure_competencias(db)
        _ensure_folha(db, colaboradores[:10], competencias)
        _ensure_ponto(db, colaboradores[:12])
        _ensure_banco_horas(db, colaboradores[:10])
        _ensure_documentos_obrigatorios(db)
        _ensure_desligamentos(db, colaboradores[20:23])
        _ensure_documentos(db, colaboradores[:5])
        _ensure_sst(db, colaboradores[:10])
        alerts.gerar_alertas(db)
        log_action(db, tabela="seed_demo", acao="seed_demo", usuario_id=1, origem="scripts", valor_novo={"status": "ok"})
        summary = {
            "departamentos": len(departamentos),
            "cargos": len(cargos),
            "centros_custo": len(centros),
            "colaboradores": len(colaboradores),
            "jornadas": len(jornadas),
            "beneficios": len(beneficios),
            "competencias": len(competencias),
        }
    return summary


def _ensure_departamentos(db):
    existentes = crud_departamentos.listar(db)
    nomes = ["Operacoes", "Gente", "Financeiro", "Tecnologia", "Comercial"]
    existentes_nomes = {item.nome for item in existentes}
    for nome in nomes:
        if nome not in existentes_nomes:
            existentes.append(crud_departamentos.criar(db, {"nome": nome, "status": "ativo"}, 1))
    return existentes


def _ensure_cargos(db, departamentos):
    existentes = crud_cargos.listar(db)
    nomes = ["Analista Jr", "Analista Pl", "Analista Sr", "Assistente", "Coordenador", "Supervisor", "Especialista", "Auxiliar", "Consultor", "Gestor"]
    existentes_nomes = {item.nome for item in existentes}
    resultado = existentes[:]
    for idx, nome in enumerate(nomes, start=len(existentes) + 1):
        if nome in existentes_nomes:
            continue
        dept = departamentos[(idx - 1) % len(departamentos)]
        resultado.append(crud_cargos.criar(db, {"nome": nome, "departamento_id": dept.id, "status": "ativo"}, 1))
    return resultado


def _ensure_centros(db):
    existentes = crud_centros.listar(db)
    existentes_codigos = {item.codigo for item in existentes}
    resultado = existentes[:]
    for idx in range(1, 6):
        if f"CC{idx:03d}" in existentes_codigos:
            continue
        resultado.append(crud_centros.criar(db, {"codigo": f"CC{idx:03d}", "nome": f"Centro {idx}", "area": "Area Demo", "subarea": f"Subarea {idx}"}, 1))
    return resultado


def _ensure_colaboradores(db, cargos, departamentos, centros):
    existentes = crud_colaboradores.listar(db)
    if len(existentes) >= 30:
        return existentes
    resultado = existentes[:]
    for idx in range(len(existentes) + 1, 31):
        dept = departamentos[(idx - 1) % len(departamentos)]
        cargo = cargos[(idx - 1) % len(cargos)]
        centro = centros[(idx - 1) % len(centros)]
        resultado.append(
            crud_colaboradores.criar(
                db,
                {
                    "matricula": f"DEMO{idx:03d}",
                    "nome_completo": f"Colaborador Demo {idx:02d}",
                    "cpf": fake_cpf(idx),
                    "email": f"demo{idx:02d}@example.test",
                    "telefone": f"1199999{idx:04d}"[-11:],
                    "regime_contratual": "CLT" if idx % 3 else "PJ",
                    "data_admissao": date.today() - timedelta(days=30 * idx),
                    "cargo_id": cargo.id,
                    "departamento_id": dept.id,
                    "centro_custo_id": centro.id,
                    "salario_base": Decimal("2000.00") + Decimal(idx * 100),
                    "status": "ativo",
                    "origem": "manual",
                },
                1,
            )
        )
    return resultado


def _ensure_admissoes(db, colaboradores):
    for idx, colaborador in enumerate(colaboradores, start=1):
        if colaborador.status != "pre_admissao":
            crud_colaboradores.editar(db, colaborador.id, {"status": "pre_admissao", "data_admissao": None}, 1)
        if not list(filter(lambda item: item.colaborador_id == colaborador.id, crud_admissoes.listar(db))):
            crud_admissoes.criar(
                db,
                {
                    "colaborador_id": colaborador.id,
                    "data_admissao": date.today() + timedelta(days=idx),
                    "checklist_json": {"cpf": True, "rg": True},
                },
                1,
            )


def _ensure_ferias(db, colaboradores):
    for idx, colaborador in enumerate(colaboradores, start=1):
        if not any(item.colaborador_id == colaborador.id for item in crud_ferias.listar(db)):
            crud_ferias.criar(
                db,
                {
                    "colaborador_id": colaborador.id,
                    "periodo_aquisitivo_inicio": date.today() - timedelta(days=365),
                    "periodo_aquisitivo_fim": date.today(),
                    "data_limite_gozo": date.today() + timedelta(days=90 - idx * 5),
                    "dias_direito": 30,
                    "dias_gozados": 10,
                    "dias_restantes": 20,
                    "data_inicio": date.today() + timedelta(days=idx),
                    "data_fim": date.today() + timedelta(days=idx + 9),
                    "status": "planejada" if idx % 2 else "aprovada",
                },
                1,
            )


def _ensure_afastamentos(db, colaboradores):
    for idx, colaborador in enumerate(colaboradores, start=1):
        if not any(item.colaborador_id == colaborador.id for item in crud_afastamentos.listar(db)):
            crud_afastamentos.criar(
                db,
                {
                    "colaborador_id": colaborador.id,
                    "tipo": random.choice(["atestado_medico", "inss", "falta_justificada", "licenca_paternidade"]),
                    "data_inicio": date.today() - timedelta(days=idx * 3),
                    "data_fim": date.today() - timedelta(days=idx * 3 - 2),
                    "impacta_folha": True,
                    "impacta_absenteismo": True,
                    "cid_mascarado": f"CID-DEMO-{idx}",
                    "status": "ativo" if idx % 2 else "encerrado",
                },
                1,
            )


def _ensure_beneficios(db):
    existentes = crud_beneficios.listar(db)
    nomes = ["vale_refeicao", "vale_alimentacao", "vale_transporte", "plano_saude", "seguro_vida", "ajuda_custo"]
    for nome in nomes:
        if not any(item.nome == nome for item in existentes):
            existentes.append(crud_beneficios.criar(db, {"nome": nome, "tipo": "beneficio", "status": "ativo"}, 1))
    return existentes


def _ensure_vinculos(db, colaboradores, beneficios):
    vinculos = crud_beneficios.listar_vinculos(db)
    for idx, colaborador in enumerate(colaboradores, start=1):
        if any(item.colaborador_id == colaborador.id for item in vinculos):
            continue
        beneficio = beneficios[(idx - 1) % len(beneficios)]
        crud_beneficios.vincular_ao_colaborador(
            db,
            {
                "colaborador_id": colaborador.id,
                "beneficio_id": beneficio.id,
                "data_inicio": date.today() - timedelta(days=30),
                "valor_empresa": "250,00",
                "valor_colaborador": "50,00",
                "dependentes": idx % 3,
                "status": "ativo",
            },
            1,
        )


def _ensure_competencias(db):
    existentes = crud_folha.listar_competencias(db)
    alvo = [(2026, 1), (2026, 2)]
    for ano, mes in alvo:
        competencia = f"{ano:04d}-{mes:02d}"
        if not any(item.competencia == competencia for item in existentes):
            existentes.append(crud_folha.criar_competencia(db, {"ano": ano, "mes": mes, "competencia": competencia, "status": "aberta"}, 1))
    return existentes


def _ensure_jornadas(db):
    jornadas = crud_jornadas.listar_jornadas(db)
    if jornadas:
        return jornadas
    specs = [
        ("Administrativo 44h", "08:00", "12:00", "13:00", "17:00"),
        ("Comercial 44h", "08:30", "12:00", "13:00", "17:30"),
        ("Operacao 12x36", "07:00", None, None, "19:00"),
    ]
    resultado = []
    for nome, entrada, saida_intervalo, retorno_intervalo, saida in specs:
        jornada = crud_jornadas.criar_jornada(
            db,
            {
                "nome": nome,
                "descricao": f"Escala demo {nome}",
                "carga_horaria_semanal": "44",
                "carga_horaria_diaria": "8",
                "tolerancia_entrada_minutos": 10,
                "tolerancia_saida_minutos": 10,
                "intervalo_minimo_minutos": 60,
                "ativo": True,
            },
            1,
        )
        for dia in range(5):
            crud_jornadas.criar_turno(
                db,
                jornada.id,
                {
                    "dia_semana": dia,
                    "hora_entrada": entrada,
                    "hora_saida_intervalo": saida_intervalo,
                    "hora_retorno_intervalo": retorno_intervalo,
                    "hora_saida": saida,
                    "descanso": False,
                },
                1,
            )
        crud_jornadas.criar_turno(db, jornada.id, {"dia_semana": 5, "descanso": True}, 1)
        crud_jornadas.criar_turno(db, jornada.id, {"dia_semana": 6, "descanso": True}, 1)
        resultado.append(jornada)
    return resultado


def _ensure_vinculos_jornada(db, colaboradores, jornadas):
    for idx, colaborador in enumerate(colaboradores, start=1):
        if crud_jornadas.jornada_atual_colaborador(db, colaborador.id):
            continue
        jornada = jornadas[(idx - 1) % len(jornadas)]
        crud_jornadas.vincular_jornada_colaborador(
            db,
            colaborador.id,
            {"jornada_id": jornada.id, "data_inicio": date.today() - timedelta(days=60), "observacao": "Seed demo"},
            1,
        )


def _ensure_folha(db, colaboradores, competencias):
    rubricas = crud_folha.listar_rubricas(db)
    if not rubricas:
        for codigo, descricao, tipo in [("SALARIO_BASE", "salario_base", "provento"), ("FGTS", "fgts", "encargo"), ("VALE_REFEICAO", "vale_refeicao", "beneficio")]:
            crud_folha.criar_rubrica(db, {"codigo": codigo, "descricao": descricao, "tipo": tipo}, 1)
        rubricas = crud_folha.listar_rubricas(db)
    lancamentos = crud_folha.listar_lancamentos(db)
    if lancamentos:
        return
    for competencia in competencias:
        for colaborador in colaboradores:
            for rubrica in rubricas:
                valor = {"provento": "2500,00", "encargo": "300,00", "beneficio": "150,00"}.get(rubrica.tipo, "0,00")
                crud_folha.criar_lancamento(
                    db,
                    {
                        "competencia_id": competencia.id,
                        "colaborador_id": colaborador.id,
                        "rubrica_id": rubrica.id,
                        "tipo": rubrica.tipo,
                        "valor": valor,
                        "origem": "manual",
                    },
                    1,
                )


def _ensure_ponto(db, colaboradores):
    if crud_ponto.listar_marcacoes(db):
        return
    for idx, colaborador in enumerate(colaboradores, start=1):
        data_ref = date.today() - timedelta(days=idx % 5)
        crud_ponto.criar_marcacao(db, {"colaborador_id": colaborador.id, "data": data_ref, "tipo": "entrada", "horario": "08:00", "origem": "manual"}, 1)
        if idx % 4 != 0:
            crud_ponto.criar_marcacao(db, {"colaborador_id": colaborador.id, "data": data_ref, "tipo": "saida_intervalo", "horario": "12:00", "origem": "manual"}, 1)
            crud_ponto.criar_marcacao(db, {"colaborador_id": colaborador.id, "data": data_ref, "tipo": "retorno_intervalo", "horario": "13:00", "origem": "manual"}, 1)
            crud_ponto.criar_marcacao(db, {"colaborador_id": colaborador.id, "data": data_ref, "tipo": "saida", "horario": "17:00" if idx % 3 else "18:00", "origem": "manual"}, 1)
    crud_ponto.apurar_periodo(db, data_inicio=date.today() - timedelta(days=5), data_fim=date.today(), usuario_id=1, atualizar_banco_horas=False)


def _ensure_banco_horas(db, colaboradores):
    if crud_banco_horas.listar_movimentos(db):
        return
    for idx, colaborador in enumerate(colaboradores, start=1):
        crud_banco_horas.criar_movimento(
            db,
            {
                "colaborador_id": colaborador.id,
                "data": date.today() - timedelta(days=idx),
                "origem": "ajuste_manual",
                "tipo": "credito" if idx % 2 else "debito",
                "horas": "1,50",
                "descricao": "Movimento demo banco de horas",
            },
            1,
        )


def _ensure_documentos_obrigatorios(db):
    tipos = crud_documentos_obrigatorios.listar_tipos_documento(db)
    if not tipos:
        tipos = [
            crud_documentos_obrigatorios.criar_tipo_documento(db, {"nome": "rg", "ativo": True}, 1),
            crud_documentos_obrigatorios.criar_tipo_documento(db, {"nome": "aso", "sensivel": True, "exige_validade": True, "ativo": True}, 1),
        ]
    if not crud_documentos_obrigatorios.listar_regras(db):
        for tipo in tipos:
            crud_documentos_obrigatorios.criar_regra(
                db,
                {"tipo_documento_id": tipo.id, "regime_contratual": "CLT", "obrigatorio": True, "validade_dias": 365},
                1,
            )
    crud_documentos_obrigatorios.gerar_pendencias(db, 1)


def _ensure_desligamentos(db, colaboradores):
    for idx, colaborador in enumerate(colaboradores, start=1):
        existentes = crud_desligamentos.listar(db)
        if any(item.colaborador_id == colaborador.id for item in existentes):
            continue
        desligamento = crud_desligamentos.criar(
            db,
            {
                "colaborador_id": colaborador.id,
                "data_aviso_previo": date.today() - timedelta(days=10),
                "data_desligamento": date.today() + timedelta(days=idx),
                "tipo_rescisao": "pedido_demissao",
                "status": "rascunho",
            },
            1,
        )
        if idx == 1:
            crud_desligamentos.concluir(db, desligamento.id, 1)


def _ensure_documentos(db, colaboradores):
    if db.scalar(select(Documento).limit(1)) is not None:
        return
    for idx, colaborador in enumerate(colaboradores, start=1):
        saved = save_upload(f"documento_demo_{idx}.pdf", f"documento demo {idx}".encode("utf-8"))
        documento = Documento(
            colaborador_id=colaborador.id,
            tipo_documento="documento_demo",
            nome_original=saved["nome_original"],
            nome_armazenado=saved["nome_armazenado"],
            caminho_arquivo=saved["caminho_arquivo"],
            hash_arquivo=saved["hash_arquivo"],
            status="ativo",
            usuario_upload_id=1,
        )
        db.add(documento)
    db.commit()


def _ensure_sst(db, colaboradores):
    if crud_sst.listar_epis(db):
        return
    epi = crud_sst.criar_epi(db, {"nome": "Capacete Demo", "ca": "CA-DEMO-001", "validade_ca": date.today() - timedelta(days=10), "ativo": True}, 1)
    treinamento = crud_sst.criar_treinamento(db, {"nome": "NR 06 Demo", "validade_meses": 12, "ativo": True}, 1)
    for idx, colaborador in enumerate(colaboradores, start=1):
        crud_sst.criar_exame(
            db,
            {
                "colaborador_id": colaborador.id,
                "tipo_exame": "periodico",
                "data_exame": date.today() - timedelta(days=365),
                "data_validade": date.today() + timedelta(days=30) if idx % 3 else date.today() - timedelta(days=5),
                "clinica": "Clinica Demo",
                "status": "ativo",
            },
            1,
        )
        crud_sst.criar_entrega_epi(db, {"colaborador_id": colaborador.id, "epi_id": epi.id, "data_entrega": date.today() - timedelta(days=30), "quantidade": 1, "status": "ativo"}, 1)
        crud_sst.vincular_treinamento(
            db,
            {
                "colaborador_id": colaborador.id,
                "treinamento_id": treinamento.id,
                "data_realizacao": date.today() - timedelta(days=400),
                "data_validade": date.today() + timedelta(days=60) if idx % 4 else date.today() - timedelta(days=2),
                "status": "ativo",
            },
            1,
        )


if __name__ == "__main__":
    result = seed_demo()
    print(result)
