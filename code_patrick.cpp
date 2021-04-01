#include "stdafx.h"
#include <iostream>
#include <sstream>
#include <string>
#include <map>
#include <fstream>
#include <vector>
#include <ctype.h>
#include <algorithm>
#include <stack>

using std::cout;
using std::cin;
using std::ifstream;
using std::ofstream;
using std::string;
using std::getline;
using std::istringstream;
using std::endl;
using std::map;
using std::multimap;
using std::pair;
using std::tuple;
using std::vector;
using std::get;
using std::stack;
using std::to_string;
using std::stoi;

struct Tokens
{
	const string num{ "num" };
	const string id{ "id" };
	const string comentario{ "comentario" };
	const string OPR{ "OPR" };
	const string RCB{ "RCB" };
	const string OPM{ "OPM" };
	const string AB_P{ "AB_P" };
	const string FC_P{ "FC_P" };
	const string PT_V{ "PT_V" };
	const string ERRO{ "ERRO" };
	const string EndOfFile{ "EOF" };

	const string inicio{ "inicio" };
	const string varinicio{ "varinicio" };
	const string varfim{ "varfim" };
	const string leia{ "leia" };
	const string escreva{ "escreva" };
	const string se{ "se" };
	const string entao{ "entao" };
	const string senao{ "senao" };
	const string fimse{ "fimse" };
	const string fim{ "fim" };
	const string inteiro{ "int" };
	const string lit{ "lit" };
	const string real{ "real" };
};

map<int, string> populatefinalStates();
map<pair<char, int>, int> populateLexicalStateMatrix();
map<pair<string, int>, int> populateSyntaticStateMatrix();
map<int, pair<string, string>> populateProductions();
pair<int, string> readMgol();

class Token
{
public:
	int line;
	int collumn;
	string lexeme;
	string token;
	string type;
	string error;

	Token()
	{
		line = 0;
		collumn = 0;
		lexeme = "";
		token = "";
		type = "";
		error = "";
	}
};

class Semantic
{
public:
	int state;
	string lexeme;
	string token;
	string type;

	Semantic()
	{
		state = -1;
		lexeme = "";
		token = "";
		type = "";
	}

	void initialize()
	{
		state = -1;
		lexeme = "";
		token = "";
		type = "";
	}

	void get(Token tok)
	{
		lexeme = tok.lexeme;
		token = tok.token;
		type = tok.type;
	}

	void get(Semantic sem)
	{
		if (sem.token.empty()) return;
		if (token == "ARG" || token == "id" || token == "EXP_R") return;
		if (!sem.lexeme.empty()) lexeme = sem.lexeme;
		token = sem.token;
		if (!sem.type.empty()) type = sem.type;
	}
};

class Lexical
{
public:

	int lineNum;
	int lineCount;
	string mgolCode;
	map <pair<char, int>, int> stateMatrix;
	map<int, string> finalStates;
	vector<Semantic> ids;
	string lastLexeme;

	Lexical() noexcept
	{
		pair<int, string> sizeAndCode = readMgol();

		stateMatrix = populateLexicalStateMatrix();
		lineCount = sizeAndCode.first;
		mgolCode = sizeAndCode.second;
		finalStates = populatefinalStates();
		lineNum = 1;
		lastLexeme = "";
	}

};

class SemanticRules
{
public:
	int rule;
	int temporaryCounter;
	bool generate;
	string tabs;

	SemanticRules()
	{
		temporaryCounter = -1;
		rule = 0;
		generate = true;
		tabs = "\t";
	}
};

class OutC
{
public:
	string header;
	string declarations;
	string body;

	OutC()
	{
		header = "#include<stdio.h>\ntypedef char literal[256];\nvoid main(void)\n{";
		body = "";
		declarations = "";
	}	
};

bool reservedWord(string word);
string getToken(int state);
char entry(char c, int state);
int countWords(string str);
string spaces(int previous);
void syntactic(Lexical& lex);
string getNextAction(int& state, string token);
string parseError(stack<Semantic>& synth, Token& tok, Lexical& lex, string& lastLexeme);
void parseLexicalError(Lexical& lex, Token& tok, Tokens& tokens);
void applySemanticRule(SemanticRules& semR, Semantic& lastPop, stack<Semantic>& synth, vector<Semantic>& expression ,Lexical& lex, OutC& outC);
void printErrorHeader(int lastState, string lastLexeme, Lexical& lex, Token& tok);
void forceInsertToken(string tk, string& lastLexeme, Lexical& lex, Token& tok, stack<Semantic>& synth);
string errorSpaces(int lexemSize);
Token nextToken(Lexical& lex);

int main()
{
	try
	{
		Tokens tokens;
		Lexical lex;

		syntactic(lex);

		if (lex.lineNum > 0 || lex.lineNum == lex.lineCount)
		{
			cout << endl << endl;

			for (Semantic& s : lex.ids)
			{
				cout << s.lexeme << "     " << s.token << "     " << s.type << endl;
			}
		}

		cout << endl << endl;

		system("pause");
		return 0;
	}
	catch (int e)
	{
		cout << "Exceção Nr. " << e << endl;
	}

}

