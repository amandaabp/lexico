import classes as classes
import matrizes as matrizes
tokens = classes.Lista_de_tokens()

def palavra_reservada(w):
    return (w == tokens.inicio or
            w == tokens.varinicio or
            w == tokens.varfim or
            w == tokens.leia or
            w == tokens.escreva or
            w == tokens.se or
            w == tokens.entao or
            w == tokens.fimse or
            w == tokens.fim or
            w == tokens.inteiro or
            w == tokens.lit or
            w == tokens.real)

def proxima_acao(estado):
    if (estado == 999):
        return "aceitar"

    if (estado > 200):
        estado = (estado - 200)
        return "reduzir"

    if (estado > 100):
        estado = (estado - 100)
        return "empilhar"

    if (estado == 0):
        return "erro"

    return ""

def ler_arquivo_mgol(lex):
    f = open("mgol.alg", "r")
    lex.qtd_linhas = len(open("mgol.alg").readlines())
    lex.codigo_mgol = f.read() + '\0'

def contar_palavras(frase):
    espaco = True
    numero_palavras = 0
    for letra in frase:
        if letra == '\0':
            break
        if letra.isspace():
            espaco = True
        elif espaco == True:
            numero_palavras += 1
            espaco = False
    return numero_palavras


def eqToken(token):
    tokenTrad=token
    if token == "OPM":
        return tokenTrad + " - Operador Matemático"
    if token == "OPR":
        return tokenTrad + " - Operador Relacional"
    if token == "id":
        return tokenTrad + " - identificador"
    if token == "num":
        return tokenTrad + " - número"
    if token == "RCB":
        return tokenTrad + " - Atribuição"
    if token == "AB_P":
        return tokenTrad + " - Abre Parêntesis - '('"
    if token == "FC_P":
        return tokenTrad + " - Fecha Parêntesis - ')'"
    if token == "PT_V":
        return tokenTrad + " - Ponto e Vírgula - ;"
    if token == "VIR":
        return tokenTrad + " - Vírgula - ,"
    else:
        return token

def tokenizar(c, estado_atual):  # essa função generaliza todas as entradas
    if (estado_atual == 2 or estado_atual == 4):
        if (c == 'e'):
            return c
        if (c == 'E'):
            return c
    if (estado_atual == 18):
        if (c != '"'):  # enquanto o estado for 18, tudo estará dentro do literal, até que feche as aspas
            return 'A'
        else:
            return c
    if (estado_atual == 16):
        if (c != '}'):  # enquanto o estado for 16, tudo estará dentro do comentário, até que feche a chave
            return 'A'
        else:
            return c
    if (c == '\n' or c == ' ' or c == '\t' or c == '\0'):
        return 'S'
    if (c.isalpha()):  # se o caractere for alfabético, retorna L
        return 'L'
    if (c.isdigit()):  # se o caractere for numérico, retorna D
        return 'D'
    else:
        return c

def erro(lex,t, tk, estado_atual, estado_novo, ini_lexema, fim_lexema):
    # Verifica se o estado atual é final
    token=matrizes.matriz_de_estados_finais.get(estado_atual, None)
    error=matrizes.matriz_de_estados_finais.get(matrizes.matriz_de_estados_lexica.get(
        (t, -1), 0), None)  # vefifica se o erro é conhecido
    if token is not None and error is not None:
        if token != error:
            if (token == tokens.id_ or token == tokens.num):
                if (lex.codigo_mgol[ini_lexema:fim_lexema] == tokens.se):
                    if (error == tokens.AB_P):
                        return 0
                if (error == tokens.PT_V or error == tokens.OPR or error == tokens.OPM or error == tokens.FC_P):
                    return 0
            if (token == tokens.AB_P):
                if (error == tokens.id_ or error == tokens.num):
                    return 0
                else:
                    tk.linha=lex.linha
                    tk.coluna=lex.coluna
                    tk.lexema=lex.codigo_mgol[ini_lexema:fim_lexema]
                    tk.erro="ERRO1 – Falta um valor ou variavel depois desse Abre Parenteses: '" + tk.lexema + "'"
                    return tk
            if (token == tokens.OPR or token == tokens.OPM or token == tokens.RCB):
                if (error == tokens.id_ or error == tokens.num):
                    return 0
                else:
                    tk.linha=lex.linha
                    tk.coluna=lex.coluna
                    tk.lexema=lex.codigo_mgol[ini_lexema:fim_lexema]
                    tk.erro="ERRO2 – Falta um valor ou variavel aqui: '" + tk.lexema + "'"
                    lex.codigo_mgol=lex.codigo_mgol[1:len(lex.codigo_mgol)]

        else:
            tk.linha=lex.linha
            tk.coluna=lex.coluna
            tk.lexema=lex.codigo_mgol[ini_lexema:fim_lexema]
            tk.erro="ERRO3 – Token duplicado: '" + tk.lexema + "'"
            return tk
    elif (token is not None and error is None):
        tk.linha=lex.linha
        tk.coluna=lex.coluna
        tk.lexema=lex.codigo_mgol[ini_lexema:fim_lexema]
        tk.erro="ERRO4 – Caractere invalido: '" + tk.lexema + "'"
        return tk
    tk.linha = lex.linha
    tk.coluna = lex.coluna
    tk.lexema = lex.codigo_mgol[ini_lexema:fim_lexema]
    tk.erro = "ERRO5 – Caractere invalido: '" + tk.lexema + "'"
    lex.codigo_mgol = lex.codigo_mgol[1:len(lex.codigo_mgol)]
    return tk

