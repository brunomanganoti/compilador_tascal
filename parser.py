# parser.py
import sys
import ply.yacc as yacc
from lexico import tokens, make_lexer, reservado

# ------------------
# TABELA DE SÍMBOLOS
# ------------------
class TabelaSimbolos:
    def __init__(self):
        self.tabela = {}

    def instala(self, nome, tipo):
        if nome in self.tabela:
            return False 
        self.tabela[nome] = {"tipo": tipo}
        return True

    def busca(self, nome):
        return self.tabela.get(nome, None)

# Variáveis globais
tab_simbolos = TabelaSimbolos()
tem_erro = False
parser = None

# Função auxiliar para erros semânticos
def erro_semantico(msg, lineno=None):
    global tem_erro
    tem_erro = True
    if lineno is None:
        print(f"ERRO SEMÂNTICO: {msg}")
    else:
        print(f"ERRO SEMÂNTICO na linha {lineno}: {msg}")

# -------------------------
# PRECEDÊNCIA DE OPERADORES
# -------------------------
precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('right', 'NOT'), 
    ('nonassoc', '=', 'DIFERENTE', 'MENOR', 'MENOR_IGUAL', 'MAIOR', 'MAIOR_IGUAL'), 
    ('left', '+', '-'),
    ('left', '*', 'DIV'),
    ('right', 'UNARY_MINUS'), 
)

# -------------------
# REGRAS DA GRAMÁTICA
# -------------------
def p_programa(p):
    """programa : cabecalho bloco '.'"""
    p[0] = None

def p_cabecalho(p):
    """cabecalho : PROGRAM ID ';'"""
    tab_simbolos.instala(p[2], tipo='programa')

def p_bloco(p):
    """bloco : parte_declaracoes parte_comandos"""
    p[0] = None

# Parte de Declaração
def p_parte_declaracoes(p):
    """parte_declaracoes : VAR lista_declaracoes
                         | empty"""
    p[0] = None

def p_lista_declaracoes(p):
    """lista_declaracoes : lista_declaracoes declaracao
                         | declaracao"""
    p[0] = None

def p_declaracao(p):
    """declaracao : lista_ids DOIS_PONTOS tipo ';'"""
    tipo_variavel = p[3] 
    lista_de_nomes = p[1]
    
    for nome in lista_de_nomes:
        if not tab_simbolos.instala(nome, tipo=tipo_variavel):
            erro_semantico(f"Variável '{nome}' já declarado.", p.lineno(1))

def p_declaracao_erro(p):
    "declaracao : error DOIS_PONTOS tipo ';'" 
    erro_tok = p[1] 
    if erro_tok.type in reservado.values():
        msg = f"Palavra reservada '{erro_tok.value}' não pode ser usada como nome de variável."
    else:
        msg = f"Token inesperado '{erro_tok.value}'. Esperava um identificador."
    print(f"ERRO SINTÁTICO na linha {p.lineno(1)}: {msg}")
    global tem_erro; tem_erro = True
    parser.errok()

def p_lista_ids(p):
    """lista_ids : lista_ids ',' ID
                 | ID"""
    if len(p) == 2:
        p[0] = [p[1]] 
    else:
        p[0] = p[1] + [p[3]] 

def p_tipo(p):
    """tipo : INTEGER
            | BOOLEAN"""
    p[0] = p[1] 

# Parte de Comandos
def p_parte_comandos(p):
    """parte_comandos : BEGIN lista_comandos END"""
    p[0] = None

def p_lista_comandos(p):
    """lista_comandos : lista_comandos_nao_vazia
                      | empty"""
    p[0] = None

def p_lista_comandos_nao_vazia(p):
    """lista_comandos_nao_vazia : lista_comandos_nao_vazia ';' comando
                                | comando"""
    p[0] = None

# Regras de Comando
def p_comando(p):
    """comando : atribuicao
               | condicional
               | repeticao
               | chamada_read
               | chamada_write
               | comando_composto"""
    p[0] = None

def p_comando_composto(p):
    """comando_composto : BEGIN lista_comandos END"""
    p[0] = None