void syntactic(Lexical& lex)
{
	Token tok;
	Tokens tokens;
	Semantic sem;
	Semantic lastPop;
	SemanticRules semRules;
	stack<Semantic> synth;
	vector<Semantic> expression;
	int i = 0;
	int state = -1;
	int stateAux = -1;
	string action = "";
	string lastLexeme = "";
	string errorHandle = "";
	pair<string, string> reduction("", "");
	map<pair<string, int>, int> synthMatrix = populateSyntaticStateMatrix();
	map<int, pair<string, string>> productions = populateProductions();
	OutC outC;

	tok = nextToken(lex);

	if (tok.line < 0 && !tok.token.empty())
	{
		cout << endl << "ERRO - linha " << tok.line*-1 << " - '" << tok.token << "'" << endl;
		return;
	}

	synth.push(sem);

	while(1)
	{
		stateAux = synthMatrix[pair<string, int>(tok.token, synth.top().state)];
		action = getNextAction(stateAux, tok.token);

		if (action == "shift")
		{
			state = stateAux;

			sem.initialize();
			sem.get(tok);
			synth.push(sem);

			if (sem.token == tokens.OPR || sem.token == tokens.OPM) expression.push_back(sem);

			sem.initialize();
			sem.state = state;
			synth.push(sem);

			lastLexeme = tok.lexeme;
			tok = nextToken(lex);

			while (tok.line < 0)
			{
				parseLexicalError(lex, tok, tokens);
			}

		}
		else if (action == "reduce")
		{		
			state = stateAux;
			reduction = productions[state];
			semRules.rule = state;

			cout << endl << "- PRODUCAO " << semRules.rule << ": " << reduction.first << " -> " << reduction.second;

			for (i = 0; i < 2 * countWords(reduction.second); i++)
			{
				if (semRules.generate) lastPop.get(synth.top());
				synth.pop();
			}

			state = synth.top().state;

			sem.initialize();
			sem.token = reduction.first;
			synth.push(sem);	

			if (semRules.generate) applySemanticRule(semRules, lastPop, synth, expression, lex, outC);

			stateAux = synthMatrix[pair<string, int>(reduction.first, state)];	
			sem.initialize();
			sem.state = stateAux;
			synth.push(sem);		

		}
		else if (action == "accept")
		{
			cout << endl << endl << "Analise Sintatica: Sucesso!";

			if (semRules.generate)
			{
				outC.body += "\n}";
				cout << " Arquivo .c gerado.";
				ofstream archive("out.c");
				archive << outC.header + outC.declarations + outC.body;
			}
			else
			{
				cout << " Erros encontrados, Arquivo .c nao foi gerado.";
			}

			return;
		}
		else
		{
			if (tok.token == tokens.EndOfFile) return;
			semRules.generate = false;

			cout << endl << endl << "ERRO!" << endl << endl;
			errorHandle = parseError(synth, tok, lex, lastLexeme);

			if (errorHandle == ";")
			{
				forceInsertToken(";", lastLexeme, lex, tok, synth);
			}
			else if (errorHandle == ")")
			{
				forceInsertToken(")", lastLexeme, lex, tok, synth);
			}
			else if (errorHandle == "(")
			{
				forceInsertToken("(", lastLexeme, lex, tok, synth);
			}
			else
			{
				if (tok.error == tokens.varfim)
				{
					lex.lineNum *= -1;
					if (tok.token == tokens.id)
					{
						tok.token = "";
					}
					while (tok.token != tokens.varfim && tok.token != tokens.id && tok.line > 0)
					{
						tok = nextToken(lex);

						while (tok.line < 0)
						{
							if (tok.token == tokens.EndOfFile) return;
							parseLexicalError(lex, tok, tokens);
						}

						if (tok.token == tokens.EndOfFile) return;
					}					
					synth.pop();

				}
				else if (tok.error == tokens.se)
				{
					cout << endl << "toda a expressao 'se 'sera ignorada - analise sintatica ira continuar" << endl;

					lex.lineNum *= -1;
					while (tok.token != tokens.fimse && tok.line > 0)
					{
						tok = nextToken(lex);

						while (tok.line < 0)
						{
							if (tok.token == tokens.EndOfFile) return;
							parseLexicalError(lex, tok, tokens);
						}

						if (tok.token == tokens.EndOfFile) return;
					}
					while (tok.token == tokens.fimse)
					{
						tok = nextToken(lex);

						while (tok.line < 0)
						{
							if (tok.token == tokens.EndOfFile) return;
							parseLexicalError(lex, tok, tokens);
						}

						if (tok.token == tokens.EndOfFile) return;
					}
					while (synth.top().token != tokens.se) synth.pop();
					synth.pop();
				}
				else
				{
					cout << endl << "'" << errorHandle << "' lexema nao reconhecido ignorado - analise sintatica ira continuar" << endl;

					lex.lineNum *= -1;
					tok.token = synth.top().token;
					synth.pop();
					tok.lexeme = lastLexeme;

					stateAux = synthMatrix[pair<string, int>(tok.token, synth.top().state)];

					if (stateAux == 0)
					{
						tok = nextToken(lex);

						while (tok.token == tokens.comentario && tok.line > 0)
							tok = nextToken(lex);

						while (tok.line < 0)
						{
							parseLexicalError(lex, tok, tokens);
						}
					}
				}	
			}
		}
	}

	lex.lineNum *= -1;
}

