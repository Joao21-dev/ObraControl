from flask_sqlalchemy import SQLAlchemy
from datetime import date

db = SQLAlchemy()

class Material(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(50), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    unidade = db.Column(db.String(20), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    fornecedor = db.Column(db.String(100), nullable=False)


class Obra(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    endereco = db.Column(db.String(200))
    data_inicio = db.Column(db.Date, default=date.today)
    ativa = db.Column(db.Boolean, default=True)

    movimentacoes = db.relationship("Movimentacao", backref="obra", lazy=True)


class Movimentacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(10), nullable=False)  # "entrada" ou "saida"
    quantidade = db.Column(db.Integer, nullable=False)
    data = db.Column(db.Date, default=date.today, nullable=False)
    observacao = db.Column(db.String(200))

    material_id = db.Column(db.Integer, db.ForeignKey("material.id"), nullable=False)
    obra_id = db.Column(db.Integer, db.ForeignKey("obra.id"), nullable=False)

    material = db.relationship("Material")
