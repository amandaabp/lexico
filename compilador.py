import collections
import pandas as pd
import copy

df_tabela_sintatica = pd.read_csv('tabela_sintatica.csv', sep=';')
df_matriz_producoes = pd.read_csv('matriz_producoes.csv', sep=';', encoding='utf-8')

class Lex:
    codigo_mgol  = ""
    qtd_linhas   = 0
    linha        = 1
    coluna       = 1
    ids          = []

class Token:
    def __str__(self):
        return "linha=%d,posição=%d,lexema=%s,Classe=%s,tipo=Nulo,erro=%s\n" % (self.linha,self.coluna,self.lexema,self.token,self.erro)
    linha   = 1
    coluna  = 1
    lexema  = ""
    token   = ""
    tipo    = "Nulo"
    erro    = ""

class Sintatico:
    def get(self,t:Token):
        self.lexema = t.lexema
        self.token  = t.token
        self.tipo   = t.tipo
    def getS(self,s):
        if(s.token == ""):
            return
        if(self.token == "ARG" or self.token == "id" or self.token == "EXP_R"):
            return
        self.token = s.token
        if(s.lexema != ""):
            self.lexema = s.lexema        
        if(s.tipo != ""):
            self.tipo = s.tipo
    def inicializar(self):
        self.estado = -1
        self.lexema = ""
        self.token = ""
        self.tipo = ""
    estado = -1
    lexema = ""
    token = ""
    tipo = ""


class Lista_de_tokens:
    num        = "num"           
    id_         = "id"            
    comentario = "comentario"    
    OPR        = "OPR"           
    RCB        = "RCB"           
    OPM        = "OPM"           
    AB_P       = "AB_P"          
    FC_P       = "FC_P"          
    PT_V       = "PT_V"
    VIR        = "VIR"          
    ERRO       = "ERRO"          
    EndOfFile  = "EndOfFile"     
    inicio     = "inicio"        
    varinicio  = "varinicio"     
    varfim     = "varfim"        
    escreva    = "escreva"       
    leia       = "leia"          
    se         = "se"            
    entao      = "entao"         
    fimse      = "fimse"         
    faca_ate   = "faca_ate"      
    fimfaca    = "fimfaca"       
    fim        = "fim"           
    inteiro    = "inteiro"       
    lit        = "lit"           
    real       = "real"   

tokens = Lista_de_tokens()       

matriz_de_estados_lexica = {
    ('S',-1) : -1 ,
    ('S',1 ) : -1 ,
    ('S',2 ) : -1 ,
    ('S',4 ) : -1 ,
    ('S',7 ) : -1 ,
    ('S',8 ) : -1 ,
    ('S',9 ) : -1 ,
    ('S',10) : -1 ,
    ('S',11) : -1 ,
    ('S',12) : -1 ,
    ('S',13) : -1 ,
    ('S',14) : -1 ,
    ('S',15) : -1 ,
    ('S',17) : -1 ,
    ('S',19) : -1 ,
    ('S',20) : -1 ,
 
    (';',1 ) : -1 , 
    (';',2 ) : -1 ,
    (';',4 ) : -1 ,
    (';',7 ) : -1 ,
    (';',19) : -1 ,

    ('L',-1) : 1  , 
    ('L',1 ) : 1  , 
    ('_',1 ) : 1  , 

    ('D',-1) : 2  , 
    ('D',1 ) : 1  , 
    ('D',2 ) : 2  , 
    ('D',3 ) : 4  , 
    ('D',4 ) : 4  , 
    ('D',5 ) : 7  , 
    ('D',6 ) : 7  , 
    ('D',7 ) : 7  , 

    ('E',2 ) : 5  , 
    ('E',4 ) : 5  , 
    ('e',2 ) : 5  , 
    ('e',4 ) : 5  , 
    ('.',2 ) : 3  , 
    ('-',5 ) : 6  , 
    ('+',5 ) : 6  ,

    ('(',-1) : 13 ,
    (')',-1) : 14 ,
    (';',-1) : 15 ,
    ('+',-1) : 17 ,
    ('*',-1) : 17 ,
    ('-',-1) : 17 ,
    ('/',-1) : 17 ,

    ('>',-1) : 9  ,
    ('<',-1) : 10 ,
    ('=',-1) : 9  ,
    ('>',10) : 12 ,
    ('=',10) : 12 ,
    ('=',9 ) : 12 ,
    ('-',10) : 11 ,

    ('"',-1) : 18 ,
    ('A',18) : 18 ,
    ('"',18) : 19 ,
    ('{',-1) : 16 ,
    ('A',16) : 16 ,
    ('}',16) : 20 
}