void applySemanticRule(SemanticRules& semR, Semantic& lastPop, stack<Semantic>& synth, vector<Semantic>& expression, Lexical& lex ,OutC& outC)
{
	bool found = false;
	Tokens tokens;
	string aux;
	Semantic sem;

	switch (semR.rule)
	{
	case 5:

		outC.body += "\n";
		break;

	case 6:

		for (Semantic& s : lex.ids)
		{
			if (s.lexeme == lastPop.lexeme)
			{
				s.type = lastPop.type;
				break;
			}
		}
		synth.top().type = lastPop.type;
		outC.declarations += "\n"+ semR.tabs + lastPop.type + " " + lastPop.lexeme + ";";
		lastPop.initialize();
		break;

	case 7:
	case 8:
	case 9:

		synth.top().type = lastPop.type;
		break;

	case 11:

		for (Semantic& s : lex.ids)
		{
			if (s.lexeme == lastPop.lexeme)
			{
				lastPop.type = s.type;
				break;
			}
		}

		if (lastPop.type == "literal")
		{
			outC.body += "\n" + semR.tabs+"scanf(\"%s\", "+lastPop.lexeme+");";
		}
		else if (lastPop.type == "int")
		{
			outC.body += "\n" + semR.tabs + "scanf(\"%d\", &" + lastPop.lexeme + ");";
		}
		else if (lastPop.type == "double")
		{
			outC.body += "\n" + semR.tabs + "scanf(\"%lf\", &" + lastPop.lexeme + ");";
		}
		else cout << endl << endl << "ERRO!" << endl << endl << "Variavel "<< lastPop.lexeme <<" nao definida!" << endl;

		lastPop.initialize();
		break;

	case 12:

		for (Semantic& s : lex.ids)
		{
			if (s.lexeme == lastPop.lexeme)
			{
				lastPop.type = s.type;
				found = true;
				break;
			}
		}

		if (found)
		{
			if (lastPop.type == "literal")
			{
				outC.body += "\n" + semR.tabs + "printf(\"%s\", " + lastPop.lexeme + ");";
			}
			else if (lastPop.type == "int")
			{
				outC.body += "\n" + semR.tabs + "printf(\"%d\", " + lastPop.lexeme + ");";
			}
			else if (lastPop.type == "double")
			{
				outC.body += "\n" + semR.tabs + "printf(\"%lf\", " + lastPop.lexeme + ");";
			}
		}
		else
		{
			outC.body += "\n" + semR.tabs + "printf(" + lastPop.lexeme + ");";
		}

		lastPop.initialize();
		break;

	case 13:
	case 14:

		synth.top().lexeme = lastPop.lexeme;
		synth.top().type = lastPop.type;
		break;

	case 15:

		for (Semantic& s : lex.ids)
		{
			if (s.lexeme == lastPop.lexeme)
			{
				found = true;
				if (!s.type.empty())
				{
					synth.top().lexeme = s.lexeme;
					synth.top().type = s.type;		
					lastPop.initialize();
					break;
				}
			}
		}
		if (synth.top().type.empty() || !found)
		{
			cout << endl << endl << "ERRO!" << endl << endl << "Variavel " << lastPop.lexeme << " nao definida!" << endl;
			semR.generate = false;
		}
		break;

	case 17:
		
		for (Semantic& s : lex.ids)
		{
			if (s.lexeme == lastPop.lexeme)
				if(!s.type.empty()) found = true;
		}

		if (!found)
		{
			cout << endl << endl << "ERRO!" << endl << endl << "Variavel " << lastPop.lexeme << " nao definida!" << endl;
			semR.generate = false;
		}
		else if (!expression.empty())
		{
			if (lastPop.type != expression[0].type)
			{
				cout << endl << endl << "ERRO!" << endl << endl << "Variaveis " << lastPop.lexeme << " e " << expression[0].lexeme << " de tipos diferentes!" << endl;
				semR.generate = false;
			}

			outC.body += "\n" + semR.tabs + lastPop.lexeme + " = " + expression[0].lexeme + ";";
			expression.clear();
		}
		else
		{
			outC.body += "\n" + semR.tabs + lastPop.lexeme + " = " + "T" + to_string(semR.temporaryCounter) + ";";
		}
		
		lastPop.initialize();
		break;

	case 18:

		for (Semantic& s : expression)
		{
			if (s.type != expression[0].type && !s.type.empty())
			{
				cout << endl << endl << "ERRO!" << endl << endl << " Variaveis de tipos diferentes dentro da expressao!" << endl;
				semR.generate = false;
				break;
			}
			else if (s.type == "lit")
			{
				cout << endl << endl << "ERRO!" << endl << endl << " Variaveis literais nao podem estar dentro de uma expressao!" << endl;
				semR.generate = false;
				break;
			}
		}

		sem.lexeme = "T" + to_string(++semR.temporaryCounter);		
		sem.token = tokens.id;
		sem.type = lastPop.type;
		lex.ids.push_back(sem);		

		synth.top().lexeme = sem.lexeme;
		outC.declarations += "\n" + semR.tabs + sem.type + " " + sem.lexeme + ";";
		outC.body += "\n" + semR.tabs + sem.lexeme + " = ";
		for (Semantic& s : expression)
		{
			outC.body += s.lexeme;
		}
		outC.body += ";";
		sem.initialize();
		lastPop.initialize();
		expression.clear();

		break;

	case 19:

		synth.top().lexeme = lastPop.lexeme;
		synth.top().type = lastPop.type;
		break;

	case 20:

		for (Semantic& s : lex.ids)
		{
			if (s.lexeme == lastPop.lexeme)
			{
				lastPop.type = s.type;
				found = true;
				break;
			}
		}
		if (!found)
		{
			cout << endl << endl << "ERRO!" << endl << endl << "Variavel " << lastPop.lexeme << " nao definida!" << endl;
			semR.generate = false;
			break;
		}

		expression.push_back(lastPop); 
		lastPop.initialize();

		break;

	case 21:

		synth.top().lexeme = lastPop.lexeme;
		synth.top().type = lastPop.type;
				
		for (char& c: lastPop.lexeme)
		{
			if (c == '.') lastPop.type = "double";
		}

		if (lastPop.type.empty())  lastPop.type = "int";

		expression.push_back(lastPop);
		break;

	case 23:

		semR.tabs = semR.tabs.substr(0, semR.tabs.size() - 1);
		outC.body += "\n" + semR.tabs + "}";		
		break;

	case 24:

		outC.body += "\n" + semR.tabs + "if ( " + lastPop.lexeme + " )\n" + semR.tabs + "{";
		semR.tabs += "\t";
		lastPop.initialize();
		break;

	case 25:

		for (Semantic& s : expression)
		{
			if (s.type != expression[0].type && !s.type.empty())
			{
				cout << endl << endl << "ERRO!" << endl << endl << " Variaveis de tipos diferentes dentro da expressao!" << endl;
				semR.generate = false;
				break;
			}
			else if (s.type == "lit")
			{
				cout << endl << endl << "ERRO!" << endl << endl << " Variaveis literais nao podem estar dentro de uma expressao!" << endl;
				semR.generate = false;
				break;
			}
		}

		sem.lexeme = "T" + to_string(++semR.temporaryCounter);
		sem.token = tokens.id;
		sem.type = lastPop.type;
		lex.ids.push_back(sem);

		synth.top().lexeme = sem.lexeme;
		outC.declarations += "\n\t" + sem.type + " " + sem.lexeme + ";";
		outC.body += "\n" + semR.tabs + sem.lexeme + " = ";
		for (Semantic& s : expression)
		{
			outC.body += s.lexeme;
		}
		outC.body += ";";
		sem.initialize();
		lastPop.initialize();
		expression.clear();
		break;

	default:
		break;
	}
}

void forceInsertToken(string toInsert, string& lastLexeme, Lexical& lex, Token& tok, stack<Semantic>& synth)
{
	lex.mgolCode = toInsert+" " + tok.lexeme + lex.mgolCode;
	tok.token = synth.top().token;
	synth.pop();
	tok.lexeme = lastLexeme;
	lex.lineNum *= -1;

	cout << endl << "'"+toInsert+"' inserido - analise sintatica ira continuar" << endl;
}

