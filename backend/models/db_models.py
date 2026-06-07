import uuid
from datetime import datetime
from database import db
import json
import bcrypt

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    credits_balance = db.Column(db.Integer, default=0)  # Sem bônus inicial; créditos via compra

    phone = db.Column(db.String(20), nullable=True)
    cpf = db.Column(db.String(14), nullable=True)
    asaas_customer_id = db.Column(db.String(50), nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True) # Para LGPD (Exclusão Lógica)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    jobs = db.relationship('GenerationJob', backref='owner', lazy=True)
    transactions = db.relationship('Transaction', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name if self.is_active else "Usuário Excluído",
            "email": self.email if self.is_active else "anonimo@aureaia.com",
            "cpf": self.cpf if self.is_active else None,
            "credits_balance": self.credits_balance,
            "is_admin": self.is_admin,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat()
        }

class EmailVerification(db.Model):
    __tablename__ = 'email_verifications'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(120), nullable=False, index=True)
    code = db.Column(db.String(6), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)

class PasswordResetToken(db.Model):
    __tablename__ = 'password_reset_tokens'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    type = db.Column(db.String(50)) # 'bonus_initial', 'generation_cost', 'admin_credit', 'purchase'
    amount = db.Column(db.Integer) # credits amount
    balance_before = db.Column(db.Integer)
    balance_after = db.Column(db.Integer)
    description = db.Column(db.String(255))
    status = db.Column(db.String(20), default='completed') # 'pending', 'completed', 'failed'
    external_id = db.Column(db.String(100), unique=True, nullable=True) # PagSeguro Order ID or Legacy ID
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class GenerationJob(db.Model):
    __tablename__ = 'generation_jobs'
    
    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    status = db.Column(db.String(20), default="queued")
    tipo_ensaio = db.Column(db.String(50))
    input_image_url = db.Column(db.String(500))
    progress = db.Column(db.Integer, default=0)
    message = db.Column(db.String(200))
    error = db.Column(db.Text)
    cost_moedas = db.Column(db.Integer, default=25)
    
    # Store images as a JSON string
    images_json = db.Column(db.Text, default='[]')
    
    # Metadata as JSON
    metadata_json = db.Column(db.Text, default='{}')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def result_url(self):
        try:
            images_list = json.loads(self.images_json) if self.images_json else []
            return images_list[0] if images_list else None
        except Exception:
            return None

    @result_url.setter
    def result_url(self, value):
        if value:
            self.images_json = json.dumps([value])

    def to_dict(self):
        try:
            images_list = json.loads(self.images_json) if self.images_json else []
        except Exception:
            images_list = []
            
        return {
            "id": self.id,
            "status": self.status,
            "progress": self.progress,
            "message": self.message,
            "images": images_list,
            "result_url": self.result_url,
            "tipo_ensaio": self.tipo_ensaio,
            "created_at": self.created_at.strftime("%d %b %Y, %H:%M"),
            "error": self.error,
            "metadata": json.loads(self.metadata_json) if self.metadata_json else {},
            "cost_moedas": self.cost_moedas
        }

    def set_images(self, images_list):
        self.images_json = json.dumps(images_list)

    def set_metadata(self, metadata_dict):
        self.metadata_json = json.dumps(metadata_dict)
