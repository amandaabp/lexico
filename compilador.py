import collections

class Lex:
    estado = -1 
    lexema = "" 
    token  = ""
    tipo   = ""
    codigo_mgol = ""
    qtd_linhas = 0

class Token:
    linha   = 0
    coluna  = 0
    lexema  = ""
    token   = ""
    tipo    = ""
    erro    = ""

tokens = {
    "num"       :"num"          ,
    "id"        :"id"           ,
    "comentario":"comentario"   ,
    "OPR"       :"OPR"          ,
    "RCB"       :"RCB"          ,
    "OPM"       :"OPM"          ,
    "AB_P"      :"AB_P"         ,
    "FC_P"      :"FC_P"         ,
    "PT_V"      :"PT_V"         ,
    "ERRO"      :"ERRO"         ,
    "EndOfFile" :"EndOfFile"    ,
    "inicio"    :"inicio"       ,
    "varinicio" :"varinicio"    ,
    "varfim"    :"varfim"       ,
    "escreva"   :"escreva"      ,
    "leia"      :"leia"         ,
    "se"        :"se"           ,
    "entao"     :"entao"        ,
    "fimse"     :"fimse"        ,
    "faca-ate"  :"faca-ate"     ,
    "fimfaca"   :"fimfaca"      ,
    "fim"       :"fim"          ,
    "inteiro"   :"inteiro"      ,
    "lit"       :"lit"          ,
    "real"      :"real"         ,
}

matriz_de_estados_lexica = {
    ('S',0 ) : 0  ,
    ('S',1 ) : 0  ,
    ('S',1 ) : 0  ,
    ('S',2 ) : 0  ,
    ('S',4 ) : 0  ,
    ('S',7 ) : 0  ,
    ('S',8 ) : 0  ,
    ('S',9 ) : 0  ,
    ('S',10) : 0  ,
    ('S',11) : 0  ,
    ('S',12) : 0  ,
    ('S',13) : 0  ,
    ('S',14) : 0  ,
    ('S',15) : 0  ,
    ('S',17) : 0  ,
    ('S',19) : 0  ,
    ('S',20) : 0  ,
 
    (';',1 ) : 0  , 
    (';',2 ) : 0  ,
    (';',4 ) : 0  ,
    (';',7 ) : 0  ,
    (';',19) : 0  ,
    ('L',-1) : 1  , 
    ('L',1 ) : 1  , 
    ('_',1 ) : 1  , 

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

def ler_arquivo_mgol(lex):
    f = open("mgol.alg", "r")
    lex.qtd_linhas = len(open("mgol.alg").readlines())
    lex.codigo_mgol = f.read() 

def analisador_lexico(lex):    
    ler_arquivo_mgol(lex)
    print(lex.codigo_mgol)

lex = Lex()
analisador_lexico(lex)