void parseLexicalError(Lexical& lex, Token& tok, Tokens& tokens)
{
	lex.lineNum = tok.line;
	cout << endl << endl << "ERRO!" << endl << endl;
	cout << "Linha " << tok.line*-1 << ", Coluna " << tok.collumn << endl << tok.error << endl
		<< "em '..." << string(&lex.mgolCode.front(), &lex.mgolCode.front() + tok.collumn + 5 > &lex.mgolCode.back() ?
			&lex.mgolCode.back() : &lex.mgolCode.front() + tok.collumn + 5) << "...'" << endl;

	while (lex.mgolCode.front() == ' ' || lex.mgolCode.front() == '\t' || lex.mgolCode.front() == '\n')
	{
		lex.mgolCode = string(&lex.mgolCode.front() + 1, &lex.mgolCode.back());
	}

	cout << endl << "'" << tok.lexeme << "' lexema nao reconhecido ignorado - analise sintatica ira continuar" << endl;

	lex.mgolCode = string(&lex.mgolCode.front() + tok.lexeme.size(), &lex.mgolCode.back());
	lex.lineNum *= -1;

	tok = nextToken(lex);

}

void printErrorHeader(int lastState, string lastLexeme, Lexical& lex, Token& tok)
{
	string message = string(&lex.mgolCode.front(), &lex.mgolCode.front() + tok.collumn + 10 > &lex.mgolCode.back() ?
		&lex.mgolCode.back() : &lex.mgolCode.front() + tok.collumn + 10);
	replace(message.begin(), message.end(), '\n', ' ');
	replace(message.begin(), message.end(), '\t', ' ');

	cout << "Ultimo Estado: " << lastState << ", Linha " << tok.line << ", Coluna " << tok.collumn << endl << endl
		<< "em '..." << message << "...'" << endl << errorSpaces(lastLexeme.size() + 7) << "^" << endl;
}

string parseError(stack<Semantic>& synth, Token& tok, Lexical& lex, string& lastLexeme)
{
	Tokens tokens;
	int lastState = 0;
	lastState = synth.top().state;
	synth.pop();
	printErrorHeader(lastState, lastLexeme, lex, tok);

	switch (lastState)
	{

	case 39:
	case 37:
	case 38:
	case 17:
	case 23:
	case 26:
	case 44:
		cout << "Faltou um ; antes de '" << tok.lexeme << "'." << endl;
		lex.lineNum *= -1;
		return ";";

	case 49:
		cout << "Faltou um operador antes de '" << tok.lexeme << "' " << endl;
		lex.lineNum *= -1;
		break;

	case 58:
		cout << "Faltou um 'se' antes desse 'entao'" << endl;
		lex.lineNum *= -1;
		break;

	case 18:
		cout << "Faltou o tipo da variavel antes de '" << tok.lexeme << "' " << endl;
		lex.lineNum *= -1;
		tok.error = tokens.varfim;
		return tok.lexeme;

	case 14:
		cout << "Faltou parenteses antes de '" << tok.lexeme << "' " << endl;
		lex.lineNum *= -1;
		return "(";

	case 43:
		cout << "Faltou fechar o parenteses antes de '" << tok.lexeme << "' " << endl;
		lex.lineNum *= -1;
		return ")";

	case 54:
	case 10:
	case 11:
		cout << "Faltou algo antes de '" << tok.lexeme << "' " << endl;
		lex.lineNum *= -1;
		lastLexeme = tok.lexeme;
		return lastLexeme;

	case 12:
		cout << "Token invalido antes de '" << tok.lexeme << "' " << endl;
		lex.lineNum *= -1;
		lastLexeme = tok.lexeme;
		return lastLexeme;

	case 53:
		cout << "Faltou o entao antes de '" << tok.lexeme << "' " << endl;
		lex.lineNum *= -1;
		lastLexeme = tok.lexeme;
		tok.error = tokens.se;
		return lastLexeme;

	case 29:
		cout << "Faltou um 'fimse' em algum lugar" << endl;
		lex.lineNum *= -1;
		break;

	case 40:
		cout << "Faltou o 'fim' ou 'fimse'" << endl;
		lex.lineNum *= -1;
		lastLexeme = tok.lexeme;
		return lastLexeme;

	default:
		cout << "Em '" << tok.lexeme << "' " << endl;
		lex.lineNum *= -1;
		lastLexeme = tok.lexeme;
		return lastLexeme;

	}
	return " ";
}

string getNextAction(int& state, string token)
{
	if (state == 999) return "accept";

	if (state > 200)
	{
		state = (state - 200);
		return "reduce";
	}

	if (state > 100)
	{
		state = (state - 100);
		return "shift";
	}

	if (state == 0) return "ërro";

	return "";
}

