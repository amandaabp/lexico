import collections

class Lex:
    estado_novo  = -1
    estado_atual = -1
    lexema       = "" 
    token        = ""
    tipo         = ""
    codigo_mgol  = ""
    qtd_linhas   = 0

class Token:
    def __str__(self):
        return "linha=%d,posição=%d,lexema=%s,token=%s,tipo=%s,erro=%s\n" % (self.linha,self.coluna,self.lexema,self.token,self.tipo,self.erro)
    linha   = 1
    coluna  = 0
    lexema  = ""
    token   = ""
    tipo    = ""
    erro    = ""

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
    ('',-1) : 15 ,
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
    1  : tokens.id_  ,
    2  : tokens.num  ,
    4  : tokens.num  ,
    7  : tokens.num  ,
    8  : tokens.fim  ,
    9  : tokens.OPR  ,
    10 : tokens.OPR  ,
    11 : tokens.RCB  ,
    12 : tokens.OPR  ,
    13 : tokens.AB_P ,
    14 : tokens.FC_P ,
    15 : tokens.PT_V ,
    17 : tokens.OPM  ,
    19 : tokens.lit  ,
    20 : tokens.comentario
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

def ler_arquivo_mgol(lex):
    f = open("mgol.alg", "r")
    lex.qtd_linhas = len(open("mgol.alg").readlines())
    lex.codigo_mgol = f.read() 

def analisador_lexico(lex):    
    ler_arquivo_mgol(lex)
    print(lex.codigo_mgol)
    while(1):
        tok = proximo_token(lex)
        print(tok)

def tokenizar(c,estado_atual):
    if (estado_atual == 2 or estado_atual == 4):
        if (c == 'e'):
            return c
        if (c == 'E'):
            return c
    if (estado_atual == 18):
        if (c != '"'):
            return 'A'
        else:
            return c
    if (estado_atual == 16):
        if (c != '}'):
            return 'A'
        else:
            return c
    if (c == '\n' or c == ' ' or c == '\t' or c == '\0'):
        return 'S'
    if (c.isalpha()): 
        return 'L'
    if (c.isdigit()):
        return 'D'
    else:
        return c

def proximo_token(lex):
    tk = Token()
    ini_lexema = 0
    for c in lex.codigo_mgol:
        if c == '\0' and lex.estado_atual == -1 and lex.estado_novo == -1:
            tk.lexema = tokens.EndOfFile
            tk.token  = tokens.EndOfFile
            return tk      
        t = tokenizar(c,lex.estado_atual)
        lex.estado_novo = matriz_de_estados_lexica[(t,lex.estado_atual)]
        if lex.estado_novo == -1 and lex.estado_atual == 20:
            print("Linha ",tk.linha," [comentario] ",lex.codigo_mgol[ini_lexema:tk.coluna])
            ini_lexema = tk.coluna                
            if c == '\n' or c == '\t' or c == ' ':
                ini_lexema += 1
                if c == '\n':
                    tk.linha += 1
                    tk.coluna = 1
        elif lex.estado_novo == -1 and lex.estado_atual != -1:
            break
        elif lex.estado_novo == -1 and lex.estado_atual == -1:
            if c == '\n':
                tk.linha += 1
                tk.coluna = 1
            ini_lexema += 1
        elif lex.estado_novo == 0:
            token = matriz_de_estados_finais[lex.estado_atual]
            error = matriz_de_estados_finais[matriz_de_estados_lexica[(t,-1)]]
            if token and error:
                if token != error:
                    if (token == tokens.id_ or token == tokens.num):
                        if (lex.codigo_mgol[ini_lexema:tk.coluna] == tokens.se):
                            if (error == tokens.AB_P):
                                break
                        if (error == tokens.PT_V or error == tokens.OPR or error == tokens.OPM or error == tokens.FC_P):
                            break
                    if (token == tokens.AB_P):
                        if (error == tokens.id_ or error == tokens.num):
                            break
                        else:
                            tk.lexema = lex.codigo_mgol[ini_lexema:tk.coluna]
                            tk.erro = "Falta um valor ou variavel depois desse Abre Parenteses: '" + tk.lexema + "'"
                            return tk
                    if (token == tokens.OPR or token == tokens.OPM or token == tokens.RCB):
                        if (error == tokens.id_ or error == tokens.num):
                            break
                        else:
                            tk.lexema = lex.codigo_mgol[ini_lexema:tk.coluna]
                            tk.erro = "Falta um valor ou variavel aqui: '" + tk.lexema + "'"
                            return tk
                else:
                    tk.lexema = lex.codigo_mgol[ini_lexema:tk.coluna]
                    tk.erro = "Token duplicado: '" + tk.lexema + "'"
                    return tk
            elif (token and not error):
                tk.lexema = lex.codigo_mgol[ini_lexema:tk.coluna]
                tk.erro = "Caractere invalido: '" + tk.lexema + "'"
                return tk
            tk.lexema = lex.codigo_mgol[ini_lexema:tk.coluna]
            tk.eerrorror = "Caractere invalido: '" + tk.lexema + "'"
            return tk
        else:
            tk.coluna += 1
        lex.estado_atual = lex.estado_novo

    _token = matriz_de_estados_finais[lex.estado_atual]
    _lexema = lex.codigo_mgol[ini_lexema:tk.coluna]

    if (_token):
        lex.codigo_mgol = lex.codigo_mgol[tk.coluna+1:len(lex.codigo_mgol)]

        if (_token == tokens.id_):
            if (not palavra_reservada(_lexema)):
                tk.tipo = ""
            else:
                _token = _lexema                
                if (_token == tokens.inteiro):
                    tk.tipo = "int"
                elif (_token == tokens.lit):
                    tk.tipo = "literal"
                elif (_token == tokens.real):
                    tk.tipo = "double"
                else:
                    tk.tipo = ""

        print("Linha ",tk.linha," [",_token,"] ",_lexema)

        tk.lexema  = _lexema
        tk.token   = _token
        return tk
    else:
        if (lex.estado_atual == 16 or lex.estado_atual == 18):
            tk.erro = "Vc esqueceu de fechar alguma coisa aqui: " + _lexema[0:7] + "..."
            return tk
        tk.lexema = _lexema
        return tk

lex = Lex()
tokens = Lista_de_tokens()
analisador_lexico(lex)
