import ply.lex as lex

# Palavras reservadas
reservadas = {
    'program': 'PROGRAM', 
    'var': 'VAR', 
    'begin': 'BEGIN', 
    'end': 'END',
    'integer': 'INTEGER', 
    'boolean': 'BOOLEAN', 
    'false': 'FALSE', 
    'true': 'TRUE',
    'read': 'READ', 
    'write': 'WRITE', 
    'while': 'WHILE', 
    'do': 'DO',
    'if': 'IF', 
    'then': 'THEN', 
    'else': 'ELSE',
    'div': 'DIV', 
    'and': 'AND', 
    'or': 'OR', 
    'not': 'NOT'
}

tokens = [
    'ID', 
    'NUM',
    'EPAR', 
    'DPAR',     
    'PV', 
    'DP', 
    'VIRG', 
    'PF',
    'ATRIB',   
    'IGUAL', 
    'DIFERENTE', 
    'MENOR', 
    'MENOR_IGUAL', 
    'MAIOR', 
    'MAIOR_IGUAL',
    'MAIS', 
    'MENOS', 
    'VEZES'
] + list(reservadas.values())

# Regras simples
t_EPAR = r'\('
t_DPAR = r'\)'
t_PV = r';'
t_DP = r':'
t_VIRG = r','
t_PF = r'\.'
t_ATRIB = r':='
t_IGUAL = r'='
t_DIFERENTE = r'<>'
t_MENOR = r'<'
t_MENOR_IGUAL = r'<='
t_MAIOR = r'>'
t_MAIOR_IGUAL = r'>='
t_MAIS = r'\+'
t_MENOS = r'-'
t_VEZES = r'\*'
t_ignore = ' \t'

def t_ID(t):
    r'[A-Za-z][A-Za-z0-9_]*'
    t.type = reservadas.get(t.value.lower(), 'ID')
    return t

def t_NUM(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"ERRO LÉXICO: Caractere ilegal '{t.value[0]}' na linha {t.lineno}")
    t.lexer.skip(1)

def make_lexer():
    return lex.lex()