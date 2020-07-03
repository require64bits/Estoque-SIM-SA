#Importações Necessárias
from flask import Flask, request, render_template, redirect
from unidecode import unidecode
import gspread

#Conexão com a Planilha
conexao = gspread.service_account()
planilha = conexao.open("Nature Saboaria").sheet1

#Aplicação:
#A variável root_path você deve modificar com o caminho completo da pasta python no seu sistema, serve para o Flask achar a pasta templates corretamente ^^
#app = Flask("Estoque-SIM-SA", root_path="H:\\Users\\agata\\Documents\\projeto trainee\\estoque-sim-sa\\Controle de estoque\\python")
#app = Flask("Estoque-SIM-SA", root_path="C:\\Users\\tanko\\estoque-sim-sa\\Controle de estoque\\python")
app = Flask("Estoque-SIM-SA", root_path="/home/lucas/Desktop/estoque-sim-sa/Controle de estoque/python")


@app.route("/")
def main():
    return render_template("home.html")

#Roteamento para remover um produto
@app.route("/remover", methods=["POST"])
def remove():
    #Pesquisa o nome enviado na planilha
    remover = planilha.find(request.form.get("delete"))

    #Faz a remoção do produto e avalia se a exclusão foi bem sucedida ou não
    if planilha.delete_rows(remover.row):
        return render_template("respostaEstoque.html", retorno = "Feito!",
        planilha_completa = planilha.get_all_values()
    )
    else:
        return render_template("respostaEstoque.html", retorno = "Houve um Erro ao deletar o produto!",
        planilha_completa = planilha.get_all_values()
    )

# Captura qual é o item que irá ser retirada uma determinada quantidade, e exibe o popup
@app.route('/popup', methods=['POST'])
def popup():
    item = planilha.find(request.form.get('item'))
    img = planilha.cell(item.row, 6)
    return render_template('popup.html',
    planilha_completa = planilha.get_all_values(),
    nome = item.value,
    imagem = img.value,
    quantidade = planilha.cell(item.row, 2).value
    )

# Roteamento para remover uma quantidade de um produto, caso a quantidade do produto fique abaixo do limite, ele dispara um alerta
@app.route("/venda", methods=["POST"])
def venda():
    # Procura o Produto
    rm = planilha.find(request.form.get('nome'))

    # Atualiza a célula com o valor da subtração do valor que já tem na célula com o valor que o usuário quer retirar
    planilha.update_cell(rm.row, 2, int(planilha.cell(rm.row, 2).value) - int(request.form.get("quantidade")))

    # Verifica se a quantidade atual está abaixo do valor limite definido pelo usuário (por enquanto o limite é fixo kkkkk)
    if int(planilha.cell(rm.row, 2).value) < 5:
        return render_template("respostaEstoque.html", retorno = "Atenção! O produto está abaixo do limite especificado",
        planilha_completa = planilha.get_all_values()
    )
    else:
        return render_template("respostaEstoque.html", retorno = "Operação feita com sucesso!",
        planilha_completa = planilha.get_all_values()
    )

# Rotas para Inserir Produto
@app.route('/inserir')
def inserir():
    return render_template("incluirProduto.html")

# Rota de Captura das Informações para adicionar na planilha
@app.route('/recebendo_dados', methods=['POST'])
def add():
    arr = [
        'nome', 
        'quantidade', 
        'preço',
        'valor',
        'área do corpo',
        'imagem'
    ]

    # Laço For para adicionar os dados dentro da minha lista row.
    row = []
    for pos, n in enumerate(arr):
        item = request.form.get(n)
        if pos == 3:
            item = request.form.get(n) + request.form.get('volume')
        row.append(item)
    
    # Laço For para verificar se os dados que o usuários inseriu é compatível com alguma linha dentro da planilha;
    # Caso seja compatível, ele apenas irá alterar a quantidade adicionada.
    same = contsame = 0
    for pos, linha in enumerate(planilha.get_all_values()):
        for cell in range(0, 6):
            if linha[cell] == linha[1] or linha[cell] == linha[5]:
                continue
            elif unidecode(linha[cell]).lower().strip() == unidecode(row[cell]).lower().strip():
                same += 1
        
        # Caso seja igual a 8, significa dizer que as 8 colunas de uma linha eram iguais aos dados que o usuário inseriu;
        # Então quer dizer que a linha já existe na planilha, portanto, só a quantidade será alterada.
        if same == 4:
            newquant = int(linha[1]) + int(row[1])
            planilha.update_cell(pos + 1, 2, newquant)
            contsame += 1

            # Verificando se a imagem adicionada é a mesma no banco de dados, caso sejam diferentes, a imagem será atualizada
            if request.form.get('imagem') != planilha.cell(pos + 1, 6).value:
                planilha.update_cell(pos + 1, 6, request.form.get('imagem'))
                return render_template('/respostaIncluir.html', retorno = 'Quantidade do item e imagem foram atualizadas com sucesso!')

            return render_template('/respostaIncluir.html', retorno = 'Quantidade do item foi atualizada com sucesso!')

        else:
            same = 0
    
    # contsame == 0 significa que não há nenhum item na planilha igual ao inserido pelo usuário, logo, será um novo item
    if contsame == 0:
        index = len(planilha.get_all_values()) + 1
        planilha.insert_row(row, index)
        return render_template('/respostaIncluir.html', retorno = 'Novo item adicionado com sucesso!')

@app.route('/estoque')
def estoque():
    return render_template('estoque.html', planilha_completa = planilha.get_all_values())

app.run(debug=True, use_reloader=True)