def scanner(lex):  # retorna o próximo token
    tk=classes.Token()
    snt=classes.Semantico()
    estado_atual=-1  # o estado inicial é -1
    estado_novo=-1
    # ini_lexema e fim_lexema marcam as posições de início e o fim de cada lexema
    ini_lexema=0
    fim_lexema=-1   # para retirar cada lexema da string que armazena o código completo
    for c in lex.codigo_mgol:  # vou iterar caractere por caractere no código, até encontrar o próximo token
        if c == '\0' and estado_atual == -1 and estado_novo == -1:          
            tk.linha = lex.linha
            tk.lexema = tokens.EndOfFile
            tk.token = tokens.EndOfFile
            return tk

        fim_lexema += 1
        t=tokenizar(c, estado_atual)

        # a matriz de estados léxica é um dicionário. A chave é um par de (char,int), e o valor é um int
        # Chave = (entrada,estado_atual)
        # Valor = estado_novo
        estado_novo=matrizes.matriz_de_estados_lexica.get((t, estado_atual), 0)
        # em python, utilizando a função get(), posso passar a chave como parâmetro para obter o valor correspondente
        # se o par (entrada,estado_atual) não for encontrado, retorno o estado 0, que é o estado de erro

        if estado_novo == -1 and estado_atual == 20:  # COMENTÁRIO
            print("Linha ", lex.linha, " [comentario] ",
                  lex.codigo_mgol[ini_lexema:fim_lexema], "\n")
            ini_lexema = fim_lexema
            if c == '\n' or c == '\t' or c == ' ':
                ini_lexema += 1
                if c == '\n':
                    lex.linha += 1
                    lex.coluna = 1
        elif estado_novo == -1 and estado_atual != -1:  # LEXEMA AINDA NÃO ACABOU
            break
        elif estado_novo == -1 and estado_atual == -1:  # LEXEMA ACABOU
            ini_lexema += 1
            if c == '\n':
                lex.linha += 1
                lex.coluna = 1
            if c == '\t' or c == ' ':
                lex.coluna += 1
        elif estado_novo == 0:  # TRATAMENTO DE ERRO
            er = erro(lex,t, tk, estado_atual, estado_novo, ini_lexema, fim_lexema)            
            if er == 0:
                break
            else:
                tk.token = matrizes.matriz_de_estados_finais.get(estado_atual, None)
                return er
        else:
            lex.coluna += 1
        estado_atual = estado_novo

    # verifico se o estado atual é final
    _token = matrizes.matriz_de_estados_finais.get(estado_atual, None)
    _lexema = lex.codigo_mgol[ini_lexema:fim_lexema]  # pego o lexema do código

    if (_token is not None):
        # atualizo o código deletando o que já foi lido
        lex.codigo_mgol = lex.codigo_mgol[fim_lexema:len(lex.codigo_mgol)]
        if (_token == tokens.id_):
            if (not palavra_reservada(_lexema)):
                for s in lex.ids:
                    if(s.lexema == _lexema):
                        snt.estado = -2
                if(snt.estado == -1):
                    snt.lexema = _lexema
                    snt.token = tokens.id_
                    lex.ids.append(snt)
                tk.tipo = ""
            else:
                # se o lexema for uma palavra reservada, pode ser que ele seja um tipo, e
                _token = _lexema
                # os tipos definidos pela linguagem são int, lit e real
                if (_token == tokens.inteiro):
                    tk.tipo = "int"
                elif (_token == tokens.lit):
                    tk.tipo = "literal"
                elif (_token == tokens.real):
                    tk.tipo = "double"
                else:
                    tk.tipo = ""

        # print("Linha ",lex.linha," [",_token,"] ",_lexema)

        tk.linha = lex.linha
        tk.coluna = lex.coluna
        tk.tipo = tk.tipo
        tk.lexema = _lexema
        tk.token = _token
        return tk
    else:
        # se chegou aqui, então o usuário esqueceu de fechar as chaves ou aspas,
        if (estado_atual == 16 or estado_atual == 18):
            # pq o estado de retorno sempre tem que ser final
            tk.linha = lex.linha
            tk.coluna = lex.coluna
            tk.erro = "Esqueceu de fechar alguma coisa aqui: " + \
                _lexema[0:7] + "..."
            return tk
        tk.linha = lex.linha
        tk.coluna = lex.coluna
        tk.lexema = _lexema
        return tk

def tratar_erro_lexico(lex,t):
    lex.codigo_mgol = lex.codigo_mgol[len(t.lexema):len(lex.codigo_mgol)]
    lex.codigo_mgol = t.lexema + "0" + lex.codigo_mgol
    t = scanner(lex)