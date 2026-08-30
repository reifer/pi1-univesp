import io
import traceback
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime
from pathlib import Path
from unittest.mock import patch
from unittest.runner import TextTestResult

import django
from django.conf import settings
from django.test.runner import DiscoverRunner


class ResultadoAuditoriaPTBR(TextTestResult):
    """Resultado customizado que captura detalhes completos por teste."""

    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.testes_resultados = []
        self._inicio_teste = None

    def _write_status(self, test, status):
        if status in {"FAIL", "ERROR"}:
            status = "FALHA"
        super()._write_status(test, status)

    def startTest(self, test):
        super().startTest(test)
        self._inicio_teste = datetime.now()

    def _base_info(self, test):
        tempo = 0.0
        if self._inicio_teste is not None:
            tempo = (datetime.now() - self._inicio_teste).total_seconds()

        return {
            "id": test.id(),
            "nome": getattr(test, "_testMethodName", str(test)),
            "classe": test.__class__.__name__,
            "objetivo": test.shortDescription() or "Sem objetivo documentado.",
            "tempo": tempo,
        }

    def addSuccess(self, test):
        super().addSuccess(test)
        info = self._base_info(test)
        info.update({"resultado": "SUCESSO", "icone": "✅", "traceback": ""})
        self.testes_resultados.append(info)

    def addFailure(self, test, err):
        super().addFailure(test, err)
        info = self._base_info(test)
        info.update(
            {
                "resultado": "FALHA",
                "icone": "❌",
                "traceback": self._exc_info_to_string(err, test),
            }
        )
        self.testes_resultados.append(info)

    def addError(self, test, err):
        super().addError(test, err)
        info = self._base_info(test)
        info.update(
            {
                "resultado": "FALHA",
                "icone": "❌",
                "traceback": self._exc_info_to_string(err, test),
            }
        )
        self.testes_resultados.append(info)

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        info = self._base_info(test)
        info.update(
            {
                "resultado": "PULADO",
                "icone": "⏭️",
                "traceback": f"Teste pulado: {reason}",
            }
        )
        self.testes_resultados.append(info)