Token nextToken(Lexical& lex)
{
	Semantic sem;
	Token tk;
	struct Tokens tokens;
	char *begin = &lex.mgolCode.front();
	char *beginLexeme = begin;
	string lexeme = "";
	string token = "";
	string type = "";
	string error = "";
	int stateAux = -1;
	int state = -1;
	int collumn = 1;
	char ent;

	for (char& c : lex.mgolCode)
	{
		if (c == '\0' && stateAux == -1 && state == -1)
		{
			tk.line = lex.lineNum;
			tk.lexeme = tokens.EndOfFile;
			tk.token = tokens.EndOfFile;
			tk.collumn = collumn;
			return tk;
		}

		begin = &c;
		ent = entry(c, state);
		stateAux = lex.stateMatrix[pair<char, int>(ent, state)];

		if (stateAux == -1 && state == 20)
		{
			cout << endl << "Linha " << lex.lineNum << " [comentario] " << string(beginLexeme, begin);
			beginLexeme = begin;

			if (c == '\n' || c == '\t' || c == ' ')
			{
				beginLexeme++;

				if (c == '\n')
				{
					lex.lineNum++;
					collumn = 1;
				}
			}
			
		}
		else if (stateAux == -1 && state != -1) break;
		else if (stateAux == -1 && state == -1)
		{
			if (c == '\n')
			{
				lex.lineNum++;
				collumn = 1;
			}
			beginLexeme++;
		}
		else if (stateAux == 0)
		{
			token = lex.finalStates[state];
			error = lex.finalStates[lex.stateMatrix[pair<char, int>(ent, -1)]];

			if (!token.empty() && !error.empty())
			{
				if (token != error)
				{
					if (token == tokens.id || token == tokens.num)
					{
						if (string(beginLexeme, begin) == tokens.se)
						{
							if (error == tokens.AB_P) break;
						}
						if (error == tokens.PT_V || error == tokens.OPR || error == tokens.OPM || error == tokens.FC_P) break;
					}

					if (token == tokens.AB_P)
					{
						if (error == tokens.id || error == tokens.num) break;
						else
						{
							tk.lexeme = string(beginLexeme, begin + 1);
							tk.line = lex.lineNum * -1;
							tk.error = "Falta um valor ou variavel depois desse Abre Parenteses: '" + tk.lexeme + "'";
							tk.collumn = collumn;
							return tk;
						}
					}


					if (token == tokens.OPR || token == tokens.OPM || token == tokens.RCB)
					{
						if (error == tokens.id || error == tokens.num) break;
						else
						{
							tk.lexeme = string(beginLexeme, begin + 1);
							tk.line = lex.lineNum * -1;
							tk.error = "Falta um valor ou variavel aqui: '" + tk.lexeme + "'";
							tk.collumn = collumn;
							return tk;
						}
					}

				}
				else
				{
					tk.lexeme = string(beginLexeme, begin + 1);
					tk.line = lex.lineNum * -1;
					tk.error = "Token duplicado: '" + tk.lexeme + "'";
					tk.collumn = collumn;
					return tk;
				}
			}
			else if (!token.empty() && error.empty())
			{
				tk.lexeme = string(beginLexeme, begin + 1);
				tk.line = lex.lineNum* -1;
				tk.error = "Caractere invalido: '" + tk.lexeme + "'";
				tk.collumn = collumn;
				return tk;
			}
			
			tk.lexeme = string(beginLexeme, begin + 1);
			tk.line = lex.lineNum * -1;
			tk.error = "Caractere invalido: '" + tk.lexeme + "'";
			tk.collumn = collumn;
			return tk;
		}
		else collumn++;
		state = stateAux;
	}

	token = lex.finalStates[state];
	lexeme = string(beginLexeme, begin);

	if (!token.empty())
	{
		lex.mgolCode = string(begin, lex.mgolCode.length());

		if (token == tokens.id)
		{
			if (!reservedWord(lexeme))
			{
				sem.initialize();

				for (Semantic& s : lex.ids)
				{
					if (s.lexeme == lexeme)
					{
						sem.state = -2;
					}
				}

				if (sem.state == -1)
				{
					sem.lexeme = lexeme;
					sem.token = tokens.id;
					lex.ids.push_back(sem);
				}

				type = "";
			}
			else
			{
				token = lexeme;
				
				if (token == tokens.inteiro) type = "int";
				else if (token == tokens.lit) type = "literal";
				else if (token == tokens.real) type = "double";
				else type = "";


			}
		}

		cout << endl << "Linha " << lex.lineNum << " [" << token << "] " << lexeme;

		tk.line = lex.lineNum;
		tk.lexeme = lexeme;
		tk.collumn = collumn;
		tk.token = token;
		tk.type = type;
		return tk;
	}
	else
	{
		if (state == 16 || state == 18)
		{
			tk.line = lex.lineNum*-1;
			tk.error = "Vc esqueceu de fechar alguma coisa aqui: " + lexeme.substr(0, 7) + "...";
			tk.collumn = collumn;
			return tk;
		}

		tk.line = lex.lineNum*-1;
		tk.lexeme = lexeme;
		tk.collumn = collumn;
		return tk;
	}
}

pair<int, string> readMgol()
{
	ifstream inmgol("mgol.alg");	
	string mgolCode;
	string rawline;
	int lineCount = 0;

	while (getline(inmgol, rawline))
	{
		lineCount++;
		istringstream iss(rawline);
		cout << lineCount << " " << rawline << endl;
		if (lineCount > 1) rawline = "\n" + rawline;
		mgolCode += rawline;
	}
	
	return pair<int, string>(lineCount, mgolCode);
}

bool reservedWord(string word)
{
	struct Tokens tokens;
	return (word == tokens.inicio ||
		word == tokens.varinicio ||
		word == tokens.varfim ||
		word == tokens.leia ||
		word == tokens.escreva ||
		word == tokens.se ||
		word == tokens.entao ||
		word == tokens.senao ||
		word == tokens.fimse ||
		word == tokens.fim ||
		word == tokens.inteiro ||
		word == tokens.lit ||
		word == tokens.real);
}

map<int, string> populatefinalStates()
{
	struct Tokens tokens;

	map<int, string> m =
	{
		{ 1,tokens.id },
	{ 2,tokens.num },
	{ 4,tokens.num },
	{ 7,tokens.num },
	{ 8,tokens.fim },
	{ 9,tokens.OPR },
	{ 10,tokens.OPR },
	{ 11,tokens.RCB },
	{ 12,tokens.OPR },
	{ 13,tokens.AB_P },
	{ 14,tokens.FC_P },
	{ 15,tokens.PT_V },
	{ 17,tokens.OPM },
	{ 19,tokens.lit },
	{ 20,tokens.comentario }
	};

	return m;

}

string getToken(int state)
{
	map <int, string> finalStates = populatefinalStates();

	return finalStates[state];
}