def p_atribuicao(p):
    """atribuicao : ID ATRIBUICAO expressao"""
    nome_var = p[1]
    var = tab_simbolos.busca(nome_var)
    tipo_expr = p[3]
    if not var:
        erro_semantico(f"Variável '{nome_var}' não declarada.", p.lineno(1))
        return
    tipo_var = var['tipo']

    if tipo_expr is None:
        return

    if tipo_var != tipo_expr:
        erro_semantico(f"Variável '{var}' não pode ser do tipo '{tipo_expr}'", p.lineno(1))

def p_condicional(p):
    """condicional : IF expressao THEN comando else_opcional"""
    tipo_expr = p[2]
    if tipo_expr is not None and tipo_expr != 'boolean':
        erro_semantico(f"Expressão da condição 'IF' deve ser de tipo lógico", p.lineno(2))
    p[0] = None

def p_else_opcional(p):
    """else_opcional : ELSE comando
                     | empty"""
    p[0] = None

def p_repeticao(p):
    """repeticao : WHILE expressao DO comando"""
    tipo_expr = p[2]
    if tipo_expr is not None and tipo_expr != 'boolean':
        erro_semantico(f"Expressão da condição 'WHILE' deve ser de tipo lógico", p.lineno(1))
    p[0] = None

def p_chamada_read(p):
    """chamada_read : READ '(' lista_ids_read ')'"""
    lista_de_nomes = p[3]
    for nome in lista_de_nomes:
        if not tab_simbolos.busca(nome):
            erro_semantico(f"Variável '{nome}' em read() não foi declarada.", p.lineno(1))
    
def p_lista_ids_read(p):
    """lista_ids_read : lista_ids
                      | empty"""
    if p[1] is None:
        p[0] = []
    else:
        p[0] = p[1] 

def p_chamada_write(p):
    """chamada_write : WRITE '(' lista_exp_write ')'"""
    p[0] = None

def p_chamada_write_erro(p):
    """chamada_write : WRITE '(' error ')'"""
    print(f"ERRO SINTÁTICO na linha {p.lineno(3)}: Lista de argumentos mal formada em 'write()'.")
    global tem_erro
    tem_erro = True
    parser.errok()

def p_lista_exp_write(p):
    """lista_exp_write : lista_expressoes
                       | empty"""
    p[0] = None

def p_lista_expressoes(p):
    """lista_expressoes : lista_expressoes ',' expressao
                        | expressao"""
    p[0] = None

# Regras de Expressão
def p_expressao_operacoes(p):
    """expressao : expressao '+' expressao
                 | expressao '-' expressao
                 | expressao '*' expressao
                 | expressao DIV expressao
                 | expressao OR expressao
                 | expressao AND expressao
                 | expressao '=' expressao
                 | expressao DIFERENTE expressao
                 | expressao MENOR expressao
                 | expressao MENOR_IGUAL expressao
                 | expressao MAIOR expressao
                 | expressao MAIOR_IGUAL expressao"""
    tipo_esq = p[1]  
    op = p[2]        
    tipo_dir = p[3]
    tipo_resultado = None

    if tipo_esq is None or tipo_dir is None:
        p[0] = None
        return
    # Aritmética
    if op == '+' or op == '-' or op == '*' or op == 'DIV':
        if tipo_esq != 'integer' or tipo_dir != 'integer':
            erro_semantico(f"Operação '{op}' só pode ser feita entre inteiros", p.lineno(2))
            tipo_resultado = None
        else:
            tipo_resultado = 'integer'
    # Relacional
    elif op == '>' or op == '<' or op == '=' or op == 'DIFERENTE' or op == 'MENOR_IGUAL' or op == 'MAIOR_IGUAL':
        if tipo_esq != tipo_dir:
            erro_semantico(f"Operação '{op}' só pode ser feita entre tipos iguais", p.lineno(2))
            tipo_resultado = None
        else:
            tipo_resultado = 'boolean'
    # Lógica
    elif op == 'AND' or op == 'OR':
        if tipo_esq != 'boolean' or tipo_dir != 'boolean':
            erro_semantico(f"Operação '{op}' só pode ser feita entre booleanos", p.lineno(2))
            tipo_resultado = None
        else:
            tipo_resultado = 'boolean'
    p[0] = tipo_resultado

