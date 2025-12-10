# Importação das bibliotecas necessárias
import sys
import ply.lex as lex

# Palavras reservadas
reservado = {
    'program': 'PROGRAM',
    'var'    : 'VAR',
    'begin'  : 'BEGIN',
    'end'    : 'END',
    'integer': 'INTEGER',
    'boolean': 'BOOLEAN',
    'false'  : 'FALSE',
    'true'   : 'TRUE',
    'read'   : 'READ',
    'write'  : 'WRITE',
    'while'  : 'WHILE',
    'do'     : 'DO',
    'if'     : 'IF',
    'then'   : 'THEN',
    'else'   : 'ELSE',
    'div'    : 'DIV',
    'and'    : 'AND',
    'or'     : 'OR',
    'not'    : 'NOT'
}

# Tokens
tokens = (
    'ID',
    'NUM',
    'ATRIBUICAO',
    'DIFERENTE',
    'DOIS_PONTOS',
    'MAIOR_IGUAL',
    'MENOR_IGUAL',
    'MAIOR',
    'MENOR'
) + tuple(reservado.values())

# Literais
literals = ['(',')',';','=','+','-','*',',','.']

t_ATRIBUICAO  = r':='
t_DIFERENTE   = r'<>'
t_DOIS_PONTOS = r':'
t_MAIOR_IGUAL = r'>='
t_MENOR_IGUAL = r'<='
t_MAIOR       = r'>'
t_MENOR       = r'<'

# Quebra e contagem de linha
def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Identificador
def t_ID(t):
    r'[a-zA-Z][a-zA-Z0-9_]*'
    if t.value in reservado:
       t.type = reservado[t.value]
    return t

# Números
def t_NUM(t):
    r'[0-9]+'
    t.value = int(t.value)
    return t

# Ignora espaços e tabulações
t_ignore = ' \t'

# Erros léxicos
def t_error(t):
    print(f"ERRO LÉXICO na linha {t.lineno}: símbolo ilegal {t.value[0]!r}")
    t.lexer.skip(1)

# Instancia o lexer
def make_lexer():
    return lex.lex()

# Testando o analisador léxico: 'Get-Content "ProgramasTascalTeste\programa.tascal" | py lexico.py'
if __name__ == '__main__':
    data = sys.stdin.read()
    lexer = make_lexer()
    lexer.input(data)
    for tok in lexer:
        print(f'<{tok.type}, {tok.value!r}> na linha: {tok.lineno}')