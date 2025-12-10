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

    def visita(self, node):
        if isinstance(node, Programa):
            for decl in node.declaracoes:
                self.visita(decl)
            
            node.total_vars = self.ts.deslocamento_atual
            
            self.visita(node.bloco)

        elif isinstance(node, Declaracao):
            for var_node in node.ids:
                self.ts.define(var_node.nome, node.tipo)
                
                info = self.ts.resolve(var_node.nome)
                var_node.tipo = info['tipo']
                var_node.deslocamento = info['end']

        elif isinstance(node, Bloco) or isinstance(node, ComandoComposto):
            for cmd in node.comandos:
                self.visita(cmd)

        elif isinstance(node, Atribuicao):
            self.visita(node.expressao)
            self.visita(node.var)

        elif isinstance(node, Condicional): 
            self.visita(node.cond)          
            self.visita(node.then_cmd)
            if node.else_cmd:
                self.visita(node.else_cmd)

        elif isinstance(node, Enquanto):
            self.visita(node.cond)
            self.visita(node.bloco)

        elif isinstance(node, Leitura):
            for v in node.vars:
                self.visita(v)
        
        elif isinstance(node, Escrita):
            for e in node.exps:
                self.visita(e)

        elif isinstance(node, CalculoBinario):
            self.visita(node.esq)
            self.visita(node.dir)
        
        elif isinstance(node, CalculoUnario):
            self.visita(node.expr)

        elif isinstance(node, Identificador):
            info = self.ts.resolve(node.nome)
            if not info:
                raise Exception(f"Erro Semântico: Variável '{node.nome}' não declarada.")
            
            node.deslocamento = info['end']
            node.tipo = info['tipo']