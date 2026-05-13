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
    credits_balance = db.Column(db.Integer, default=25) # Bônus inicial: 25 moedas
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
            "email": self.email if self.is_active else "anonimo@lumiere.com",
            "credits_balance": self.credits_balance,
            "is_admin": self.is_admin,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat()
        }

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
    type = db.Column(db.String(50)) # 'bonus_initial', 'generation_cost', 'admin_credit'
    amount = db.Column(db.Integer)
    balance_before = db.Column(db.Integer)
    balance_after = db.Column(db.Integer)
    description = db.Column(db.String(255))
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

    def to_dict(self):
        return {
            "id": self.id,
            "status": self.status,
            "progress": self.progress,
            "message": self.message,
            "images": json.loads(self.images_json),
            "tipo_ensaio": self.tipo_ensaio,
            "created_at": self.created_at.strftime("%d %b %Y, %H:%M"),
            "error": self.error,
            "metadata": json.loads(self.metadata_json),
            "cost_moedas": self.cost_moedas
        }

    def set_images(self, images_list):
        self.images_json = json.dumps(images_list)

    def set_metadata(self, metadata_dict):
        self.metadata_json = json.dumps(metadata_dict)