matriz_de_estados_finais = {
    1  : tokens.id_       ,
    2  : tokens.num       ,
    4  : tokens.num       ,
    7  : tokens.num       ,
    8  : tokens.fim       ,
    9  : tokens.OPR       ,
    10 : tokens.OPR       ,
    11 : tokens.RCB       ,
    12 : tokens.OPR       ,
    13 : tokens.AB_P      ,
    14 : tokens.FC_P      ,
    15 : tokens.PT_V      ,
    17 : tokens.OPM       ,
    19 : tokens.lit       ,
    20 : tokens.comentario,
    22 : tokens.VIR
}

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

def analisador_sintatico(lex):
    ler_arquivo_mgol(lex)     
    print(lex.codigo_mgol)
    i = 0
    lista_tokens = []
    sint = Sintatico()
    pilha = []
    pilha.append(copy.deepcopy(sint))
    reducao = ("","")
    while(1):
        t = scanner(lex)
        lista_tokens.append(t)
        
        if pilha[-1].estado == -1:
          estado_aux = df_tabela_sintatica[t.token][0]
          estado_aux = estado_aux[1:(len(estado_aux))]
        else:
          estado_aux = df_tabela_sintatica[t.token][int(pilha[-1].estado)]
          estado_aux = df_tabela_sintatica[t.token][int(pilha[-1].estado)][1:(len(estado_aux))]
        
        if pilha[-1].estado == -1:
          acao = df_tabela_sintatica[t.token][0][0]
        else:
          acao = df_tabela_sintatica[t.token][int(pilha[-1].estado)][0]
        if(acao == "s"):#empilhar
            sint.inicializar()
            estado = estado_aux
            sint.get(t)
            pilha.append(copy.deepcopy(sint))
            sint.inicializar()
            sint.estado = estado
            pilha.append(copy.deepcopy(sint))
            ultimo_lexema = t.lexema
            t = scanner(lex)
        elif(acao == "r"):#reduzir
            estado = estado_aux
            reducao = df_matriz_producoes['Nonterminal'][estado], df_matriz_producoes['producoes'][estado]
            for i in range(0,2*(contar_palavras(reducao[1]))):
                print(pilha[-1])
                pilha.pop()
            estado = pilha[-1].estado
            sint.inicializar()
            sint.token = reducao[0]
            pilha.append(copy.deepcopy(sint))
            estado_aux = df_tabela_sintatica[(reducao[0],estado)]
            sint.inicializar()
            sint.estado = estado_aux
            pilha.append(copy.deepcopy(sint))
        elif(acao == "acc"):#aceitar
            print("\nSUCESSO!\n")
        else:
            if(lista_tokens[i].token == tokens.EndOfFile):
                break # se o token encontrado for Fim de Arquivo, 
                      # o laço de repetição que busca o próximo token vai parar
            #print("\nERRO!\n")
        i += 1

def tokenizar(c,estado_atual): # essa função generaliza todas as entradas
    if (estado_atual == 2 or estado_atual == 4):
        if (c == 'e'):
            return c
        if (c == 'E'):
            return c
    if (estado_atual == 18):
        if (c != '"'): # enquanto o estado for 18, tudo estará dentro do literal, até que feche as aspas
            return 'A'
        else:
            return c
    if (estado_atual == 16):
        if (c != '}'): # enquanto o estado for 16, tudo estará dentro do comentário, até que feche a chave
            return 'A'
        else:
            return c
    if (c == '\n' or c == ' ' or c == '\t' or c == '\0'):
        return 'S'
    if (c.isalpha()): # se o caractere for alfabético, retorna L
        return 'L'
    if (c.isdigit()): # se o caractere for numérico, retorna D
        return 'D'
    else:
        return c

def erro(t, tk, estado_atual, estado_novo, ini_lexema, fim_lexema):
    token = matriz_de_estados_finais.get(estado_atual,None) # Verifica se o estado atual é final
    error = matriz_de_estados_finais.get(matriz_de_estados_lexica.get((t,-1),0),None) # vefifica se o erro é conhecido
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
                    tk.linha = lex.linha
                    tk.coluna = lex.coluna
                    tk.lexema = lex.codigo_mgol[ini_lexema:fim_lexema]
                    tk.erro = "ERRO1 – Falta um valor ou variavel depois desse Abre Parenteses: '" + tk.lexema + "'"
                    return tk
            if (token == tokens.OPR or token == tokens.OPM or token == tokens.RCB):
                if (error == tokens.id_ or error == tokens.num):
                    return 0
                else:
                    tk.linha = lex.linha
                    tk.coluna = lex.coluna
                    tk.lexema = lex.codigo_mgol[ini_lexema:fim_lexema]
                    tk.erro = "ERRO2 – Falta um valor ou variavel aqui: '" + tk.lexema + "'"
                    return tk
        else:
            tk.linha = lex.linha
            tk.coluna = lex.coluna
            tk.lexema = lex.codigo_mgol[ini_lexema:fim_lexema]
            tk.erro = "ERRO3 – Token duplicado: '" + tk.lexema + "'"
            return tk
    elif (token is not None and error is None):
        tk.linha = lex.linha
        tk.coluna = lex.coluna
        tk.lexema = lex.codigo_mgol[ini_lexema:fim_lexema]
        tk.erro = "ERRO4 – Caractere invalido: '" + tk.lexema + "'"
        return tk
    tk.linha = lex.linha
    tk.coluna = lex.coluna
    tk.lexema = lex.codigo_mgol[ini_lexema:fim_lexema]
    tk.erro = "ERRO5 – Caractere invalido: '" + tk.lexema + "'"
    return tk

