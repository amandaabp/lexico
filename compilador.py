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


def aplicar_regra_Semanticoa(semR, ultimo_pop, pilha, expressao, lex, programaC, ids_declarados, expressao_declarada):
    tk = classes.Token()
    sem = classes.Semantico()
    RED   = "\033[1;31m"
    RESET = "\033[0;0m"
    global regrasArg
    achou = False

    # P' → P ou P→ inicio V A ou V→ varincio LV ou LV→ D LV
    if semR.regra == 1 or semR.regra == 2 or semR.regra == 3 or semR.regra == 4:
        return

    # LV -> varfim;
    elif semR.regra == 5:
        programaC.corpo += "\n\t"

    # D→ TIPO L;
    elif semR.regra == 6:
        for id in lex.ids:
            if id.lexema == ultimo_pop.lexema:
                sem.tipo = ultimo_pop.tipo

        pilha.top().tipo = ultimo_pop.tipo
        ultimo_pop.inicializar()

    # L→ id, L
    elif semR.regra == 7:
        for id in lex.ids:
            if id.lexema == ultimo_pop.lexema:
                sem.tipo = ultimo_pop.tipo

        pilha.top().tipo = ultimo_pop.tipo
        programaC.declaracoes += "\n\t" + semR.tabs + " " + ultimo_pop.lexema + ";"
        ultimo_pop.inicializar()
    # L→ id
    elif semR.regra == 8:
        for id in lex.ids:
            if id.lexema == ultimo_pop.lexema:
                sem.tipo = ultimo_pop.tipo

        pilha.top().tipo = ultimo_pop.tipo
        programaC.declaracoes += "\n\t" + semR.tabs + \
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
            programaC.corpo += "\n\t" + semR.tabs + \
                "scanf(\"%s\", "+ultimo_pop.lexema+");"
        elif ultimo_pop.tipo == "int":
            programaC.corpo += "\n\t" + semR.tabs + \
                "scanf(\"%d\", &" + ultimo_pop.lexema + ");"
        elif ultimo_pop.tipo == "double":
            programaC.corpo += "\n\t" + semR.tabs + \
                "scanf(\"%lf\", &" + ultimo_pop.lexema + ");"
        else:
            print(RED + "ERRO!"+ RESET +" Variavel", ultimo_pop.lexema, " não declarada")

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
                programaC.corpo += "\n\t" + semR.tabs + \
                    "printf(\"%s\", " + ultimo_pop.lexema + ");"
            elif ultimo_pop.tipo == "int":
                programaC.corpo += "\n\t" + semR.tabs + \
                    "printf(\"%d\", " + ultimo_pop.lexema + ");"
            elif ultimo_pop.tipo == "double":
                programaC.corpo += "\n\t" + semR.tabs + \
                    "printf(\"%lf\", " + ultimo_pop.lexema + ");"
        else:
            programaC.corpo += "\n\t" + semR.tabs + \
                "printf(" + ultimo_pop.lexema + ");"

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
                    regrasArg = copy.deepcopy(ultimo_pop)

        if not pilha.top().tipo or not achou:
            print(RED + "ERRO!"+ RESET + "Variavel  nao definida!",
                  "linha: ", tk.linha, "coluna: ", tk.coluna)
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
            print(RED + "ERRO!"+ RESET +"Variavel nao definida!",
                  tk.linha, "coluna: ", tk.coluna)
        elif not expressao:
            if ultimo_pop.tipo != '':
                for id in lex.ids:
                    if id.token == ultimo_pop.token and id.lexema == ultimo_pop.lexema:
                        ultimo_pop.tipo = id.tipo
            if len(expressao_declarada) != 0:
                if ultimo_pop.tipo != expressao_declarada[-1].tipo:
                    print(RED + "ERRO!"+ RESET +" Tipos diferentes para atribuição", ultimo_pop.lexema, " e ",
                          expressao[0].lexema, "linha: ", tk.linha, "coluna: ", tk.coluna)
                    semR.gerar = False

                programaC.corpo += "\n\t" + semR.tabs + ultimo_pop.lexema + \
                    " = " + expressao_declarada[-1].lexema + ";"
                del expressao_declarada[:]
            else:
                programaC.corpo += "\n\t" + semR.tabs + ultimo_pop.lexema + \
                    " = " + "T" + str(semR.contador_temp) + ";"
        else:
            if len(expressao_declarada) != 0:
                programaC.corpo += "\n\t" + semR.tabs + ultimo_pop.lexema + \
                    " = " + expressao_declarada[-1].lexema + ";"
            else:
                programaC.corpo += "\n\t" + semR.tabs + ultimo_pop.lexema + \
                    " = " + "T" + str(semR.contador_temp) + ";"

        ultimo_pop.inicializar()
        return

    # LD→ OPRD opm OPRD
    elif semR.regra == 20:
        for id in lex.ids:
            if id.tipo != expressao[0].tipo and not id.tipo:
                print(RED + "ERRO!"+ RESET +" Variaveis de tipos diferentes dentro da expressao! \nlinha: ",
                      tk.linha, "coluna: ", tk.coluna)
                semR.gerar = False
                return
            elif id.tipo == "lit":
                print(
                    RED + "ERRO!"+ RESET +" Variaveis literais nao podem estar dentro de uma expressao! \nlinha: ", tk.linha, "coluna: ", tk.coluna)
                semR.gerar = False
                return
        semR.contador_temp = semR.contador_temp + 1
        sem.lexema = "T" + str(semR.contador_temp)
        sem.token = tk.token
        sem.tipo = ultimo_pop.tipo
        if sem.tipo == 'Nulo' or sem.tipo == '':
            sem.tipo = expressao[-1].tipo

        pilha.top().lexema = sem.lexema
        programaC.declaracoesT += "\n\t" + semR.tabs + sem.tipo + " " + sem.lexema + ";"
        programaC.corpo += "\n\t" + semR.tabs + sem.lexema + " = "

        for id in expressao_declarada:
            programaC.corpo += id.lexema

        programaC.corpo += ";"
        sem.inicializar()
        ultimo_pop.inicializar()
        del expressao_declarada[:]
        del expressao[:]
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
            print(RED + "ERRO!"+ RESET +" Variável", ultimo_pop.lexema, "não declarada",
                  "linha: ", tk.linha, "coluna: ", tk.coluna)
            semR.gerar = False
            return

        expressao.append(copy.deepcopy(ultimo_pop))
        ultimo_pop.inicializar()
        return
    # OPRD→ num
    elif semR.regra == 23:
        pilha.top().lexema = ultimo_pop.lexema
        pilha.top().tipo = ultimo_pop.tipo

        for c in ultimo_pop.lexema:
            if c == '.':
                ultimo_pop.tipo = "double"
        if ultimo_pop.tipo == 'Nulo':
            ultimo_pop.tipo = "int"

        expressao.append(copy.deepcopy(ultimo_pop))
        return
    # A→ COND A
    elif semR.regra == 24:
        return
    # COND→ CAB CP
    elif semR.regra == 25:
        semR.tabs = semR.tabs[0: len(semR.tabs) - 1]
        programaC.corpo += "\n\t" + semR.tabs + "}"
        return
    # CAB→ se (EXP_R) então
    elif semR.regra == 26:
        sem.lexema = "T" + str(semR.contador_temp)
        programaC.corpo += "\n\t" + semR.tabs + \
            "if ( " + sem.lexema + " )\n\t" + semR.tabs + "{"
        semR.tabs += "\t"
        ultimo_pop.inicializar()
        return
    # EXP_R→ OPRD opr OPRD
    elif semR.regra == 27:
        for id in lex.ids:
            if id.tipo != expressao[0].tipo and not id.tipo:
                print(RED + "ERRO!"+ RESET +" Operandos com tipos incompatíveis \nlinha: ",
                      tk.linha, "coluna: ", tk.coluna)
                semR.gerar = False
                return
            elif id.tipo == "lit":
                print(RED + "ERRO!"+ RESET +" Operandos com tipos incompatíveis \nlinha: ",
                      tk.linha, "coluna: ", tk.coluna)
                semR.gerar = False
                return
        semR.contador_temp = semR.contador_temp + 1
        sem.lexema = "T" + str(semR.contador_temp)
        sem.token = tk.token
        sem.tipo = ultimo_pop.tipo
        if sem.tipo == 'Nulo' or sem.tipo == '':
            sem.tipo = expressao[-1].tipo

        pilha.top().lexema = sem.lexema
        programaC.declaracoesT += "\n\t" + sem.tipo + " " + sem.lexema + ";"
        programaC.corpo += "\n\t" + semR.tabs + sem.lexema + " = "
        for s in expressao_declarada:
            programaC.corpo += s.lexema

        programaC.corpo += ";"
        sem.inicializar()
        ultimo_pop.inicializar()
        del expressao_declarada[:]
        del expressao[:]
        return
    # CP→ ES CP ou CP→ CMD CP ou CP→ COND CP ou CP→ fimse ou A→ R A
    elif semR.regra == 28 or semR.regra == 29 or semR.regra == 30 or semR.regra == 31 or semR.regra == 32:
        return
    # R → facaAte (EXP_R) CP_R
    elif semR.regra == 33:
        return


