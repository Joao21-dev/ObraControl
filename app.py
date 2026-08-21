from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import date
import os
from dotenv import load_dotenv
from models import db, Material, Obra, Movimentacao

load_dotenv()  # lê o arquivo .env da pasta do projeto, se existir

app = Flask(__name__)
app.secret_key = "obracontrol123"

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL",
    "postgresql://obracontrol:obracontrol@localhost:5432/obracontrol"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()

# Categorias de material e as unidades de medida compatíveis com cada uma
CATEGORIAS_UNIDADES = {
    "Cimento e Argamassa": ["saco", "kg", "ton"],
    "Agregados (areia, brita, pedra)": ["m³", "ton", "kg"],
    "Aço e Ferragens": ["barra", "kg", "ton", "un"],
    "Alvenaria (tijolo, bloco)": ["milheiro", "un", "m²"],
    "Madeira": ["m³", "m", "un", "peça"],
    "Hidráulica": ["un", "m", "rolo", "kg"],
    "Elétrica": ["un", "m", "rolo", "caixa"],
    "Tintas e Vernizes": ["litro", "galão (18L)", "lata"],
    "Revestimentos (piso, azulejo)": ["m²", "caixa", "un"],
    "Cobertura (telha)": ["un", "m²", "milheiro"],
    "Esquadrias (porta, janela)": ["un"],
    "Ferramentas e EPI": ["un", "par", "caixa"],
    "Outros": ["un", "kg", "m", "m²", "m³", "litro"],
}

def eh_ajax():
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"

# ---------------- MATERIAIS ----------------

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
            nome=request.form["nome"][:45],
            categoria=request.form["categoria"],
            quantidade=int(request.form["quantidade"]),
            unidade=request.form["unidade"],
            valor=float(request.form["valor"]),
            fornecedor=request.form["fornecedor"][:45]
        )
        db.session.add(material)
        db.session.commit()
        flash("✅ Material cadastrado com sucesso!", "success")
        if eh_ajax():
            return jsonify(ok=True)
        return redirect(url_for("index"))
    if eh_ajax():
        return render_template("_cadastrar_content.html", categorias_unidades=CATEGORIAS_UNIDADES)
    return render_template("cadastrar.html", categorias_unidades=CATEGORIAS_UNIDADES)

@app.route("/excluir/<int:id>")
def excluir(id):
    material = Material.query.get_or_404(id)
    db.session.delete(material)
    db.session.commit()
    flash("🗑️ Material excluído com sucesso!", "success")
    return redirect(url_for("index"))

@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    material = Material.query.get_or_404(id)
    if request.method == "POST":
        material.nome = request.form["nome"][:45]
        material.categoria = request.form["categoria"]
        material.quantidade = int(request.form["quantidade"])
        material.unidade = request.form["unidade"]
        material.valor = float(request.form["valor"])
        material.fornecedor = request.form["fornecedor"][:45]
        db.session.commit()
        flash("✏️ Material atualizado com sucesso!", "success")
        if eh_ajax():
            return jsonify(ok=True)
        return redirect(url_for("index"))
    if eh_ajax():
        return render_template("_editar_content.html", material=material, categorias_unidades=CATEGORIAS_UNIDADES)
    return render_template("editar.html", material=material, categorias_unidades=CATEGORIAS_UNIDADES)

# ---------------- OBRAS ----------------

@app.route("/obras")
def obras():
    lista = Obra.query.order_by(Obra.nome).all()
    total_obras = len(lista)
    ativas = len([o for o in lista if o.ativa])
    return render_template("obras.html", obras=lista, total_obras=total_obras, ativas=ativas)

@app.route("/obras/nova", methods=["GET", "POST"])
def nova_obra():
    if request.method == "POST":
        obra = Obra(
            nome=request.form["nome"][:80],
            endereco=request.form.get("endereco", "")[:150],
            data_inicio=date.fromisoformat(request.form["data_inicio"]) if request.form.get("data_inicio") else date.today(),
            ativa=True
        )
        db.session.add(obra)
        db.session.commit()
        flash("✅ Obra cadastrada com sucesso!", "success")
        if eh_ajax():
            return jsonify(ok=True)
        return redirect(url_for("obras"))
    if eh_ajax():
        return render_template("_obra_form_content.html", obra=None)
    return render_template("obra_form.html", obra=None)

@app.route("/obras/<int:id>/editar", methods=["GET", "POST"])
def editar_obra(id):
    obra = Obra.query.get_or_404(id)
    if request.method == "POST":
        obra.nome = request.form["nome"][:80]
        obra.endereco = request.form.get("endereco", "")[:150]
        if request.form.get("data_inicio"):
            obra.data_inicio = date.fromisoformat(request.form["data_inicio"])
        obra.ativa = bool(request.form.get("ativa"))
        db.session.commit()
        flash("✏️ Obra atualizada com sucesso!", "success")
        if eh_ajax():
            return jsonify(ok=True)
        return redirect(url_for("obras"))
    if eh_ajax():
        return render_template("_obra_form_content.html", obra=obra)
    return render_template("obra_form.html", obra=obra)

@app.route("/obras/<int:id>/excluir")
def excluir_obra(id):
    obra = Obra.query.get_or_404(id)
    if obra.movimentacoes:
        flash("⚠️ Não é possível excluir uma obra com movimentações registradas.", "danger")
        return redirect(url_for("obras"))
    db.session.delete(obra)
    db.session.commit()
    flash("🗑️ Obra excluída com sucesso!", "success")
    return redirect(url_for("obras"))

