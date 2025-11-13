# 1. Inicie o shell
# python manage.py shell

from django.core.mail import send_mail
from django.conf import settings

def run():
    subject = 'Teste SMTP MailerSend'
    message = 'Teste de conexão SMTP bem-sucedido.'
    # Mude para o seu e-mail de destino
    recipient_list = ['seu_email_de_destino@exemplo.com'] 
    sender_email = settings.DEFAULT_FROM_EMAIL

    try:
        result = send_mail(
            subject,
            message,
            sender_email,
            recipient_list,
            fail_silently=False, 
        )
        
        if result > 0:
            print(f"✅ SUCESSO! E-mail enviado (via MailerSend SMTP). Mensagens: {result}")
        
    except Exception as e:
        print(f"❌ ERRO ao enviar o e-mail: {e}")
        # Se o erro for SMTPAuthenticationError, verifique o EMAIL_HOST_PASSWORD
        # Se o erro for relacionado ao remetente, verifique se o DEFAULT_FROM_EMAIL está verificado no MailerSend.