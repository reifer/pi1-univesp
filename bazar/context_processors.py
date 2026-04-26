from urllib.parse import quote

from django.conf import settings


def whatsapp_context(request):
    """Expõe a URL dinâmica do WhatsApp para os templates globais."""
    numero = getattr(settings, 'WHATSAPP_NUMERO', '').strip()
    mensagem = getattr(settings, 'WHATSAPP_MENSAGEM_PADRAO', '').strip()

    if not numero or not mensagem:
        return {'WHATSAPP_URL': ''}

    return {
        'WHATSAPP_URL': f'https://wa.me/{numero}?text={quote(mensagem)}',
    }