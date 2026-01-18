from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    jersey_id = db.Column(db.Integer, nullable=False, index=True)
    jersey_name = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Integer, nullable=False)  # Amount in cents
    customer_email = db.Column(db.String(255), nullable=False, index=True)
    customer_name = db.Column(db.String(255), nullable=False)
    shipping_address = db.Column(db.Text, nullable=False)
    shipping_method = db.Column(db.String(255), nullable=False)
    shipping_cost = db.Column(db.Numeric(10, 2), nullable=False)
    payment_intent_id = db.Column(db.String(255), unique=True, nullable=False)
    payment_status = db.Column(db.String(50), nullable=False, default='pending', index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert order to dictionary."""
        return {
            'order_id': f"ORD-{self.id:06d}",  # Fixed format: ORD-000001
            'jersey_name': self.jersey_name,
            'amount': self.amount,
            'customer_email': self.customer_email,
            'customer_name': self.customer_name,
            'shipping_address': self.shipping_address,
            'shipping_method': self.shipping_method,
            'shipping_cost': float(self.shipping_cost),
            'payment_status': self.payment_status,
            'created_at': self.created_at.isoformat(),
        } 