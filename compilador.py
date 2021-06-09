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


def applySemanticRule(semR, lastPop, pilha, expression, lex, outC, ids_declarados, expression_declarada, found):
    tk = classes.Token()
    aux = ""
    sem = classes.Semantic()
    global regrasArg
    achou =  False

    # P' → P ou P→ inicio V A ou V→ varincio LV ou LV→ D LV
    if semR.rule == 1 or semR.rule == 2 or semR.rule == 3 or semR.rule == 4:
        return

    # LV -> varfim;
    elif semR.rule == 5:
        outC.body += "\n"

    # D→ TIPO L;
    elif semR.rule == 6:
        for id in lex.ids:
            if id.lexema == lastPop.lexema:
                sem.tipo = lastPop.tipo

        pilha.top().tipo = lastPop.tipo
        # outC.declarations += "\n"+ semR.tabs + lastPop.tipo + " " + lastPop.lexema + ";"
        lastPop.inicializar()

    # L→ id, L
    elif semR.rule == 7:
        for id in lex.ids:
            if id.lexema == lastPop.lexema:
                sem.tipo = lastPop.tipo

        pilha.top().tipo = lastPop.tipo
        outC.declarations += "\n" + semR.tabs + " " + lastPop.lexema + ";"
        lastPop.inicializar()
    # L→ id
    elif semR.rule == 8:
        for id in lex.ids:
            if id.lexema == lastPop.lexema:
                sem.tipo = lastPop.tipo

        pilha.top().tipo = lastPop.tipo   
        outC.declarations += "\n" + semR.tabs + \
            lastPop.tipo + " " + lastPop.lexema + ";"
        lastPop.inicializar()
        return

    # TIPO→ int  ou  TIPO→ real  ou TIPO→ lit
    elif semR.rule == 9 or semR.rule == 10 or semR.rule == 11:
        lex.ids[-1].tipo = lastPop.tipo
        pilha.top().tipo = lastPop.tipo
    # A→ ES A
    elif semR.rule == 12:
        return
    # ES→ leia id
    elif semR.rule == 13:
        for id in lex.ids:
            if id.lexema == ids_declarados[-1].lexema:
                sem.tipo = id.tipo
                lastPop.tipo = id.tipo
                lastPop.lexema = id.lexema

        if lastPop.tipo == "literal":
            outC.body += "\n" + semR.tabs+"scanf(\"%s\", "+lastPop.lexema+");"
        elif lastPop.tipo == "int":
            outC.body += "\n" + semR.tabs + \
                "scanf(\"%d\", &" + lastPop.lexema + ");"
        elif lastPop.tipo == "double":
            outC.body += "\n" + semR.tabs + \
                "scanf(\"%lf\", &" + lastPop.lexema + ");"
        else:
            print("ERRO! Variavel", lastPop.lexema, " não declarada")

        lastPop.inicializar()

        return
    # ES→ escreva ARG;
    elif semR.rule == 14:
        lastPop = copy.deepcopy(regrasArg)
        for id in lex.ids:
            if id.lexema == lastPop.lexema:
                sem.tipo = lastPop.tipo

        if lastPop.tipo != 'Nulo' and lastPop.tipo != '':
            if lastPop.tipo == "literal":
                outC.body += "\n" + semR.tabs + \
                    "printf(\"%s\", " + lastPop.lexema + ");"
            elif lastPop.tipo == "int":
                outC.body += "\n" + semR.tabs + \
                    "printf(\"%d\", " + lastPop.lexema + ");"
            elif lastPop.tipo == "double":
                outC.body += "\n" + semR.tabs + \
                    "printf(\"%lf\", " + lastPop.lexema + ");"
        else:
            outC.body += "\n" + semR.tabs + "printf(" + lastPop.lexema + ");"

        lastPop.inicializar()

        return
    # ARG→ literal  ou ARG→ num
    elif semR.rule == 15 or semR.rule == 16:
        regrasArg = copy.deepcopy(lastPop)
        pilha.top().lexema = lastPop.lexema
        pilha.top().tipo = lastPop.tipo
        return
    # ARG→ id
    elif semR.rule == 17:
        for id in lex.ids:
            if id.lexema == lastPop.lexema:
                achou = True
                if len(id.tipo) != 0:
                    pilha.top().lexema = id.lexema
                    pilha.top().tipo = id.tipo
                    lastPop.tipo = id.tipo
                    #lastPop.inicializar()
                    regrasArg = copy.deepcopy(lastPop)

        if not pilha.top().tipo or not achou:
            print("ERRO! Variavel  nao definida!")
            semR.generate = False

        return

    # A→ CMD A
    elif semR.rule == 18:
        return

    # CMD→ id rcb LD;
    elif semR.rule == 19:
        for id in lex.ids:
            if id.lexema == lastPop.lexema:
                if not id.tipo:
                    achou = True

        if achou:
            print("ERRO! Variavel nao definida!")
        elif not expression:
            if lastPop.tipo != '':
                for id in lex.ids:
                    if id.token == lastPop.token and id.lexema == lastPop.lexema:
                        lastPop.tipo = id.tipo
            if len(expression_declarada) != 0:
                if lastPop.tipo != expression_declarada[-1].tipo:
                    print("ERRO! Variaveis ", lastPop.lexema, " e ",
                        expression[0].lexema, " de tipos diferentes!")
                    semR.generate = False

                outC.body += "\n" + semR.tabs + lastPop.lexema + \
                    " = " + expression_declarada[-1].lexema + ";"
                del expression_declarada[:]
            else:
                outC.body += "\n" + semR.tabs + lastPop.lexema + \
                " = " + "T" + str(semR.temporaryCounter) + ";"
        else:
            if len(expression_declarada) != 0:
                outC.body += "\n" + semR.tabs + lastPop.lexema + \
                    " = " + expression_declarada[-1].lexema + ";"
            else:
                outC.body += "\n" + semR.tabs + lastPop.lexema + \
                    " = " + "T" + str(semR.temporaryCounter) + ";"

        lastPop.inicializar()
        return

    # LD→ OPRD opm OPRD
    elif semR.rule == 20:
        for id in lex.ids:
            if id.tipo != expression[0].tipo and not id.tipo:
               print("ERRO! Variaveis de tipos diferentes dentro da expressao!")
               semR.generate = False
               return
            elif id.tipo == "lit":
                print(
                    "ERRO! Variaveis literais nao podem estar dentro de uma expressao!")
                semR.generate=False
                return
        semR.temporaryCounter = semR.temporaryCounter + 1
        sem.lexema = "T" + str(semR.temporaryCounter)
        #sem.token = tk.id
        sem.token = tk.token
        sem.tipo = lastPop.tipo
        #lex.ids.append(sem)
        if sem.tipo == 'Nulo' or sem.tipo == '' :
            sem.tipo = expression[-1].tipo

        pilha.top().lexema = sem.lexema
        outC.declarations += "\n" + semR.tabs + sem.tipo + " " + sem.lexema + ";"
        outC.body += "\n" + semR.tabs + sem.lexema + " = "

        for id in expression_declarada:
            outC.body += id.lexema
        
        outC.body += ";"
        sem.inicializar()
        lastPop.inicializar()
        del expression_declarada[:]
        del expression[:]
        return
        
    # LD→ OPRD
    elif semR.rule == 21:
        pilha.top().lexema = lastPop.lexema
        pilha.top().tipo = lastPop.tipo
        return

    # OPRD→ id
    elif semR.rule == 22:
        for id in lex.ids:
            if id.lexema == lastPop.lexema:
                lastPop.tipo = id.tipo
                achou = True
                return
        if not achou:
            print("Erro: Variável", lastPop.lexema ,"não declarada" )
            semR.generate = False
            return
        
        expression.append(copy.deepcopy(lastPop))
        lastPop.inicializar()
        return
    # OPRD→ num    
    elif semR.rule == 23:
        pilha.top().lexema = lastPop.lexema
        pilha.top().tipo = lastPop.tipo

        for c in lastPop.lexema:
            if c == '.':
                lastPop.tipo = "double"
        if lastPop.tipo == 'Nulo' :
            lastPop.tipo = "int"
        
        expression.append(copy.deepcopy(lastPop))
        return
    # A→ COND A
    elif semR.rule == 24:
        return
    # COND→ CAB CP
    elif semR.rule == 25:
        semR.tabs = semR.tabs[0: len(semR.tabs) - 1]
        outC.body += "\n" + semR.tabs + "}"
        return
    # CAB→ se (EXP_R) então
    elif semR.rule == 26:
        sem.lexema = "T" + str(semR.temporaryCounter)
        outC.body += "\n" + semR.tabs + "if ( " + sem.lexema + " )\n" + semR.tabs + "{"
        semR.tabs += "\t"
        lastPop.inicializar()
        return
    # EXP_R→ OPRD opr OPRD
    elif semR.rule == 27:
        for id in lex.ids:
            if id.tipo != expression[0].tipo and not id.tipo:
                print("Erro: Operandos com tipos incompatíveis")
                semR.generate = False
                return
            elif id.tipo == "lit":
                print("Erro: Operandos com tipos incompatíveis")
                semR.generate = False
                return
        semR.temporaryCounter = semR.temporaryCounter + 1
        sem.lexema = "T" + str(semR.temporaryCounter)
        sem.token = tk.token
        sem.tipo = lastPop.tipo
        if sem.tipo == 'Nulo' or sem.tipo == '' :
            sem.tipo = expression[-1].tipo
        #lex.ids.append(sem)

        pilha.top().lexema = sem.lexema
        outC.declarations += "\n\t" + sem.tipo + " " + sem.lexema + ";"
        outC.body +=  "\n" + semR.tabs + sem.lexema + " = "
        for s in expression_declarada:    
            outC.body += s.lexema
        
        outC.body += ";"
        sem.inicializar()
        lastPop.inicializar()
        del expression_declarada[:]
        del expression[:]
        return
    # CP→ ES CP ou CP→ CMD CP ou CP→ COND CP ou CP→ fimse ou A→ R A
    elif semR.rule == 28 or semR.rule == 29 or semR.rule == 30 or semR.rule == 31  or semR.rule == 32:
        return
    # R → facaAte (EXP_R) CP_R
    elif semR.rule == 33:
        return

