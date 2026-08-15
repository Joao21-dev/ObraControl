from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Material(db.Model):
    __tablename__ = "materiais"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    categoria = db.Column(db.String(100), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    unidade = db.Column(db.String(20), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    fornecedor = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<Material {self.nome}>"
    