map<pair<char, int>, int> populateLexicalStateMatrix()
{
	//pair<entry,current state> destination state
	map<pair<char, int>, int> m =
	{
	{ pair<char,int>('S',-1),-1 },
	{ pair<char,int>('S',1),-1 },
	{ pair<char,int>('S',1),-1 },
	{ pair<char,int>('S',2),-1 },
	{ pair<char,int>('S',4),-1 },
	{ pair<char,int>('S',7),-1 },
	{ pair<char,int>('S',8),-1 },
	{ pair<char,int>('S',9),-1 },
	{ pair<char,int>('S',10),-1 },
	{ pair<char,int>('S',11),-1 },
	{ pair<char,int>('S',12),-1 },
	{ pair<char,int>('S',13),-1 },
	{ pair<char,int>('S',14),-1 },
	{ pair<char,int>('S',15),-1 },
	{ pair<char,int>('S',17),-1 },
	{ pair<char,int>('S',19),-1 },
	{ pair<char,int>('S',20),-1 },

	{ pair<char,int>(';',1),-1 },
	{ pair<char,int>(';',2),-1 },
	{ pair<char,int>(';',4),-1 },
	{ pair<char,int>(';',7),-1 },
	{ pair<char,int>(';',19),-1 },

	{ pair<char,int>('L',-1),1 },
	{ pair<char,int>('L',1),1 },
	{ pair<char,int>('_',1),1 },

	{ pair<char,int>('D',-1),2 },
	{ pair<char,int>('D',1),1 },
	{ pair<char,int>('D',2),2 },
	{ pair<char,int>('D',3),4 },
	{ pair<char,int>('D',4),4 },
	{ pair<char,int>('D',5),7 },
	{ pair<char,int>('D',6),7 },
	{ pair<char,int>('D',7),7 },

	{ pair<char,int>('E',2),5 },
	{ pair<char,int>('E',4),5 },
	{ pair<char,int>('e',2),5 },
	{ pair<char,int>('e',4),5 },
	{ pair<char,int>('.',2),3 },
	{ pair<char,int>('-',5),6 },
	{ pair<char,int>('+',5),6 },

	{ pair<char,int>('(',-1),13 },
	{ pair<char,int>(')',-1),14 },
	{ pair<char,int>(';',-1),15 },
	{ pair<char,int>('+',-1),17 },
	{ pair<char,int>('*',-1),17 },
	{ pair<char,int>('-',-1),17 },
	{ pair<char,int>('/',-1),17 },

	{ pair<char,int>('>',-1),9 },
	{ pair<char,int>('<',-1),10 },
	{ pair<char,int>('=',-1),9 },
	{ pair<char,int>('>',10),12 },
	{ pair<char,int>('=',10),12 },
	{ pair<char,int>('=',9),12 },
	{ pair<char,int>('-',10),11 },

	{ pair<char,int>('"',-1),18 },
	{ pair<char,int>('A',18),18 },
	{ pair<char,int>('"',18),19 },
	{ pair<char,int>('{',-1),16 },
	{ pair<char,int>('A',16),16 },
	{ pair<char,int>('}',16),20 }
	};

	return m;

}

