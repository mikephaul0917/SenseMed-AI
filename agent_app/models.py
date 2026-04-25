from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Drug(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    drug_name = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    pro_tip = db.Column(db.Text, nullable=True)
    dosage_snapshot = db.Column(db.Text, nullable=True)

    side_effect_reports = db.relationship('SideEffectReport', backref='drug', lazy=True, cascade="all, delete-orphan")


class SideEffectReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    side_effect_name = db.Column(db.String(100), nullable=False)
    side_effect_category = db.Column(db.String(50), nullable=True)
    side_effect_probability = db.Column(db.Float, nullable=False)
    side_effect_severity = db.Column(db.Float, nullable=True, default=5.0)
    side_effect_demographics = db.Column(db.Text, nullable=True) # JSON multipliers

    drug_id = db.Column(db.Integer, db.ForeignKey('drug.id'), nullable=False)