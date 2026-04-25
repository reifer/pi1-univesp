from django.test.runner import DiscoverRunner
from unittest.runner import TextTestResult


class ResultadoAuditoriaPTBR(TextTestResult):
    def _write_status(self, test, status):
        if status in {'FAIL', 'ERROR'}:
            status = 'FALHA'
        super()._write_status(test, status)


class ExecutorDeTestesAuditoria(DiscoverRunner):
    resultclass = ResultadoAuditoriaPTBR
