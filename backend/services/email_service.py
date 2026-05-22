import os
import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from config import Config

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.api_key = os.environ.get('SENDGRID_API_KEY')
        self.from_email = os.environ.get('EMAIL_FROM', 'contato@aureaia.com')
        self.from_name = os.environ.get('EMAIL_FROM_NAME', 'AureaIA')
        
        if self.api_key:
            self.client = SendGridAPIClient(self.api_key)
            logger.info("SendGrid Service Initialized.")
        else:
            self.client = None
            logger.warning("SENDGRID_API_KEY not found. Emails will not be sent.")

    def _send(self, to_email, subject, html_content):
        if not self.client:
            logger.warning(f"Email not sent (no API key): {subject} to {to_email}")
            return False

        message = Mail(
            from_email=(self.from_email, self.from_name),
            to_emails=to_email,
            subject=subject,
            html_content=html_content
        )
        try:
            response = self.client.send(message)
            logger.info(f"Email sent: {subject} to {to_email} (Status: {response.status_code})")
            return True
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False

    def send_welcome(self, to_email, name):
        subject = f"Bem-vinda ao AureaIA, {name.split(' ')[0]}! ✨"
        html = f"""
        <div style="font-family: sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #eee; border-radius: 10px;">
            <h2 style="color: #9857CB;">Sua jornada artística começou!</h2>
            <p>Olá, <strong>{name}</strong>,</p>
            <p>Seja bem-vinda ao <strong>AureaIA</strong>. Seu acesso ao estúdio de fotografia por IA mais avançado do mundo está liberado.</p>
            <p>Bem‑vindo(a) ao <strong>AureaIA</strong>. Seu acesso ao estúdio de fotografia por IA mais avançado do mundo está liberado.</p>
            <div style="margin: 30px 0;">
                <a href="{Config.FRONTEND_URL}/generate" style="background: #9857CB; color: white; padding: 15px 25px; text-decoration: none; border-radius: 5px; font-weight: bold;">Começar meu Ensaio</a>
            </div>
            <p style="color: #666; font-size: 12px;">Se precisar de ajuda, responda a este e-mail.</p>
        </div>
        """
        return self._send(to_email, subject, html)

    def send_generation_complete(self, to_email, job_id):
        subject = "Seu ensaio premium está pronto! 📸"
        html = f"""
        <div style="font-family: sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #eee; border-radius: 10px;">
            <h2 style="color: #9857CB;">A arte foi revelada.</h2>
            <p>Boas notícias! Sua geração de fotos por IA acaba de ser concluída com sucesso.</p>
            <p>Estamos ansiosos para que você veja o resultado final.</p>
            <div style="margin: 30px 0;">
                <a href="{Config.FRONTEND_URL}/history" style="background: #000; color: white; padding: 15px 25px; text-decoration: none; border-radius: 5px; font-weight: bold;">Ver meu Álbum</a>
            </div>
            <p>As imagens ficarão disponíveis para download por 24 horas.</p>
            <p style="color: #666; font-size: 12px;">ID do pedido: {job_id}</p>
        </div>
        """
        return self._send(to_email, subject, html)

    def send_password_reset(self, to_email, reset_link):
        subject = "Recuperação de Senha — AureaIA"
        html = f"""
        <div style="font-family: sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #eee; border-radius: 10px;">
            <h2>Esqueceu sua senha?</h2>
            <p>Recebemos uma solicitação para redefinir a senha da sua conta no AureaIA.</p>
            <p>Clique no botão abaixo para escolher uma nova senha:</p>
            <div style="margin: 30px 0;">
                <a href="{reset_link}" style="background: #9857CB; color: white; padding: 15px 25px; text-decoration: none; border-radius: 5px; font-weight: bold;">Redefinir Senha</a>
            </div>
            <p style="color: #666; font-size: 12px;">Se você não solicitou isso, pode ignorar este e-mail.</p>
        </div>
        """
        return self._send(to_email, subject, html)

# Singleton
email_service = EmailService()
