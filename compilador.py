import collections
from numpy import flatiter
import pandas as pd
import math
import copy
import classes as classes
import matrizes as matrizes
import lexico as lexico

df_tabela_sintatica = pd.read_csv('tabela_sintatica_nova.csv', sep=';')
df_matriz_follow = pd.read_csv('matriz_follow.csv', sep=';')
df_matriz_producoes = pd.read_csv(
    'matriz_producoes.csv', sep=';', encoding='utf-8')


pilha = classes.Stack()  # pilha para auxiliar na analise Sintática
pilha.push(0)

tokens = classes.Lista_de_tokens()
matriz_de_estados_finais = matrizes.matriz_de_estados_finais
matriz_de_estados_lexica = matrizes.matriz_de_estados_lexica


def aplicar_regra_semantica(semR, ultimo_pop, pilha, expression, lex, outC, ids_declarados, expression_declarada, found):
    tk = classes.Token()
    aux = ""
    sem = classes.Semantic()
    global regrasArg
    achou =  False

    # P' → P ou P→ inicio V A ou V→ varincio LV ou LV→ D LV
    if semR.regra == 1 or semR.regra == 2 or semR.regra == 3 or semR.regra == 4:
        return

    # LV -> varfim;
    elif semR.regra == 5:
        outC.corpo += "\n"

    # D→ TIPO L;
    elif semR.regra == 6:
        for id in lex.ids:
            if id.lexema == ultimo_pop.lexema:
                sem.tipo = ultimo_pop.tipo

        pilha.top().tipo = ultimo_pop.tipo
        # outC.declaracoes += "\n"+ semR.tabs + ultimo_pop.tipo + " " + ultimo_pop.lexema + ";"
        ultimo_pop.inicializar()

    # L→ id, L
    elif semR.regra == 7:
        for id in lex.ids:
            if id.lexema == ultimo_pop.lexema:
                sem.tipo = ultimo_pop.tipo

        pilha.top().tipo = ultimo_pop.tipo
        outC.declaracoes += "\n" + semR.tabs + " " + ultimo_pop.lexema + ";"
        ultimo_pop.inicializar()
    # L→ id
    elif semR.regra == 8:
        for id in lex.ids:
            if id.lexema == ultimo_pop.lexema:
                sem.tipo = ultimo_pop.tipo

        pilha.top().tipo = ultimo_pop.tipo   
        outC.declaracoes += "\n" + semR.tabs + \
            ultimo_pop.tipo + " " + ultimo_pop.lexema + ";"
        ultimo_pop.inicializar()
        return

    # TIPO→ int  ou  TIPO→ real  ou TIPO→ lit
    elif semR.regra == 9 or semR.regra == 10 or semR.regra == 11:
        lex.ids[-1].tipo = ultimo_pop.tipo
        pilha.top().tipo = ultimo_pop.tipo
    # A→ ES A
    elif semR.regra == 12:
        return
    # ES→ leia id
    elif semR.regra == 13:
        for id in lex.ids:
            if id.lexema == ids_declarados[-1].lexema:
                sem.tipo = id.tipo
                ultimo_pop.tipo = id.tipo
                ultimo_pop.lexema = id.lexema

        if ultimo_pop.tipo == "literal":
            outC.corpo += "\n" + semR.tabs+"scanf(\"%s\", "+ultimo_pop.lexema+");"
        elif ultimo_pop.tipo == "int":
            outC.corpo += "\n" + semR.tabs + \
                "scanf(\"%d\", &" + ultimo_pop.lexema + ");"
        elif ultimo_pop.tipo == "double":
            outC.corpo += "\n" + semR.tabs + \
                "scanf(\"%lf\", &" + ultimo_pop.lexema + ");"
        else:
            print("ERRO! Variavel", ultimo_pop.lexema, " não declarada")

        ultimo_pop.inicializar()

        return
    # ES→ escreva ARG;
    elif semR.regra == 14:
        ultimo_pop = copy.deepcopy(regrasArg)
        for id in lex.ids:
            if id.lexema == ultimo_pop.lexema:
                sem.tipo = ultimo_pop.tipo

        if ultimo_pop.tipo != 'Nulo' and ultimo_pop.tipo != '':
            if ultimo_pop.tipo == "literal":
                outC.corpo += "\n" + semR.tabs + \
                    "printf(\"%s\", " + ultimo_pop.lexema + ");"
            elif ultimo_pop.tipo == "int":
                outC.corpo += "\n" + semR.tabs + \
                    "printf(\"%d\", " + ultimo_pop.lexema + ");"
            elif ultimo_pop.tipo == "double":
                outC.corpo += "\n" + semR.tabs + \
                    "printf(\"%lf\", " + ultimo_pop.lexema + ");"
        else:
            outC.corpo += "\n" + semR.tabs + "printf(" + ultimo_pop.lexema + ");"

        ultimo_pop.inicializar()

        return
    # ARG→ literal  ou ARG→ num
    elif semR.regra == 15 or semR.regra == 16:
        regrasArg = copy.deepcopy(ultimo_pop)
        pilha.top().lexema = ultimo_pop.lexema
        pilha.top().tipo = ultimo_pop.tipo
        return
    # ARG→ id
    elif semR.regra == 17:
        for id in lex.ids:
            if id.lexema == ultimo_pop.lexema:
                achou = True
                if len(id.tipo) != 0:
                    pilha.top().lexema = id.lexema
                    pilha.top().tipo = id.tipo
                    ultimo_pop.tipo = id.tipo
                    #ultimo_pop.inicializar()
                    regrasArg = copy.deepcopy(ultimo_pop)

        if not pilha.top().tipo or not achou:
            print("ERRO! Variavel  nao definida!")
            semR.gerar = False

        return

    # A→ CMD A
    elif semR.regra == 18:
        return

    # CMD→ id rcb LD;
    elif semR.regra == 19:
        for id in lex.ids:
            if id.lexema == ultimo_pop.lexema:
                if not id.tipo:
                    achou = True

        if achou:
            print("ERRO! Variavel nao definida!")
        elif not expression:
            if ultimo_pop.tipo != '':
                for id in lex.ids:
                    if id.token == ultimo_pop.token and id.lexema == ultimo_pop.lexema:
                        ultimo_pop.tipo = id.tipo
            if len(expression_declarada) != 0:
                if ultimo_pop.tipo != expression_declarada[-1].tipo:
                    print("ERRO! Variaveis ", ultimo_pop.lexema, " e ",
                        expression[0].lexema, " de tipos diferentes!")
                    semR.gerar = False

                outC.corpo += "\n" + semR.tabs + ultimo_pop.lexema + \
                    " = " + expression_declarada[-1].lexema + ";"
                del expression_declarada[:]
            else:
                outC.corpo += "\n" + semR.tabs + ultimo_pop.lexema + \
                " = " + "T" + str(semR.contador_temp) + ";"
        else:
            if len(expression_declarada) != 0:
                outC.corpo += "\n" + semR.tabs + ultimo_pop.lexema + \
                    " = " + expression_declarada[-1].lexema + ";"
            else:
                outC.corpo += "\n" + semR.tabs + ultimo_pop.lexema + \
                    " = " + "T" + str(semR.contador_temp) + ";"

        ultimo_pop.inicializar()
        return

    # LD→ OPRD opm OPRD
    elif semR.regra == 20:
        for id in lex.ids:
            if id.tipo != expression[0].tipo and not id.tipo:
               print("ERRO! Variaveis de tipos diferentes dentro da expressao!")
               semR.gerar = False
               return
            elif id.tipo == "lit":
                print(
                    "ERRO! Variaveis literais nao podem estar dentro de uma expressao!")
                semR.gerar=False
                return
        semR.contador_temp = semR.contador_temp + 1
        sem.lexema = "T" + str(semR.contador_temp)
        #sem.token = tk.id
        sem.token = tk.token
        sem.tipo = ultimo_pop.tipo
        #lex.ids.append(sem)
        if sem.tipo == 'Nulo' or sem.tipo == '' :
            sem.tipo = expression[-1].tipo

        pilha.top().lexema = sem.lexema
        outC.declaracoes += "\n" + semR.tabs + sem.tipo + " " + sem.lexema + ";"
        outC.corpo += "\n" + semR.tabs + sem.lexema + " = "

        for id in expression_declarada:
            outC.corpo += id.lexema
        
        outC.corpo += ";"
        sem.inicializar()
        ultimo_pop.inicializar()
        del expression_declarada[:]
        del expression[:]
        return
        
    # LD→ OPRD
    elif semR.regra == 21:
        pilha.top().lexema = ultimo_pop.lexema
        pilha.top().tipo = ultimo_pop.tipo
        return

    # OPRD→ id
    elif semR.regra == 22:
        for id in lex.ids:
            if id.lexema == ultimo_pop.lexema:
                ultimo_pop.tipo = id.tipo
                achou = True
                return
        if not achou:
            print("Erro: Variável", ultimo_pop.lexema ,"não declarada" )
            semR.gerar = False
            return
        
        expression.append(copy.deepcopy(ultimo_pop))
        ultimo_pop.inicializar()
        return
    # OPRD→ num    
    elif semR.regra == 23:
        pilha.top().lexema = ultimo_pop.lexema
        pilha.top().tipo = ultimo_pop.tipo

        for c in ultimo_pop.lexema:
            if c == '.':
                ultimo_pop.tipo = "double"
        if ultimo_pop.tipo == 'Nulo' :
            ultimo_pop.tipo = "int"
        
        expression.append(copy.deepcopy(ultimo_pop))
        return
    # A→ COND A
    elif semR.regra == 24:
        return
    # COND→ CAB CP
    elif semR.regra == 25:
        semR.tabs = semR.tabs[0: len(semR.tabs) - 1]
        outC.corpo += "\n" + semR.tabs + "}"
        return
    # CAB→ se (EXP_R) então
    elif semR.regra == 26:
        sem.lexema = "T" + str(semR.contador_temp)
        outC.corpo += "\n" + semR.tabs + "if ( " + sem.lexema + " )\n" + semR.tabs + "{"
        semR.tabs += "\t"
        ultimo_pop.inicializar()
        return
    # EXP_R→ OPRD opr OPRD
    elif semR.regra == 27:
        for id in lex.ids:
            if id.tipo != expression[0].tipo and not id.tipo:
                print("Erro: Operandos com tipos incompatíveis")
                semR.gerar = False
                return
            elif id.tipo == "lit":
                print("Erro: Operandos com tipos incompatíveis")
                semR.gerar = False
                return
        semR.contador_temp = semR.contador_temp + 1
        sem.lexema = "T" + str(semR.contador_temp)
        sem.token = tk.token
        sem.tipo = ultimo_pop.tipo
        if sem.tipo == 'Nulo' or sem.tipo == '' :
            sem.tipo = expression[-1].tipo
        #lex.ids.append(sem)

        pilha.top().lexema = sem.lexema
        outC.declaracoes += "\n\t" + sem.tipo + " " + sem.lexema + ";"
        outC.corpo +=  "\n" + semR.tabs + sem.lexema + " = "
        for s in expression_declarada:    
            outC.corpo += s.lexema
        
        outC.corpo += ";"
        sem.inicializar()
        ultimo_pop.inicializar()
        del expression_declarada[:]
        del expression[:]
        return
    # CP→ ES CP ou CP→ CMD CP ou CP→ COND CP ou CP→ fimse ou A→ R A
    elif semR.regra == 28 or semR.regra == 29 or semR.regra == 30 or semR.regra == 31  or semR.regra == 32:
        return
    # R → facaAte (EXP_R) CP_R
    elif semR.regra == 33:
        return

