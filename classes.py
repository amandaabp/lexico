

class Lex:
    codigo_mgol = ""
    qtd_linhas = 0
    linha = 1
    coluna = 1
    ids = []

class Token:
    def __str__(self):
        return "linha=%d,posição=%d,lexema=%s,Classe=%s,tipo=%s,erro=%s\n" % (self.linha, self.coluna, self.lexema, self.token, self.tipo, self.erro)
    linha = 1
    coluna = 1
    lexema = ""
    token = ""
    tipo = "Nulo"
    erro = ""
    estado = -1

class Semantic:
    def Semantic(self):
        self.estado = -1
        self.lexema = ""
        self.token = ""
        self.tipo = ""
        
    def get(self, t: Token):
        self.lexema = t.lexema
        self.token = t.token
        self.tipo = t.tipo

    def getS(self, s):
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


class Stack:
     def __init__(self):
         self.items = []

     def isEmpty(self):
         return self.items == []

     def push(self, item):
         self.items.append(item)

     def pop(self):
         return self.items.pop()

     def top(self):
         return self.items[len(self.items)-1]

     def size(self):
         return len(self.items)


class Semanticn:
    def Semantic(self):
        self.estado = -1
        self.lexeme = ""
        self.token = ""
        self.tipo = ""

    def get(self, t: Token):
        self.lexema = t.lexema
        self.token = t.token
        self.tipo = t.tipo

    def getS(self, s):
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

class RegrasSemanticas:
    def RegrasSemanticas(self):
        self.contador_temp = -1
        self.regra = 0
        self.gerar = True
        self.tabs = "\t"
    regra = 0
    contador_temp = -1
    gerar = True
    tabs = ""

class OutC:
    def OutC(self):
        cabecalho = "#include<stdio.h>\ntypedef char literal[256];\nvoid main(void)\n{"
        corpo = ""
        declaracoes = ""
    cabecalho =  "#include<stdio.h>\ntypedef char literal[256];\nvoid main(void)\n{"
    declaracoes = ""
    corpo = ""

class Lista_de_tokens:
    num = "num"
    id_ = "id"
    comentario = "comentario"
    literal = "literal"
    OPR = "OPR"
    RCB = "RCB"
    OPM = "OPM"
    AB_P = "AB_P"
    FC_P = "FC_P"
    PT_V = "PT_V"
    VIR = "VIR"
    ERRO = "ERRO"
    EndOfFile = "EndOfFile"
    inicio = "inicio"
    varinicio = "varinicio"
    varfim = "varfim"
    escreva = "escreva"
    leia = "leia"
    se = "se"
    entao = "entao"
    fimse = "fimse"
    faca_ate = "faca_ate"
    fimfaca = "fimfaca"
    fim = "fim"
    inteiro = "inteiro"
    lit = "lit"
    real = "real"

