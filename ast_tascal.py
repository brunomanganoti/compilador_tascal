# ast_tascal.py
from dataclasses import dataclass
from typing import List, Union

# Classe base
class No:
    pass

@dataclass
class Programa(No):
    id: str
    declaracoes: List['Declaracao']
    bloco: 'Bloco'
    total_vars: int = 0  # Preenchido na analise semantica

@dataclass
class Bloco(No):
    comandos: List['Comando']

class Comando(No): pass

@dataclass
class Declaracao(No):
    ids: List['Var']
    tipo: str

@dataclass
class Atribuicao(Comando):
    var: 'Var'
    expressao: 'Expressao'

@dataclass
class If(Comando):
    condicao: 'Expressao'
    then_cmd: Comando
    else_cmd: Union[Comando, None]

@dataclass
class While(Comando):
    condicao: 'Expressao'
    body: Comando

@dataclass
class Read(Comando):
    vars: List['Var']

@dataclass
class Write(Comando):
    exps: List['Expressao']

@dataclass
class ComandoComposto(Comando):
    comandos: List[Comando]

class Expressao(No): pass

@dataclass
class BinOp(Expressao):
    esq: Expressao
    op: str
    dir: Expressao

@dataclass
class UnOp(Expressao):
    op: str
    expr: Expressao

@dataclass
class Var(Expressao):
    nome: str
    # Campos preenchidos pelo analisador semântico
    tipo: str = None
    deslocamento: int = None 

@dataclass
class Num(Expressao):
    valor: int

@dataclass
class Bool(Expressao):
    valor: bool