# ---------------- MOVIMENTAÇÕES ----------------

@app.route("/movimentacoes")
def movimentacoes():
    obra_id = request.args.get("obra_id", type=int)
    query = Movimentacao.query
    if obra_id:
        query = query.filter_by(obra_id=obra_id)
    lista = query.order_by(Movimentacao.data.desc(), Movimentacao.id.desc()).all()
    todas_obras = Obra.query.order_by(Obra.nome).all()
    return render_template("movimentacoes.html", movimentacoes=lista, obras=todas_obras, obra_id=obra_id)

@app.route("/movimentacoes/nova", methods=["GET", "POST"])
def nova_movimentacao():
    if request.method == "POST":
        material = Material.query.get_or_404(int(request.form["material_id"]))
        tipo = request.form["tipo"]
        quantidade = int(request.form["quantidade"])

        if tipo == "saida" and quantidade > material.quantidade:
            erro = f"⚠️ Estoque insuficiente. Disponível: {material.quantidade} {material.unidade}."
            if eh_ajax():
                return jsonify(ok=False, error=erro)
            flash(erro, "danger")
            return redirect(url_for("nova_movimentacao"))

        movimentacao = Movimentacao(
            tipo=tipo,
            quantidade=quantidade,
            data=date.fromisoformat(request.form["data"]) if request.form.get("data") else date.today(),
            observacao=request.form.get("observacao", "")[:200],
            material_id=material.id,
            obra_id=int(request.form["obra_id"])
        )

        if tipo == "entrada":
            material.quantidade += quantidade
        else:
            material.quantidade -= quantidade

        db.session.add(movimentacao)
        db.session.commit()
        flash("✅ Movimentação registrada com sucesso!", "success")
        if eh_ajax():
            return jsonify(ok=True)
        return redirect(url_for("movimentacoes"))

    materiais = Material.query.order_by(Material.nome).all()
    todas_obras = Obra.query.order_by(Obra.nome).all()
    obra_id = request.args.get("obra_id", type=int)
    if not todas_obras:
        if eh_ajax():
            return render_template("_sem_obras_content.html")
        flash("⚠️ Cadastre uma obra antes de registrar movimentações.", "danger")
        return redirect(url_for("obras"))
    if eh_ajax():
        return render_template("_movimentacao_form_content.html", mov=None, materiais=materiais, obras=todas_obras, obra_id=obra_id)
    return render_template("movimentacao_form.html", mov=None, materiais=materiais, obras=todas_obras, obra_id=obra_id)

@app.route("/movimentacoes/<int:id>/editar", methods=["GET", "POST"])
def editar_movimentacao(id):
    mov = Movimentacao.query.get_or_404(id)

    if request.method == "POST":
        novo_material = Material.query.get_or_404(int(request.form["material_id"]))
        novo_tipo = request.form["tipo"]
        nova_quantidade = int(request.form["quantidade"])

        # Reverte o efeito que a movimentação antiga tinha no estoque
        material_antigo = mov.material
        if mov.tipo == "entrada":
            material_antigo.quantidade -= mov.quantidade
        else:
            material_antigo.quantidade += mov.quantidade

        # Valida se o novo lançamento é possível (com o estoque já revertido)
        if novo_tipo == "saida" and nova_quantidade > novo_material.quantidade:
            db.session.rollback()
            erro = f"⚠️ Estoque insuficiente para essa alteração. Disponível: {novo_material.quantidade} {novo_material.unidade}."
            if eh_ajax():
                return jsonify(ok=False, error=erro)
            flash(erro, "danger")
            return redirect(url_for("editar_movimentacao", id=id))

        # Aplica o novo efeito
        if novo_tipo == "entrada":
            novo_material.quantidade += nova_quantidade
        else:
            novo_material.quantidade -= nova_quantidade

        mov.tipo = novo_tipo
        mov.quantidade = nova_quantidade
        mov.data = date.fromisoformat(request.form["data"]) if request.form.get("data") else mov.data
        mov.observacao = request.form.get("observacao", "")[:200]
        mov.material_id = novo_material.id
        mov.obra_id = int(request.form["obra_id"])

        db.session.commit()
        flash("✏️ Movimentação atualizada e estoque ajustado!", "success")
        if eh_ajax():
            return jsonify(ok=True)
        return redirect(url_for("movimentacoes"))

    materiais = Material.query.order_by(Material.nome).all()
    todas_obras = Obra.query.order_by(Obra.nome).all()
    if eh_ajax():
        return render_template("_movimentacao_form_content.html", mov=mov, materiais=materiais, obras=todas_obras, obra_id=None)
    return render_template("movimentacao_editar.html", mov=mov, materiais=materiais, obras=todas_obras, obra_id=None)

@app.route("/movimentacoes/<int:id>/excluir")
def excluir_movimentacao(id):
    mov = Movimentacao.query.get_or_404(id)
    material = mov.material

    # Verifica se reverter essa movimentação deixaria o estoque negativo
    if mov.tipo == "entrada" and material.quantidade - mov.quantidade < 0:
        flash("⚠️ Não é possível excluir: o estoque já foi consumido depois desta entrada.", "danger")
        return redirect(url_for("movimentacoes"))

    if mov.tipo == "entrada":
        material.quantidade -= mov.quantidade
    else:
        material.quantidade += mov.quantidade

    db.session.delete(mov)
    db.session.commit()
    flash("🗑️ Movimentação excluída e estoque ajustado de volta!", "success")
    return redirect(url_for("movimentacoes"))

if __name__ == "__main__":
    app.run(debug=True)