def p_expressao_not(p):
    """expressao : NOT expressao"""
    tipo_op = p[2]
    if tipo_op is None:
        p[0] = None
        return
    if tipo_op != 'boolean':
        erro_semantico(f"Operador 'not' requer um operando 'boolean'.", p.lineno(1))
        p[0] = None
    else: 
        p[0] = 'boolean'

def p_expressao_unary_minus(p):
    """expressao : '-' expressao %prec UNARY_MINUS"""
    tipo_op = p[2]
    if tipo_op is None:
        p[0] = None # Propaga o erro
        return
    if tipo_op != 'integer':
        erro_semantico(f"Operador de negação '-' requer um operando 'integer'.", p.lineno(1))
        p[0] = None
    else:
        p[0] = 'integer'

def p_expressao_parenteses(p):
    """expressao : '(' expressao ')'"""
    p[0] = p[2] 

def p_expressao_fator(p):
    """expressao : fator"""
    p[0] = p[1]

def p_fator(p):
    """fator : ID
             | NUM
             | TRUE
             | FALSE"""
    if p.slice[1].type == 'ID':
        nome_var = p[1]
        var = tab_simbolos.busca(nome_var)
        if not var:
            erro_semantico(f"Variável '{nome_var}' sem declaração prévia.", p.lineno(1))
            p[0] = None 
        else:
            p[0] = var['tipo'] 
    elif p.slice[1].type == 'NUM':
        p[0] = 'integer'
    elif p.slice[1].type == 'TRUE' or p.slice[1].type == 'FALSE':
        p[0] = 'boolean'

# Regras de ERRO
# Cabeçalho (program ID ;)
def p_cabecalho_erro_program(p):
    "cabecalho : error ID ';'"
    print(f"ERRO SINTÁTICO na linha {p.lineno(1)}: esperava 'program'")
    global tem_erro
    tem_erro = True
    parser.errok()

def p_cabecalho_erro_id(p):
    "cabecalho : PROGRAM error ';'"
    print(f"ERRO SINTÁTICO na linha {p.lineno(2)}: esperava identificador após 'program'")
    global tem_erro
    tem_erro = True
    parser.errok()

def p_cabecalho_erro_delim(p):
    "cabecalho : PROGRAM ID error"
    print(f"ERRO SINTÁTICO na linha {p.lineno(3)}: esperava ';'")
    global tem_erro
    tem_erro = True
    parser.errok()

# Comandos
def p_parte_comandos_erro_begin(p):
    "parte_comandos : error lista_comandos END"
    print(f"ERRO SINTÁTICO na linha {p.lineno(1)}: esperava 'begin' antes dos comandos")
    global tem_erro
    tem_erro = True
    parser.errok()

def p_parte_comandos_erro_end(p):
    "parte_comandos : BEGIN lista_comandos error"
    print(f"ERRO SINTÁTICO na linha {p.lineno(3)}: esperava 'end' após os comandos")
    global tem_erro
    tem_erro = True
    parser.errok()

# Regra Vazia
def p_empty(p):
    'empty :'
    p[0] = None

# --------------
# ERRO SINTÁTICO
# --------------
def p_error(tok):
    global tem_erro
    tem_erro = True
    if tok is None:
        print("ERRO SINTÁTICO: Fim de arquivo inesperado (EOF).")
        return
    print(f"ERRO SINTÁTICO na linha {tok.lineno}: Token inesperado '{tok.value}' (Tipo: {tok.type!r})")

def make_parser(start='programa'):
    global parser
    parser = yacc.yacc(start=start)
    return parser

if __name__ == "__main__":
    data = sys.stdin.read()
    lexer = make_lexer()
    parser = make_parser(start='programa')
    parser.parse(data, lexer=lexer)
    if not tem_erro:
        print('Análise concluída. Nenhum erro semântico/sintético encontrado!')
        print('Tabela de Símbolos:')
        print(tab_simbolos.tabela)