map<pair<string, int>, int> populateSyntaticStateMatrix()
{
	Tokens tokens;
	//pair<entry,current state> destination state
	//destination state * 100 = shift
	//destination state * 200 = reduce
	map<pair<string, int>, int> m =
	{

	{ pair<string,int>("P",-1), 1 },
	{ pair<string,int>(tokens.inicio,-1),102 },

	{ pair<string,int>("V",2),3 },
	{ pair<string,int>(tokens.varinicio,2),104 },

	{ pair<string,int>("A",3),5 },
	{ pair<string,int>("ES",3),6 },
	{ pair<string,int>("CMD",3),7 },
	{ pair<string,int>("COND",3),8 },
	{ pair<string,int>("CABECALHO",3),13 },
	{ pair<string,int>(tokens.fim,3),109 },
	{ pair<string,int>(tokens.escreva,3),110 },
	{ pair<string,int>(tokens.leia,3),111 },
	{ pair<string,int>(tokens.id,3),112 },
	{ pair<string,int>(tokens.se,3),114 },

	{ pair<string,int>("LV",4),15 },
	{ pair<string,int>("D",4),16 },
	{ pair<string,int>(tokens.varfim,4),117 },
	{ pair<string,int>(tokens.id,4),118 },

	{ pair<string,int>("A",6),19 },
	{ pair<string,int>("ES",6),6 },
	{ pair<string,int>("CMD",6),7 },
	{ pair<string,int>("COND",6),8 },
	{ pair<string,int>("CABECALHO",6),13 },
	{ pair<string,int>(tokens.fim,6),109 },
	{ pair<string,int>(tokens.escreva,6),110 },
	{ pair<string,int>(tokens.leia,6),111 },
	{ pair<string,int>(tokens.id,6),112 },
	{ pair<string,int>(tokens.se,6),114 },

	{ pair<string,int>("A",7),20 },
	{ pair<string,int>("ES",7),6 },
	{ pair<string,int>("CMD",7),7 },
	{ pair<string,int>("COND",7),8 },
	{ pair<string,int>("CABECALHO",7),13 },
	{ pair<string,int>(tokens.fim,7),109 },
	{ pair<string,int>(tokens.escreva,7),110 },
	{ pair<string,int>(tokens.leia,7),111 },
	{ pair<string,int>(tokens.id,7),112 },
	{ pair<string,int>(tokens.se,7),114 },

	{ pair<string,int>("A",8),21 },
	{ pair<string,int>("ES",8),6 },
	{ pair<string,int>("CMD",8),7 },
	{ pair<string,int>("COND",8),8 },
	{ pair<string,int>("CABECALHO",8),13 },
	{ pair<string,int>(tokens.fim,8),109 },
	{ pair<string,int>(tokens.escreva,8),110 },
	{ pair<string,int>(tokens.leia,8),111 },
	{ pair<string,int>(tokens.id,8),112 },

	{ pair<string,int>(tokens.se,8),114 },

	{ pair<string,int>("ARG",10),22 },
	{ pair<string,int>(tokens.lit,10),123 },
	{ pair<string,int>(tokens.num,10),124 },
	{ pair<string,int>(tokens.id,10),125 },

	{ pair<string,int>(tokens.id,11),126 },

	{ pair<string,int>(tokens.RCB,12),127 },

	{ pair<string,int>("ES",13),29 },
	{ pair<string,int>("CMD",13),30 },
	{ pair<string,int>("CORPO",13),28 },
	{ pair<string,int>("COND",13),31 },
	{ pair<string,int>("CABECALHO",13),13 },
	{ pair<string,int>(tokens.escreva,13),110 },
	{ pair<string,int>(tokens.leia,13),111 },
	{ pair<string,int>(tokens.id,13),112 },
	{ pair<string,int>(tokens.se,13),114 },
	{ pair<string,int>(tokens.fimse,13),132 },

	{ pair<string,int>(tokens.AB_P,14),133 },

	{ pair<string,int>(tokens.varfim,16),117 },
	{ pair<string,int>(tokens.id,16),118 },
	{ pair<string,int>("D",16),16 },
	{ pair<string,int>("LV",16),34 },

	{ pair<string,int>(tokens.PT_V,17),135 },

	{ pair<string,int>(tokens.inteiro,18),137 },
	{ pair<string,int>(tokens.real,18),138 },
	{ pair<string,int>(tokens.lit,18),139 },
	{ pair<string,int>("TIPO",18),36 },

	{ pair<string,int>(tokens.PT_V,22),140 },

	{ pair<string,int>(tokens.PT_V,26),158 },

	{ pair<string,int>(tokens.id,27),143 },
	{ pair<string,int>(tokens.num,27),144 },
	{ pair<string,int>("LD",27),41 },
	{ pair<string,int>("OPRD",27),42 },

	{ pair<string,int>("CORPO",29),45 },
	{ pair<string,int>("ES",29),29 },
	{ pair<string,int>("CMD",29),30 },
	{ pair<string,int>("COND",29),31 },
	{ pair<string,int>("CABECALHO",29),13 },
	{ pair<string,int>(tokens.fimse,29),132 },
	{ pair<string,int>(tokens.escreva,29),110 },
	{ pair<string,int>(tokens.leia,29),111 },
	{ pair<string,int>(tokens.id,29),112 },
	{ pair<string,int>(tokens.se,29),114 },

	{ pair<string,int>("CORPO",30),46 },
	{ pair<string,int>("ES",30),29 },
	{ pair<string,int>("CMD",30),30 },
	{ pair<string,int>("COND",30),31 },
	{ pair<string,int>("CABECALHO",30),13 },
	{ pair<string,int>(tokens.fimse,30),132 },
	{ pair<string,int>(tokens.escreva,30),110 },
	{ pair<string,int>(tokens.leia,30),111 },
	{ pair<string,int>(tokens.id,30),112 },
	{ pair<string,int>(tokens.se,30),114 },

	{ pair<string,int>("CORPO",31),47 },
	{ pair<string,int>("ES",31),29 },
	{ pair<string,int>("CMD",31),30 },
	{ pair<string,int>("COND",31),31 },
	{ pair<string,int>("CABECALHO",31),13 },
	{ pair<string,int>(tokens.fimse,31),132 },
	{ pair<string,int>(tokens.escreva,31),110 },
	{ pair<string,int>(tokens.leia,31),111 },
	{ pair<string,int>(tokens.id,31),112 },
	{ pair<string,int>(tokens.se,31),114 },

	{ pair<string,int>(tokens.id,33),143 },
	{ pair<string,int>(tokens.num,33),144 },
	{ pair<string,int>("OPRD",33),49 },
	{ pair<string,int>("EXP_R",33),48 },

	{ pair<string,int>(tokens.PT_V,36),150 },

	{ pair<string,int>(tokens.PT_V,41),151 },

	{ pair<string,int>(tokens.OPM,42),152 },

	{ pair<string,int>(tokens.FC_P,48),153 },

	{ pair<string,int>(tokens.OPR,49),154 },

	{ pair<string,int>("OPRD",52),55 },
	{ pair<string,int>(tokens.id,52),143 },
	{ pair<string,int>(tokens.num,52),144 },

	{ pair<string,int>(tokens.entao,53),156 },

	{ pair<string,int>("OPRD",54),57 },
	{ pair<string,int>(tokens.id,54),143 },
	{ pair<string,int>(tokens.num,54),144 },

	{ pair<string,int>(tokens.EndOfFile,1),999 },

	{ pair<string,int>(tokens.EndOfFile,5),202 },

	{ pair<string,int>(tokens.EndOfFile,9),230 },

	{ pair<string,int>(tokens.leia,15),203 },
	{ pair<string,int>(tokens.escreva,15),203 },
	{ pair<string,int>(tokens.id,15),203 },
	{ pair<string,int>(tokens.se,15),203 },
	{ pair<string,int>(tokens.fim,15),203 },

	{ pair<string,int>(tokens.EndOfFile,19),210 },

	{ pair<string,int>(tokens.EndOfFile,20),216 },

	{ pair<string,int>(tokens.EndOfFile,21),222 },

	{ pair<string,int>(tokens.PT_V,23),213 },

	{ pair<string,int>(tokens.PT_V,24),214 },

	{ pair<string,int>(tokens.PT_V,25),215 },

	{ pair<string,int>(tokens.leia,28),223 },
	{ pair<string,int>(tokens.escreva,28),223 },
	{ pair<string,int>(tokens.id,28),223 },
	{ pair<string,int>(tokens.se,28),223 },
	{ pair<string,int>(tokens.fim,28),223 },
	{ pair<string,int>(tokens.fimse,28),223 },

	{ pair<string,int>(tokens.leia,32),229 },
	{ pair<string,int>(tokens.escreva,32),229 },
	{ pair<string,int>(tokens.id,32),229 },
	{ pair<string,int>(tokens.se,32),229 },
	{ pair<string,int>(tokens.fim,32),229 },
	{ pair<string,int>(tokens.fimse,32),229 },

	{ pair<string,int>(tokens.leia,34),204 },
	{ pair<string,int>(tokens.escreva,34),204 },
	{ pair<string,int>(tokens.id,34),204 },
	{ pair<string,int>(tokens.se,34),204 },
	{ pair<string,int>(tokens.fim,34),204 },

	{ pair<string,int>(tokens.leia,35),205 },
	{ pair<string,int>(tokens.escreva,35),205 },
	{ pair<string,int>(tokens.id,35),205 },
	{ pair<string,int>(tokens.se,35),205 },
	{ pair<string,int>(tokens.fim,35),205 },

	{ pair<string,int>(tokens.PT_V,37),207 },

	{ pair<string,int>(tokens.PT_V,38),208 },

	{ pair<string,int>(tokens.PT_V,39),209 },

	{ pair<string,int>(tokens.leia,40),212 },
	{ pair<string,int>(tokens.escreva,40),212 },
	{ pair<string,int>(tokens.id,40),212 },
	{ pair<string,int>(tokens.se,40),212 },
	{ pair<string,int>(tokens.fim,40),212 },
	{ pair<string,int>(tokens.fimse,40),212 },

	{ pair<string,int>(tokens.PT_V,42),219 },

	{ pair<string,int>(tokens.PT_V,43),220 },
	{ pair<string,int>(tokens.FC_P,43),220 },
	{ pair<string,int>(tokens.OPM,43),220 },
	{ pair<string,int>(tokens.OPR,43),220 },

	{ pair<string,int>(tokens.PT_V,44),221 },
	{ pair<string,int>(tokens.FC_P,44),221 },
	{ pair<string,int>(tokens.OPM,44),221 },
	{ pair<string,int>(tokens.OPR,44),221 },

	{ pair<string,int>(tokens.leia,45),226 },
	{ pair<string,int>(tokens.escreva,45),226 },
	{ pair<string,int>(tokens.id,45),226 },
	{ pair<string,int>(tokens.se,45),226 },
	{ pair<string,int>(tokens.fim,45),226 },
	{ pair<string,int>(tokens.fimse,45),226 },

	{ pair<string,int>(tokens.leia,46),227 },
	{ pair<string,int>(tokens.escreva,46),227 },
	{ pair<string,int>(tokens.id,46),227 },
	{ pair<string,int>(tokens.se,46),227 },
	{ pair<string,int>(tokens.fim,46),227 },
	{ pair<string,int>(tokens.fimse,46),227 },

	{ pair<string,int>(tokens.leia,47),228 },
	{ pair<string,int>(tokens.escreva,47),228 },
	{ pair<string,int>(tokens.id,47),228 },
	{ pair<string,int>(tokens.se,47),228 },
	{ pair<string,int>(tokens.fim,47),228 },
	{ pair<string,int>(tokens.fimse,47),228 },

	{ pair<string,int>(tokens.id,50),206 },
	{ pair<string,int>(tokens.varfim,50),206 },

	{ pair<string,int>(tokens.leia,51),217 },
	{ pair<string,int>(tokens.escreva,51),217 },
	{ pair<string,int>(tokens.id,51),217 },
	{ pair<string,int>(tokens.se,51),217 },
	{ pair<string,int>(tokens.fim,51),217 },
	{ pair<string,int>(tokens.fimse,51),217 },

	{ pair<string,int>(tokens.PT_V,55),218 },

	{ pair<string,int>(tokens.leia,56),224 },
	{ pair<string,int>(tokens.escreva,56),224 },
	{ pair<string,int>(tokens.id,56),224 },
	{ pair<string,int>(tokens.se,56),224 },
	{ pair<string,int>(tokens.fim,56),224 },
	{ pair<string,int>(tokens.fimse,56),224 },

	{ pair<string,int>(tokens.FC_P,57),225 },

	{ pair<string,int>(tokens.leia,58),211 },
	{ pair<string,int>(tokens.escreva,58),211 },
	{ pair<string,int>(tokens.id,58),211 },
	{ pair<string,int>(tokens.se,58),211 },
	{ pair<string,int>(tokens.fim,58),211 },
	{ pair<string,int>(tokens.fimse,58),211 },

	};

	return m;

}