def analisador_sintatico_antigo(lex):
    erroSint=False
    lexico.ler_arquivo_mgol(lex)
    t=lexico.scanner(lex)
    a=t.token
    tAntigo=t
    print('\nAnalisador sintático\n')
    lastPop= classes.Semantic()
    sem= classes.Semantic()
    semRules= classes.SemanticRules()
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
                    semRules.generate=False

            # reduzir
            elif acao == 'r':
                # produção gerada
                aux2=df_matriz_producoes['Nonterminal'][linhaEstado]
                linhaProd=linhaEstado
                semRules.rule=linhaEstado + 1

                print('Regra: ', df_matriz_producoes['Nonterminal'][linhaProd],
                      '->', df_matriz_producoes['producoes'][linhaProd])

                # desempilha de acordo com a quantidade de produções
                for i in range(df_matriz_producoes['tamProd'][linhaEstado]):
                    pilha.pop()
                    if semRules.generate:
                        lastPop.get(pilha.top())
                    pilha.pop()

                linhaEstado=pilha.items[len(pilha.items)-1]

                #sem.inicializar()

                pilha.push(t)
                aux_estado=df_tabela_sintatica[aux2][linhaEstado]

                if semRules.generate:
                    applySemanticRule(semRules, lastPop,
                                      pilha, expression, lex, outC)

                sem.inicializar()
                pilha.push(
                    int(df_tabela_sintatica[aux2][linhaEstado][1:(len(aux_estado))]))




            # aceita
            elif acao == 'a':
                print('\n----- ACEITA -----\n')

                #if semRules.generate:
                outC.body += "\n}"
                print(" Arquivo .c gerado.")
                # Abre(ou cria) um arquivo .c com o nome do arquivo em mgol que está sendo analisado 
                arqDestino = open(str("out")+".c", "w+")
                # Imprime um elemento da lista TextoArquivo
                arqDestino.write( outC.header + outC.declarations + outC.body)
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
    lastPop = classes.Semantic()
    semRules = classes.SemanticRules()
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
                semRules.generate = False

        elif (acao == "r"):
            reduction = df_matriz_producoes['Nonterminal'][estado]
            semRules.rule= estado + 1

            print('Regra: ', df_matriz_producoes['Nonterminal'][estado],
                    '->', df_matriz_producoes['producoes'][estado])

            # desempilha de acordo com a quantidade de produções
            for i in range(df_matriz_producoes['tamProd'][estado]):
                if semRules.generate:
                    lastPop.get(copy.deepcopy(pilha.top()))
                    
                pilha.pop()
                if lastPop.tipo == '':
                    lastPop.tipo = pilha.top().tipo

            estado = pilha.top().estado

            if pilha.top().estado == -1:
                estado = 0
            else:
                estado = pilha.top().estado

            #sem.inicializar()
            #sem.token = reduction
            pilha.push(copy.deepcopy(sem))

            if semRules.generate:
                applySemanticRule(semRules, lastPop, pilha, expression, lex, outC, ids_declarados, expression_declarada, found)
            
            aux_estado= df_tabela_sintatica[reduction][estado]
            estado_aux =  int(df_tabela_sintatica[reduction][estado][1:(len(aux_estado))])
            sem.inicializar()
            sem.estado = estado_aux
            pilha.top().estado = estado_aux


        # aceita
        elif acao == 'a':
            print('\n----- ACEITA -----\n')

            #if semRules.generate:
            outC.body += "\n}"
            print(" Arquivo .c gerado.")
            # Abre(ou cria) um arquivo .c com o nome do arquivo em mgol que está sendo analisado 
            arqDestino = open(str("out")+".c", "w+")
            # Imprime um elemento da lista TextoArquivo
            arqDestino.write( outC.header + outC.declarations + outC.body)
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