class ExecutorDeTestesAuditoria(DiscoverRunner):
    """Runner de auditoria: terminal limpo, relatório markdown e retenção."""

    resultclass = ResultadoAuditoriaPTBR

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._resultado_execucao = None
        self._buffer_execucao = io.StringIO()

    def run_suite(self, suite, **kwargs):
        """Executa a suíte com stream capturado e mantém referência do resultado."""
        runner_kwargs = self.get_test_runner_kwargs()
        runner_kwargs.update(kwargs)
        runner_kwargs["stream"] = self._buffer_execucao
        runner_kwargs["resultclass"] = self.resultclass

        runner = self.test_runner(**runner_kwargs)
        self._resultado_execucao = runner.run(suite)
        return self._resultado_execucao

    def run_tests(self, test_labels, extra_tests=None, **kwargs):
        """Silencia terminal, executa testes e gera relatório em logs_testes/."""
        logs_dir = Path(settings.BASE_DIR) / "logs_testes"
        logs_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%d%m%y_%H%M%S")
        caminho_relatorio = logs_dir / f"TESTE_{timestamp}.md"

        print("Iniciando testes...")
        print("Processando auditoria...")

        captura_global = io.StringIO()
        erro_inesperado = ""
        quantidade_falhas = 1
        tempo_inicio = datetime.now()

        with patch("sys.stdout", captura_global), patch("sys.stderr", captura_global), redirect_stdout(captura_global), redirect_stderr(captura_global):
            try:
                quantidade_falhas = super().run_tests(test_labels, extra_tests=extra_tests, **kwargs)
            except BaseException:
                erro_inesperado = traceback.format_exc()
                quantidade_falhas = 1

        tempo_total = (datetime.now() - tempo_inicio).total_seconds()

        self._gerar_relatorio_markdown(
            caminho_relatorio=caminho_relatorio,
            timestamp=timestamp,
            tempo_total=tempo_total,
            buffer_global=captura_global.getvalue(),
            erro_inesperado=erro_inesperado,
        )
        self._limpar_historico_logs(logs_dir)

        print("OK" if quantidade_falhas == 0 else "FALHA")
        return quantidade_falhas

    def _gerar_relatorio_markdown(self, caminho_relatorio, timestamp, tempo_total, buffer_global, erro_inesperado):
        resultado = self._resultado_execucao
        testes = resultado.testes_resultados if resultado is not None else []

        total = len(testes)
        sucessos = sum(1 for t in testes if t["resultado"] == "SUCESSO")
        falhas = sum(1 for t in testes if t["resultado"] == "FALHA")
        pulados = sum(1 for t in testes if t["resultado"] == "PULADO")
        testes_com_falha = [
            (indice, teste)
            for indice, teste in enumerate(testes, start=1)
            if teste["resultado"] == "FALHA"
        ]

        db_engine = settings.DATABASES["default"]["ENGINE"]
        data_execucao = datetime.now()

        linhas = [
            "# 📋 Relatório de Auditoria de Testes\n",
            "\n",
            "## 🧾 Metadados\n",
            f"- **Data:** {data_execucao.strftime('%d/%m/%Y')}\n",
            f"- **Hora:** {data_execucao.strftime('%H:%M:%S')}\n",
            f"- **Timestamp:** {timestamp}\n",
            f"- **Versão Django:** {django.get_version()}\n",
            f"- **Banco de Dados:** {db_engine}\n",
            "\n",
            "## 📊 Resumo da Execução\n",
            "| Total Testes | Sucessos | Falhas | Pulados | Tempo |\n",
            "|---|---|---|---|---|\n",
            f"| {total} | {sucessos} | {falhas} | {pulados} | {tempo_total:.3f}s |\n",
            "\n",
            "## 🔎 Detalhamento dos Testes\n",
            "\n",
        ]

        if testes:
            linhas.append("<a id=\"indice-testes\"></a>\n")
            linhas.append("## 🗂️ Índice dos Testes\n")
            linhas.append("\n")
            for indice, teste in enumerate(testes, start=1):
                linhas.append(f"- [{indice}. {teste['nome']}](#teste-{indice})\n")
            linhas.append("\n")

        if testes_com_falha:
            linhas.append("## 🚨 Painel de Falhas\n")
            linhas.append("\n")
            for indice, teste in testes_com_falha:
                linhas.append(f"- [{teste['nome']}](#teste-{indice})\n")
            linhas.append("\n")

        if not testes:
            linhas.append("Nenhum resultado individual foi capturado.\n\n")

        for indice, teste in enumerate(testes, start=1):
            linhas.append(f"<a id=\"teste-{indice}\"></a>\n")
            linhas.append(f"### {indice}. {teste['id']}\n")
            linhas.append(f"- **Nome do Teste:** {teste['nome']}\n")
            linhas.append(f"- **Objetivo:** {teste['objetivo']}\n")
            linhas.append(f"- **Resultado:** {teste['icone']} {teste['resultado']}\n")
            linhas.append(f"- **Tempo:** {teste['tempo']:.3f}s\n")
            linhas.append("- [Voltar ao índice](#indice-testes)\n")
            linhas.append("- **Logs Técnicos:**\n")
            if teste["traceback"]:
                linhas.append("```text\n")
                linhas.append(f"{teste['traceback'].rstrip()}\n")
                linhas.append("```\n")
            else:
                linhas.append("```text\nSem traceback (execução bem-sucedida).\n```\n")
            linhas.append("\n")

        if erro_inesperado:
            linhas.append("## ❗ Erro Inesperado no Runner\n")
            linhas.append("```text\n")
            linhas.append(f"{erro_inesperado.rstrip()}\n")
            linhas.append("```\n\n")

        if buffer_global.strip():
            linhas.append("## 📦 Log Capturado da Execução (silenciado no terminal)\n")
            linhas.append("```text\n")
            linhas.append(f"{buffer_global.rstrip()}\n")
            linhas.append("```\n")

        caminho_relatorio.write_text("".join(linhas), encoding="utf-8")

    def _limpar_historico_logs(self, logs_dir):
        """Mantém apenas os 3 relatórios mais recentes em logs_testes/."""
        arquivos = sorted(
            logs_dir.glob("TESTE_*.md"),
            key=lambda arquivo: arquivo.stat().st_ctime,
            reverse=True,
        )

        for arquivo_antigo in arquivos[3:]:
            arquivo_antigo.unlink(missing_ok=True)


