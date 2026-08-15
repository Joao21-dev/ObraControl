from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Material

app = Flask(__name__)
app.secret_key = "obracontrol123"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///materiais.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route("/")
def index():
    pesquisa = request.args.get("pesquisa", "")
    if pesquisa:
        materiais = Material.query.filter(Material.nome.contains(pesquisa)).order_by(Material.nome).all()
    else:
        materiais = Material.query.order_by(Material.nome).all()
    total_materiais = len(materiais)
    valor_total = sum(material.quantidade * material.valor for material in materiais)
    categorias = len(set(material.categoria for material in materiais))
    estoque_baixo = len([material for material in materiais if material.quantidade < 5])
    return render_template("index.html", materiais=materiais, total_materiais=total_materiais, valor_total=valor_total, categorias=categorias, estoque_baixo=estoque_baixo, pesquisa=pesquisa)

@app.route("/cadastrar", methods=["GET", "POST"])
def cadastrar():
    if request.method == "POST":
        material = Material(
            nome=request.form["nome"],
            categoria=request.form["categoria"],
            quantidade=int(request.form["quantidade"]),
            unidade=request.form["unidade"],
            valor=float(request.form["valor"]),
            fornecedor=request.form["fornecedor"]
        )
        db.session.add(material)
        db.session.commit()
        flash("✅ Material cadastrado com sucesso!", "success")
        return redirect(url_for("index"))
    return render_template("cadastrar.html")
@app.route("/excluir/<int:id>")
def excluir(id):
    material = Material.query.get_or_404(id)
    db.session.delete(material)
    db.session.commit()
    flash("🗑️ Material excluído com sucesso!", "success")
    return redirect(url_for("index"))
@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    material= Material.query.get_or_404(id)
    if request.method == "POST":
        material.nome = request.form["nome"]
        material.categoria = request.form["categoria"]
        material.quantidade = int(request.form["quantidade"])
        material.unidade = request.form["unidade"]
        material.valor = float(request.form["valor"])
        material.fornecedor = request.form["fornecedor"]
        db.session.commit()
        flash("✏️ Material atualizado com sucesso!", "success")
        return redirect(url_for("index"))
    return render_template("editar.html", material=material)
if __name__ == "__main__":
    app.run(debug=True)