def scanner(lex): # retorna o próximo token
    tk = Token()
    snt = Sintatico()  
    estado_atual = -1 # o estado inicial é -1
    estado_novo = -1
    ini_lexema = 0    # ini_lexema e fim_lexema marcam as posições de início e o fim de cada lexema
    fim_lexema = -1   # para retirar cada lexema da string que armazena o código completo
    for c in lex.codigo_mgol: # vou iterar caractere por caractere no código, até encontrar o próximo token
        if c == '\0' and estado_atual == -1 and estado_novo == -1:
            tk.linha  = lex.linha         
            tk.lexema = tokens.EndOfFile 
            tk.token  = tokens.EndOfFile 
            return tk
        fim_lexema +=1
        t = tokenizar(c,estado_atual)

        # a matriz de estados léxica é um dicionário. A chave é um par de (char,int), e o valor é um int
        # Chave = (entrada,estado_atual)
        # Valor = estado_novo
        estado_novo = matriz_de_estados_lexica.get((t,estado_atual),0)
        # em python, utilizando a função get(), posso passar a chave como parâmetro para obter o valor correspondente
        # se o par (entrada,estado_atual) não for encontrado, retorno o estado 0, que é o estado de erro

        if estado_novo == -1 and estado_atual == 20: # COMENTÁRIO
            #print("Linha ",lex.linha," [comentario] ",lex.codigo_mgol[ini_lexema:fim_lexema],"\n")
            ini_lexema = fim_lexema               
            if c == '\n' or c == '\t' or c == ' ':
                ini_lexema += 1
                if c == '\n':
                    lex.linha += 1
                    lex.coluna = 1
        elif estado_novo == -1 and estado_atual != -1: # LEXEMA AINDA NÃO ACABOU
            break
        elif estado_novo == -1 and estado_atual == -1: # LEXEMA ACABOU
            ini_lexema += 1
            if c == '\n':
                lex.linha += 1
                lex.coluna = 1
            if c == '\t' or c == ' ':
                lex.coluna += 1           
        elif estado_novo == 0: # TRATAMENTO DE ERRO
            er = erro(t, tk, estado_atual, estado_novo, ini_lexema, fim_lexema)
            if er == 0:
                break
            else:
                return er
        else:
            lex.coluna += 1
        estado_atual = estado_novo

    _token = matriz_de_estados_finais.get(estado_atual,None)  # verifico se o estado atual é final
    _lexema = lex.codigo_mgol[ini_lexema:fim_lexema] # pego o lexema do código

    if (_token is not None):
        lex.codigo_mgol = lex.codigo_mgol[fim_lexema:len(lex.codigo_mgol)] # atualizo o código deletando o que já foi lido
        if (_token == tokens.id_):
            if (not palavra_reservada(_lexema)):
                for s in lex.ids:
                    if(s.lexema == _lexema):
                        snt.estado = -2
                if(snt.estado == -1):
                    snt.lexema = _lexema
                    snt.token  = tokens.id_
                    lex.ids.append(snt)
                tk.tipo = ""
            else:
                _token = _lexema               # se o lexema for uma palavra reservada, pode ser que ele seja um tipo, e
                if (_token == tokens.inteiro): # os tipos definidos pela linguagem são int, literal e double
                    tk.tipo = "int"
                elif (_token == tokens.lit):
                    tk.tipo = "literal"
                elif (_token == tokens.real):
                    tk.tipo = "double"
                else:
                    tk.tipo = ""

        #print("Linha ",lex.linha," [",_token,"] ",_lexema)

        tk.linha   = lex.linha
        tk.coluna = lex.coluna
        tk.lexema  = _lexema
        tk.token   = _token
        return tk
    else: 
        if (estado_atual == 16 or estado_atual == 18): # se chegou aqui, então o usuário esqueceu de fechar as chaves ou aspas, 
            tk.linha = lex.linha                       # pq o estado de retorno sempre tem que ser final
            tk.coluna = lex.coluna
            tk.erro = "Esqueceu de fechar alguma coisa aqui: " + _lexema[0:7] + "..."
            return tk
        tk.linha = lex.linha
        tk.coluna = lex.coluna
        tk.lexema = _lexema
        return tk

#Main(Principal)

lex = Lex()
tokens = Lista_de_tokens()
analisador_sintatico(lex)