map<int, pair<string, string>> populateProductions()
{
	struct Tokens tokens;
	map<int, pair<string, string>> m =
	{
	{ 1,pair<string,string>("P'","P") },
	{ 2,pair<string,string>("P",tokens.inicio + " V A") },
	{ 3,pair<string,string>("V",tokens.varinicio + " LV") },
	{ 4,pair<string,string>("LV","D LV") },
	{ 5,pair<string,string>("LV",tokens.varfim + " " + tokens.PT_V) },
	{ 6,pair<string,string>("D",tokens.id + " TIPO " + tokens.PT_V) },
	{ 7,pair<string,string>("TIPO",tokens.inteiro) },
	{ 8,pair<string,string>("TIPO",tokens.real) },
	{ 9,pair<string,string>("TIPO",tokens.lit) },
	{ 10,pair<string,string>("A","ES A") },
	{ 11,pair<string,string>("ES",tokens.leia + " " + tokens.id + " " + tokens.PT_V) },
	{ 12,pair<string,string>("ES",tokens.escreva + " ARG " + tokens.PT_V) },
	{ 13,pair<string,string>("ARG",tokens.lit) },
	{ 14,pair<string,string>("ARG",tokens.num) },
	{ 15,pair<string,string>("ARG",tokens.id) },
	{ 16,pair<string,string>("A","CMD A") },
	{ 17,pair<string,string>("CMD",tokens.id + " " + tokens.RCB + " LD " + tokens.PT_V) },
	{ 18,pair<string,string>("LD","OPRD " + tokens.OPM + " OPRD") },
	{ 19,pair<string,string>("LD","OPRD") },
	{ 20,pair<string,string>("OPRD",tokens.id) },
	{ 21,pair<string,string>("OPRD",tokens.num) },
	{ 22,pair<string,string>("A","COND A") },
	{ 23,pair<string,string>("COND","CABECALHO CORPO") },
	{ 24,pair<string,string>("CABECALHO",tokens.se + " " + tokens.AB_P + " EXP_R " + tokens.FC_P + " " + tokens.entao) },
	{ 25,pair<string,string>("EXP_R","OPRD " + tokens.OPR + " OPRD") },
	{ 26,pair<string,string>("CORPO","ES CORPO") },
	{ 27,pair<string,string>("CORPO","CMD CORPO") },
	{ 28,pair<string,string>("CORPO","COND CORPO") },
	{ 29,pair<string,string>("CORPO",tokens.fimse) },
	{ 30,pair<string,string>("A",tokens.fim) },
	};

	return m;
}

int countWords(string str)
{
	bool inSpaces = true;
	int numWords = 0;

	for (char& c : str)
	{
		if (c == '\0') break;
		if (isspace(c))
		{
			inSpaces = true;
		}
		else if (inSpaces)
		{
			numWords++;
			inSpaces = false;
		}
	}

	return numWords;
}

char entry(char c, int state)
{
	if (state == 2 || state == 4)
	{
		if (c == 'e') return c;
		if (c == 'E') return c;
	}

	if (state == 18)
	{
		if (c != '"') return 'A';
		else return c;
	}

	if (state == 16)
	{
		if (c != '}') return 'A';
		else return c;
	}

	if (c == '\n' || c == ' ' || c == '\t' || c == '\0') return 'S';

	if (isalpha(c)) return 'L';
	if (isdigit(c)) return 'D';
	else return c;
}

string errorSpaces(int lexemSize)
{
	string spac = " ";
	int i = 0;
	for (i = 0; i < lexemSize; i++) spac += " ";
	return spac;
}

string spaces(int previous)
{
	int sp = 30;
	int i = 0;
	string spac = " ";

	for (i = 0; i < sp - previous; i++)
	{
		spac += " ";
	}

	return spac;
}




© 2021 GitHub, Inc.
Terms
Privacy
Security
Status
Docs
Contact GitHub
Pricing
API
Training
Blog
About
