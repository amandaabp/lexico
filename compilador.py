import collections

Tokens = {
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
	"leia"      :"leia"         ,
	"se"        :"se"           ,
	"entao"     :"entao"        ,
	"senao"     :"senao"        ,
	"fimse"     :"fimse"        ,
	"fim"       :"fim"          ,
	"inteiro"   :"inteiro"      ,
	"lit"       :"lit"          ,
	"real"      :"real"         ,
}

Matriz_de_estados_lexica = {
    ('S',0) : 0,
    ('S',-1) : -1,
    ('S',-1) : -1,
    ('S',-1) : -1,
    ('S',-1) : -1,
    ('S',-1) : -1,
    ('S',-1) : -1,
    ('S',-1) : -1,
    ('S',-1) : -1,
    ('S',-1) : -1,
    ('S',-1) : -1,
    ('S',-1) : -1
}

print("oi")