def analisador_sintatico(lex):
    erroSint = False
    lexico.ler_arquivo_mgol(lex)
    tok = classes.Token()
    sem = classes.Semantico()
    ultimo_pop = classes.Semantico()
    semregras = classes.RegrasSemanticas()
    pilha = classes.Stack()  # pilha para auxiliar na analise Sintática
    estado = -1
    lastLexeme = ""
    expressao = []
    programaC = classes.programaC()
    expressao_declarada = []
    cont_expres = False
    ids_declarados = []
    RED   = "\033[1;31m"
    RESET = "\033[0;0m"
    tok = lexico.scanner(lex)

    if tok.linha < 0 and not tok.token:
        print(RED + "ERRO!"+ RESET +"- linha", tok.linha, " - ", tok.token)

    pilha.push(copy.deepcopy(sem))

    while(1):
        if pilha.top().estado == -1:
            s = 0
        else:
            s = pilha.top().estado

        # busca acao na tabela sintatica
        aux = df_tabela_sintatica[tok.token][s]
        estado_aux = df_tabela_sintatica[tok.token][s][1:(len(aux))]
        acao = df_tabela_sintatica[tok.token][s][0]

        if acao == 's' or acao == 'r' or acao == 'E':
            estado = int(estado_aux)

        if (acao == "s"):
            sem.inicializar()
            sem.get(tok)
            pilha.push(copy.deepcopy(sem))

            if (sem.token == tokens.OPR or sem.token == tokens.OPM):
                expressao.append(copy.deepcopy(sem))

            sem.inicializar()
            sem.estado = estado
            pilha.top().estado = estado

            lastLexeme = tok.lexema

            if erroSint:
                tok = tAntigo
                erroSint = False
            else:
                tok = lexico.scanner(lex)

            if tok.token == "id":
                ids_declarados.append(tok)

            if lastLexeme == '(' or lastLexeme == '<-':
                cont_expres = True
            elif tok.lexema == ')' or tok.lexema == ';':
                cont_expres = False

            if cont_expres:
                expressao_declarada.append(tok)

            while tok.linha < 0:
                semregras.gerar = False

        elif (acao == "r"):
            reduction = df_matriz_producoes['Nonterminal'][estado]
            semregras.regra = estado + 1

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

            pilha.push(copy.deepcopy(sem))

            if semregras.gerar:
                aplicar_regra_Semanticoa(
                    semregras, ultimo_pop, pilha, expressao, lex, programaC, ids_declarados, expressao_declarada)

            aux_estado = df_tabela_sintatica[reduction][estado]
            estado_aux = int(
                df_tabela_sintatica[reduction][estado][1:(len(aux_estado))])
            sem.inicializar()
            sem.estado = estado_aux
            pilha.top().estado = estado_aux

        # aceita
        elif acao == 'a':
            print('\n----- ACEITA -----\n')

            if semregras.gerar:
                programaC.corpo += "\n}"
                # Abre(ou cria) um arquivo .c com o nome do arquivo em mgol que está sendo analisado
                arqDestino = open(str("programa")+".c", "w+")
                # Imprime um elemento da lista TextoArquivo
                arqDestino.write(programaC.cabecalho + programaC.declaracoesT + programaC.declaracaoa_finalT +
                                 programaC.declaracoes + programaC.corpo)
                # Fim do arquivo
                arqDestino.write("\n")
                arqDestino.close()
                print("Arquivo " + "programa" + ".c gerado")
            else:
                print("\033[0;30;41mErros encontrados, Arquivo programa.c não foi gerado.\033[m")
            return
        # erro
        elif acao == 'E':
            faltSib = {}
            impriLista = ""

            linhas = df_tabela_sintatica.values[s]
            colunas = df_tabela_sintatica.columns

            for k, v in zip(linhas, colunas):
                if v != 'estado':
                    if k != '0' and k != 0:
                        if k[0] != 'E':
                            faltSib.update({v: k})
                            nomeToken = lexico.eqToken(v)
                            impriLista = impriLista + " " + str(nomeToken)
            print(RED + "ERRO Sintático!"+ RESET +"\nLinha: ", tok.linha, "Coluna: ",
                  tok.coluna, "\n Faltando símbolo(s):", impriLista)

            if len(faltSib) == 1:
                print("\tTratamento de erro. Inserindo símbolo ausente...")
                chave = [key for key in faltSib.keys()]

                tAntigo = tok

                a = chave[0]

                erroSint = True

                pilha.pop()
                pilha.pop()
                pilha.push(chave[0])
                pilha.push(int(aux))

                print("\nInserindo para continuar a análise.")
                print("\nFim de tratamento de erro\n")
            else:
                print("\nTratamento de erro.")
                listaFollow = df_matriz_follow['FOLLOW'][int(s)-1]
                aux = 1

                while (aux):
                    while True:
                        tok = lexico.scanner(lex)
                        a = tok.token

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
                                aux = 0
                                break

                    x = df_matriz_producoes['tamProd'][int(s)]
                    if x:
                        for i in range(0, int(x)):
                            pilha.pop()
                            pilha.pop()

                    print("Recuperando análise sintática\n")
    else:
        print(RED + "ERRO lexico!"+ RESET + tok.erro)

        if tok.erro.split == 'ERRO2' or tok.erro.split == 'ERRO5':
            print('Esperava argumento "num"'+'\n' +
                  'Linha : {} | Coluna : {}'.format(tok.linha, tok.coluna-2))

        tok = lexico.scanner(lex)
        a = tok.token

# função para interpretar alguns tokens


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
