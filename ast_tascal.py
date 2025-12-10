from dataclasses import dataclass
from typing import List, Optional, Union

class No:
    pass

class Comando(No):
    pass

class Expressao(No):
    pass

@dataclass
class Programa(No):
    id: str
    declaracoes: List['Declaracao']
    bloco: 'Bloco'
    total_vars: int = 0

@dataclass
class Bloco(No):
    comandos: List[Comando]

@dataclass
class Declaracao(No):
    ids: List['Identificador']
    tipo: str

@dataclass
class Atribuicao(Comando):
    var: 'Identificador'
    expressao: Expressao

@dataclass
class Condicional(Comando):
    cond: Expressao
    then_cmd: Comando
    else_cmd: Union[Comando, None]

@dataclass
class Enquanto(Comando):
    cond: Expressao
    bloco: Comando

@dataclass
class Leitura(Comando):
    vars: List['Identificador']

@dataclass
class Escrita(Comando):
    exps: List[Expressao]

@dataclass
class ComandoComposto(Comando):
    comandos: List[Comando]

@dataclass
class CalculoBinario(Expressao):
    esq: Expressao
    op: str
    dir: Expressao

@dataclass
class CalculoUnario(Expressao):
    op: str
    expr: Expressao

@dataclass
class Identificador(Expressao):
    nome: str
    tipo: str = None
    deslocamento: int = None 

@dataclass
class Numero(Expressao):
    valor: int

@dataclass
class Booleano(Expressao):
    valor: bool