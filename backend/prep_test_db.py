from app import create_app
from models.db_models import db, User, Transaction

app = create_app()
with app.app_context():
    user = User.query.filter_by(email='qa@aureaia.com').first()
    if not user:
        user = User(name='QA User', email='qa@aureaia.com')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
    
    # Create a pending transaction for testing the webhook
    # Using the identifier from my previous successful API call
    identifier = 'a9a6702b-a426-4ebb-9672-687c2e37381c'
    
    # Remove existing if any
    Transaction.query.filter_by(external_id=identifier).delete()
    db.session.commit()
    
    txn = Transaction(
        user_id=user.id,
        type='purchase',
        amount=100,
        status='pending',
        external_id=identifier
    )
    db.session.add(txn)
    db.session.commit()
    print(f"Transaction created with external_id: {identifier}")
    print(f"User Balance before: {user.credits_balance}")
