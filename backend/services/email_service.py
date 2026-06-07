import os
import logging
import requests
from config import Config

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.api_key = os.environ.get('BREVO_API_KEY') or Config.BREVO_API_KEY
        self.from_email = os.environ.get('BREVO_SENDER_EMAIL') or Config.BREVO_SENDER_EMAIL
        self.from_name = os.environ.get('BREVO_SENDER_NAME') or Config.BREVO_SENDER_NAME
        self.base_url = 'https://api.brevo.com/v3/smtp/email'

    def _send(self, to_email, subject, html_content):
        if not self.api_key:
            logger.warning(f"Email not sent (no BREVO_API_KEY): {subject} to {to_email}")
            return False

        payload = {
            'sender': {'email': self.from_email, 'name': self.from_name},
            'to': [{'email': to_email}],
            'subject': subject,
            'htmlContent': html_content
        }

        headers = {
            'api-key': self.api_key,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        try:
            resp = requests.post(self.base_url, json=payload, headers=headers, timeout=15)
            if resp.ok:
                logger.info(f"Email sent: {subject} to {to_email} (Status: {resp.status_code})")
                return True
            else:
                logger.error(f"Brevo error: {resp.status_code} {resp.text}")
                return False
        except Exception as e:
            logger.error(f"Error sending email via Brevo: {e}")
            return False

    def send_verification_code(self, to_email, name, code):
        subject = "Seu código de verificação — AureaIA"
        html = f"""
        <div style="font-family: sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #eee; border-radius: 10px;">
            <h2 style="color: #9857CB;">Verifique seu e-mail</h2>
            <p>Olá, <strong>{name}</strong>,</p>
            <p>Use o código abaixo para confirmar seu e-mail no AureaIA:</p>
            <div style="margin: 30px 0; text-align: center;">
                <span style="font-size: 36px; font-weight: bold; color: #9857CB; letter-spacing: 8px; background: #f5f0ff; padding: 15px 30px; border-radius: 10px;">{code}</span>
            </div>
            <p style="color: #666;">Este código expira em 15 minutos.</p>
            <p style="color: #666; font-size: 12px;">Se você não solicitou este código, ignore este e-mail.</p>
        </div>
        """
        return self._send(to_email, subject, html)

    def send_welcome(self, to_email, name):
        subject = f"Bem-vinda ao AureaIA, {name.split(' ')[0]}! ✨"
        html = f"""
        <div style="font-family: sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #eee; border-radius: 10px;">
            <h2 style="color: #9857CB;">Sua jornada artística começou!</h2>
            <p>Olá, <strong>{name}</strong>,</p>
            <p>Seja bem-vinda ao <strong>AureaIA</strong>. Seu acesso ao estúdio de fotografia por IA mais avançado do mundo está liberado.</p>
            <div style="margin: 30px 0;">
                <a href="{Config.FRONTEND_URL}/generate" style="background: #9857CB; color: white; padding: 15px 25px; text-decoration: none; border-radius: 5px; font-weight: bold;">Começar meu Ensaio</a>
            </div>
            <p style="color: #666; font-size: 12px;">Se precisar de ajuda, responda a este e-mail.</p>
        </div>
        """
        return self._send(to_email, subject, html)

    def send_password_reset_link(self, to_email, name, reset_link):
        subject = "Recuperação de Senha — AureaIA"
        html = f"""
        <div style="font-family: sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #eee; border-radius: 10px;">
            <h2 style="color: #9857CB;">Esqueceu sua senha?</h2>
            <p>Olá, <strong>{name}</strong>,</p>
            <p>Recebemos uma solicitação para redefinir a senha da sua conta no AureaIA.</p>
            <p>Clique no botão abaixo para escolher uma nova senha:</p>
            <div style="margin: 30px 0;">
                <a href="{reset_link}" style="background: #9857CB; color: white; padding: 15px 25px; text-decoration: none; border-radius: 5px; font-weight: bold;">Redefinir Senha</a>
            </div>
            <p style="color: #666; font-size: 12px;">Se você não solicitou isso, pode ignorar este e-mail.</p>
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

email_service = EmailService()
