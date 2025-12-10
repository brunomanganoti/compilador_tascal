import sys
from ast_tascal import *

class TabelaSimbolos:
    def __init__(self):
        self.simbolos = {}
        self.deslocamento_atual = 0
    
    def define(self, nome, tipo):
        if nome in self.simbolos:
            raise Exception(f"Erro Semântico: Variável '{nome}' já declarada.")
        self.simbolos[nome] = {'tipo': tipo, 'end': self.deslocamento_atual}
        self.deslocamento_atual += 1
    
    def resolve(self, nome):
        return self.simbolos.get(nome)

class AnalisadorSemantico:
    def __init__(self):
        self.ts = TabelaSimbolos()

    def visit(self, node):
        if isinstance(node, Programa):
            for decl in node.declaracoes:
                self.visit(decl)
            
            node.total_vars = self.ts.deslocamento_atual
            
            self.visit(node.bloco)

        elif isinstance(node, Declaracao):
            for var_node in node.ids:
                self.ts.define(var_node.nome, node.tipo)
                
                # Atualizamos o nó da AST com as informações da tabela
                info = self.ts.resolve(var_node.nome)
                var_node.tipo = info['tipo']
                var_node.deslocamento = info['end']

        elif isinstance(node, Bloco) or isinstance(node, ComandoComposto):
            for cmd in node.comandos:
                self.visit(cmd)

        elif isinstance(node, Atribuicao):
            self.visit(node.expressao)
            self.visit(node.var) # Vai chamar visit(Var) abaixo

        elif isinstance(node, If):
            self.visit(node.condicao)
            self.visit(node.then_cmd)
            if node.else_cmd:
                self.visit(node.else_cmd)

        elif isinstance(node, While):
            self.visit(node.condicao)
            self.visit(node.body)

        elif isinstance(node, Read):
            for v in node.vars:
                self.visit(v)
        
        elif isinstance(node, Write):
            for e in node.exps:
                self.visit(e)

        elif isinstance(node, BinOp):
            self.visit(node.esq)
            self.visit(node.dir)
        
        elif isinstance(node, UnOp):
            self.visit(node.expr)

        elif isinstance(node, Var):
            info = self.ts.resolve(node.nome)
            if not info:
                raise Exception(f"Erro Semântico: Variável '{node.nome}' não declarada.")
            
            node.deslocamento = info['end']
            node.tipo = info['tipo']