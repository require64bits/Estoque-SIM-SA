#Importações Necessárias
from flask import Flask, request, render_template
import gspread

#Conexão com a Planilha
conexao = gspread.service_account()
planilha = conexao.open("Nature Saboaria").sheet1

#Aplicação:
#A variável root_path você deve modificar com o caminho completo da pasta python no seu sistema, serve para o Flask achar a pasta templates corretamente ^^
app = Flask("Estoque-SIM-SA", root_path="")
@app.route("/")
def main():
    #Isso aqui é era só pra mostrar o poder do Jinja2, pode remover se quiser
    #Obtendo a planilha completa sem os valores "Nome", "Quantidade" e etc
    planilha_completa = []
    for produto in planilha.get_all_values():
        if produto[0] == "Nome":
            continue
        planilha_completa.append(produto)
    #Gerando um hmtl com todos os produtos da planilha com o Jinja2, dê uma olhada no arquivo listarProdutos e base na pasta templates
    return render_template("remover_quantidade.html")

#Roteamento para remover um produto
@app.route("/remover", methods=["POST"])
def remove():
    #Pesquisa o nome enviado na planilha
    remover = planilha.find(request.form.get("nome"))
    #Verifica se encontrou o produto
    if not remover:
        return u"""<script>alert("Houve um erro na pesquisa do produto! Confira se digitou corretamente.")</script>"""
    #Faz a remoção do produto e avalia se a exclusão foi bem sucedida ou não
    if planilha.delete_rows(remover.row):
        return u"""<script>alert("Feito!")</script>"""
    else:
        return u"""<script>alert("Houve um Erro ao deletar o produto!")</script>"""

#Roteamento para remover uma quantidade de um produto, caso a quantidade do produto fique abaixo do limite, ele dispara um alerta
@app.route("/remover_qtd", methods=["POST"])
def retirar():
    #Procura o Produto
    rm = planilha.find(request.form.get("nome"))
    #Verifica se encontrou o produto
    if not rm:
        return u"""<script>alert("Houve um erro na pesquisa do produto! Confira se digitou corretamente.")</script>"""
    #Verifica se a quantidade que vai ser retirada é maior que a quantidade disponível, se sim, retorna um erro
    if int(planilha.cell(rm.row, 2).value) < int(request.form.get("quantidade")):
        return u"""<script>alert("A quantidade que você quer retirar é maior que a quantidade disponível!Tente colocar um número menor!")</script>"""
    #Atualiza a célula com o valor da subtração do valor que já tem na célula com o valor que o usuário quer retirar
    planilha.update_cell(rm.row, 2, int(planilha.cell(rm.row, 2).value) - int(request.form.get("quantidade")))
    #Verifica se a quantidade atual está abaixo do valor limite definido pelo usuário (por enquanto o limite é fixo kkkkk)
    if int(planilha.cell(rm.row, 2).value) < 5:
        return u"""<script>alert("Atenção! O produto está abaixo do limite especificado")</script>"""
    else:
        return u"""<script>alert("Operação feita com sucesso!")</script>"""



app.run(debug=True, use_reloader=True)