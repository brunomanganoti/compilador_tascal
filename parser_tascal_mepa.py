import ply.yacc as yacc
from lexico_tascal_mepa import tokens, make_lexer
import ast_tascal as ast

# Precedência
precedence = (
    ('nonassoc', 'IF'),
    ('nonassoc', 'ELSE'),
    ('right', 'NOT'),
)

def p_programa(p):
    """programa : PROGRAM ID PV bloco PF"""
    p[0] = ast.Programa(id=p[2], declaracoes=p[4]['decls'], bloco=p[4]['cmds'])

def p_bloco(p):
    """bloco : declaracoes comando_composto"""
    p[0] = {
        'decls': p[1],
        'cmds': p[2]
    }

def p_declaracoes(p):
    """declaracoes : VAR declaracao_variaveis
                   | empty"""
    if len(p) == 3:
        p[0] = p[2]
    else:
        p[0] = []

def p_declaracao_variaveis(p):
    """declaracao_variaveis : lista_id DP tipo PV declaracao_variaveis
                            | lista_id DP tipo PV"""
    vars_nodes = [ast.Identificador(nome=n) for n in p[1]]
    decl = ast.Declaracao(ids=vars_nodes, tipo=p[3])
    
    if len(p) == 6:
        p[0] = [decl] + p[5]
    else:
        p[0] = [decl]

def p_lista_id(p):
    """lista_id : ID
                | ID VIRG lista_id"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]

def p_tipo(p):
    """tipo : INTEGER
            | BOOLEAN"""
    p[0] = p[1].lower()

def p_comando_composto(p):
    """comando_composto : BEGIN lista_comandos END"""
    p[0] = ast.Bloco(comandos=p[2])

def p_lista_comandos(p):
    """lista_comandos : comando
                      | comando PV lista_comandos
                      | comando PV"""
    cmd = p[1]
    cmds = []
    
    if cmd:
        cmds.append(cmd)
    
    if len(p) == 4:
        cmds += p[3]
    
    p[0] = cmds

def p_comando(p):
    """comando : atribuicao
               | comando_condicional
               | comando_enquanto
               | comando_leitura
               | comando_escrita
               | comando_composto
               | empty"""
    p[0] = p[1]

def p_atribuicao(p):
    """atribuicao : ID ATRIB expressao"""
    p[0] = ast.Atribuicao(var=ast.Identificador(nome=p[1]), expressao=p[3])

def p_comando_condicional(p):
    """comando_condicional : IF expressao THEN comando
                           | IF expressao THEN comando ELSE comando"""
    else_node = p[6] if len(p) > 5 else None
    p[0] = ast.Condicional(cond=p[2], then_cmd=p[4], else_cmd=else_node)

def p_comando_enquanto(p):
    """comando_enquanto : WHILE expressao DO comando"""
    p[0] = ast.Enquanto(cond=p[2], bloco=p[4])

def p_comando_leitura(p):
    """comando_leitura : READ EPAR lista_id DPAR"""
    vars_nodes = [ast.Identificador(nome=n) for n in p[3]]
    p[0] = ast.Leitura(vars=vars_nodes)

def p_comando_escrita(p):
    """comando_escrita : WRITE EPAR lista_expressoes DPAR"""
    p[0] = ast.Escrita(exps=p[3])

def p_lista_expressoes(p):
    """lista_expressoes : expressao
                        | expressao VIRG lista_expressoes"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]

def p_expressao_or(p):
    """expressao : expressao OR expressao_and
                 | expressao_and"""
    if len(p) == 4:
        p[0] = ast.CalculoBinario(esq=p[1], op='or', dir=p[3])
    else:
        p[0] = p[1]

def p_expressao_and(p):
    """expressao_and : expressao_and AND expressao_rel
                     | expressao_rel"""
    if len(p) == 4:
        p[0] = ast.CalculoBinario(esq=p[1], op='and', dir=p[3])
    else:
        p[0] = p[1]

def p_expressao_rel(p):
    """expressao_rel : soma relacao soma
                     | soma"""
    if len(p) == 4:
        p[0] = ast.CalculoBinario(esq=p[1], op=p[2], dir=p[3])
    else:
        p[0] = p[1]

def p_relacao(p):
    """relacao : IGUAL
               | DIFERENTE
               | MENOR
               | MENOR_IGUAL
               | MAIOR
               | MAIOR_IGUAL"""
    p[0] = p[1]

def p_soma(p):
    """soma : soma MAIS termo
            | soma MENOS termo
            | termo"""
    if len(p) == 4:
        op = '+' if p[2] == '+' else '-'
        p[0] = ast.CalculoBinario(esq=p[1], op=op, dir=p[3])
    else:
        p[0] = p[1]

def p_termo(p):
    """termo : termo VEZES fator
             | termo DIV fator
             | fator"""
    if len(p) == 4:
        op = '*' if p[2] == '*' else 'div'
        p[0] = ast.CalculoBinario(esq=p[1], op=op, dir=p[3])
    else:
        p[0] = p[1]

def p_fator(p):
    """fator : ID
             | NUM
             | TRUE
             | FALSE
             | EPAR expressao DPAR
             | NOT fator
             | MENOS fator"""
    if len(p) == 2:
        token_type = p.slice[1].type
        if token_type == 'ID':
            p[0] = ast.Identificador(nome=p[1])
        elif token_type == 'NUM':
            p[0] = ast.Numero(valor=p[1])
        elif token_type in ['TRUE', 'FALSE']:
            val = True if p[1].lower() == 'true' else False
            p[0] = ast.Booleano(valor=val)
    elif len(p) == 4:
        p[0] = p[2]
    elif len(p) == 3:
        op = p[1]
        if op == 'not': op = 'not'
        else: op = '-'
        p[0] = ast.CalculoUnario(op=op, expr=p[2])

def p_empty(p):
    'empty :'
    p[0] = None

def p_error(p):
    if p:
        print(f"ERRO SINTÁTICO: Token inesperado '{p.value}' na linha {p.lineno}")
    else:
        print("ERRO SINTÁTICO: Fim de arquivo inesperado")

def make_parser():
    return yacc.yacc()