def analisador_sintatico_antigo(lex):
    erroSint=False
    lexico.ler_arquivo_mgol(lex)
    t=lexico.scanner(lex)
    a=t.token
    tAntigo=t
    print('\nAnalisador sintático\n')
    ultimo_pop= classes.Semantic()
    sem= classes.Semantic()
    semregras= classes.Semanticregras()
    expression=[]
    outC= classes.OutC

    while(1):
        if a != '':
            # topo da pilha
            s=pilha.items[len(pilha.items)-1]

            # busca acao na tabela sintatica
            estado_aux=df_tabela_sintatica[a][s]
            aux=df_tabela_sintatica[a][s][1:(len(estado_aux))]
            acao=df_tabela_sintatica[a][s][0]

            if acao == 's' or acao == 'r' or acao == 'E':
                linhaEstado=int(aux)

            # empilhar
            if acao == 's':
                sem.inicializar()
                sem.get(t)
                pilha.push(t)
                pilha.push(linhaEstado)

                if (sem.token == tokens.OPR or sem.token == tokens.OPM):
                    expression.append(sem)

                if erroSint:
                    t=tAntigo
                    erroSint=False
                else:
                    t=lexico.scanner(lex)

                a=t.token

                while t.linha < 0:
                    # parseLexicalError(lex, tok, tokens);
                    semregras.gerar=False

            # reduzir
            elif acao == 'r':
                # produção gerada
                aux2=df_matriz_producoes['Nonterminal'][linhaEstado]
                linhaProd=linhaEstado
                semregras.regra=linhaEstado + 1

                print('Regra: ', df_matriz_producoes['Nonterminal'][linhaProd],
                      '->', df_matriz_producoes['producoes'][linhaProd])

                # desempilha de acordo com a quantidade de produções
                for i in range(df_matriz_producoes['tamProd'][linhaEstado]):
                    pilha.pop()
                    if semregras.gerar:
                        ultimo_pop.get(pilha.top())
                    pilha.pop()

                linhaEstado=pilha.items[len(pilha.items)-1]

                #sem.inicializar()

                pilha.push(t)
                aux_estado=df_tabela_sintatica[aux2][linhaEstado]

                if semregras.gerar:
                    aplicar_regra_semantica(semregras, ultimo_pop,
                                      pilha, expression, lex, outC)

                sem.inicializar()
                pilha.push(
                    int(df_tabela_sintatica[aux2][linhaEstado][1:(len(aux_estado))]))




            # aceita
            elif acao == 'a':
                print('\n----- ACEITA -----\n')

                #if semregras.gerar:
                outC.corpo += "\n}"
                print(" Arquivo .c gerado.")
                # Abre(ou cria) um arquivo .c com o nome do arquivo em mgol que está sendo analisado 
                arqDestino = open(str("out")+".c", "w+")
                # Imprime um elemento da lista TextoArquivo
                arqDestino.write( outC.cabecalho + outC.declaracoes + outC.corpo)
                # Fim do arquivo
                arqDestino.write("}\n")
                arqDestino.close()
                print("Arquivo " + "out" +  ".c gerado")
                #else:
                    #print(" Erros encontrados, Arquivo .c nao foi gerado.")
                #return
            # erro
            elif acao == 'E':
                faltSib={}
                impriLista=""

                linhas=df_tabela_sintatica.values[s]
                colunas=df_tabela_sintatica.columns

                for k, v in zip(linhas, colunas):
                    if v != 'estado':
                        if k != '0' and k != 0:
                            if k[0] != 'E':
                                faltSib.update({v: k})
                                nomeToken=eqToken(v)
                                impriLista=impriLista + " " + str(nomeToken)
                print("\nErro Sintático.\nLinha: ", t.linha, "Coluna: ",
                      t.coluna, "\n Faltando símbolo(s):", impriLista)

                if len(faltSib) == 1:
                    print("\tTratamento de erro. Inserindo símbolo ausente...")
                    chave=[key for key in faltSib.keys()]

                    tAntigo=t

                    a=chave[0]

                    erroSint=True

                    pilha.pop()
                    pilha.pop()
                    pilha.push(chave[0])
                    pilha.push(int(aux))

                    print("\nInserindo para continuar a análise.")
                    print("\nFim de tratamento de erro\n")
                else:
                    print("\nTratamento de erro.")
                    listaFollow=df_matriz_follow['FOLLOW'][int(s)-1]
                    aux=1

                    while (aux):
                        while True:
                            t=lexico.scanner(lex)
                            a=t.token

                            if a == "$":
                                print("Fim de tratamento de erro\n")
                                print("Finalizada. Falha!")
                                return

                            elif a != "comentario":
                                break

                        if listaFollow == '0':
                            print("A análise não conseguiu se recuperar do erro: ")
                            break
                        else:
                            for token in listaFollow.split():
                                if token == a:
                                    aux=0
                                    break

                        x=df_matriz_producoes['tamProd'][int(s)]
                        if x:
                            for i in range(0, int(x)):
                                pilha.pop()
                                pilha.pop()

                        print("Recuperando análise sintática\n")
        else:
            print('Erro lexico' + t.erro)

            if t.erro.split == 'ERRO2' or t.erro.split == 'ERRO5':
                print('Esperava argumento "num"'+'\n' +
                    'Linha : {} | Coluna : {}'.format(t.linha, t.coluna-2))

            t=lexico.scanner(lex)
            a=t.token

def analisador_sintatico(lex):
    erroSint=False
    lexico.ler_arquivo_mgol(lex)
    tok = classes.Token()
    sem = classes.Semantic()
    ultimo_pop = classes.Semantic()
    semregras = classes.RegrasSemanticas()
    pilha = classes.Stack()  # pilha para auxiliar na analise Sintática
    pilha.push(0)
    i = 0
    estado = -1
    estadoAux = -1
    lastLexeme = ""
    errorHandle = ""
    expression=[]
    outC = classes.OutC()
    expression_declarada = []
    cont_expres = False
    ids_declarados = []
    found = False
    tok=lexico.scanner(lex)

    if tok.linha < 0 and not tok.token:
        print("ERRO - linha", tok.linha, " - ", tok.token)
    
    pilha.push(copy.deepcopy(sem))

    while(1):
        if pilha.top().estado == -1:
            s = 0
        else:
            s = pilha.top().estado

        # busca acao na tabela sintatica
        aux=df_tabela_sintatica[tok.token][s]
        estado_aux= df_tabela_sintatica[tok.token][s][1:(len(aux))]
        acao=df_tabela_sintatica[tok.token][s][0]

        if acao == 's' or acao == 'r' or acao == 'E':
            estado= int(estado_aux)

        if (acao == "s"):
            sem.inicializar()
            sem.get(tok)
            pilha.push(copy.deepcopy(sem))

            if  (sem.token == tokens.OPR or sem.token == tokens.OPM):
                expression.append(copy.deepcopy(sem))
            
            sem.inicializar()
            sem.estado = estado
            pilha.top().estado = estado
            #pilha.push(copy.deepcopy(sem))

            lastLexeme = tok.lexema
            tok = lexico.scanner(lex)
            if tok.token == "id":
                ids_declarados.append(tok)
            
            if lastLexeme == '(' or lastLexeme == '<-':
                cont_expres = True
            elif tok.lexema == ')' or tok.lexema == ';' :
                cont_expres = False
            
            if cont_expres :
                expression_declarada.append(tok)
                

            while tok.linha < 0:
                #fazer erro lexico
                semregras.gerar = False

        elif (acao == "r"):
            reduction = df_matriz_producoes['Nonterminal'][estado]
            semregras.regra= estado + 1

            print('Regra: ', df_matriz_producoes['Nonterminal'][estado],
                    '->', df_matriz_producoes['producoes'][estado])

            # desempilha de acordo com a quantidade de produções
            for i in range(df_matriz_producoes['tamProd'][estado]):
                if semregras.gerar:
                    ultimo_pop.get(copy.deepcopy(pilha.top()))
                    
                pilha.pop()
                if ultimo_pop.tipo == '':
                    ultimo_pop.tipo = pilha.top().tipo

            estado = pilha.top().estado

            if pilha.top().estado == -1:
                estado = 0
            else:
                estado = pilha.top().estado

            #sem.inicializar()
            #sem.token = reduction
            pilha.push(copy.deepcopy(sem))

            if semregras.gerar:
                aplicar_regra_semantica(semregras, ultimo_pop, pilha, expression, lex, outC, ids_declarados, expression_declarada, found)
            
            aux_estado= df_tabela_sintatica[reduction][estado]
            estado_aux =  int(df_tabela_sintatica[reduction][estado][1:(len(aux_estado))])
            sem.inicializar()
            sem.estado = estado_aux
            pilha.top().estado = estado_aux


        # aceita
        elif acao == 'a':
            print('\n----- ACEITA -----\n')

            #if semregras.gerar:
            outC.corpo += "\n}"
            print(" Arquivo .c gerado.")
            # Abre(ou cria) um arquivo .c com o nome do arquivo em mgol que está sendo analisado 
            arqDestino = open(str("out")+".c", "w+")
            # Imprime um elemento da lista TextoArquivo
            arqDestino.write( outC.cabecalho + outC.declaracoes + outC.corpo)
            # Fim do arquivo
            arqDestino.write("}\n")
            arqDestino.close()
            print("Arquivo " + "out" +  ".c gerado")
            #else:
                #print(" Erros encontrados, Arquivo .c nao foi gerado.")
            return
        # erro
        elif acao == 'E':
            faltSib={}
            impriLista=""

            linhas=df_tabela_sintatica.values[s]
            colunas=df_tabela_sintatica.columns

            for k, v in zip(linhas, colunas):
                if v != 'estado':
                    if k != '0' and k != 0:
                        if k[0] != 'E':
                            faltSib.update({v: k})
                            nomeToken=lexico.eqToken(v)
                            impriLista=impriLista + " " + str(nomeToken)
            print("\nErro Sintático.\nLinha: ", tok.linha, "Coluna: ",
                    tok.coluna, "\n Faltando símbolo(s):", impriLista)

            if len(faltSib) == 1:
                print("\tTratamento de erro. Inserindo símbolo ausente...")
                chave=[key for key in faltSib.keys()]

                tAntigo=tok

                a=chave[0]

                erroSint=True

                pilha.pop()
                pilha.pop()
                pilha.push(chave[0])
                pilha.push(int(aux))

                print("\nInserindo para continuar a análise.")
                print("\nFim de tratamento de erro\n")
            else:
                print("\nTratamento de erro.")
                listaFollow=df_matriz_follow['FOLLOW'][int(s)-1]
                aux=1

                while (aux):
                    while True:
                        tok=lexico.scanner(lex)
                        a=tok.token

                        if a == "$":
                            print("Fim de tratamento de erro\n")
                            print("Finalizada. Falha!")
                            return

                        elif a != "comentario":
                            break

                    if listaFollow == '0':
                        print("A análise não conseguiu se recuperar do erro: ")
                        break
                    else:
                        for token in listaFollow.split():
                            if token == a:
                                aux=0
                                break

                    x=df_matriz_producoes['tamProd'][int(s)]
                    if x:
                        for i in range(0, int(x)):
                            pilha.pop()
                            pilha.pop()

                    print("Recuperando análise sintática\n")
    else:
        print('Erro lexico' + tok.erro)

        if tok.erro.split == 'ERRO2' or tok.erro.split == 'ERRO5':
            print('Esperava argumento "num"'+'\n' +
                'Linha : {} | Coluna : {}'.format(tok.linha, tok.coluna-2))

        tok=lexico.scanner(lex)
        a=tok.token

#função para interpretar alguns tokens
def eqToken(token):    
    tokenTrad = token
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

# Main(Principal)
lex = classes.Lex()
tokens = classes.Lista_de_tokens()
analisador_sintatico(lex)
