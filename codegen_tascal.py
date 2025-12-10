from ast_tascal import *

class GeradorMepa:
    def __init__(self):
        self.codigo = []
        self.count_rotulos = 0
    
    def novo_rotulo(self):
        self.count_rotulos += 1
        return f"L{self.count_rotulos}"
    
    def emit(self, instr, arg=""):
        if arg != "":
            self.codigo.append(f"   {instr} {arg}")
        else:
            self.codigo.append(f"   {instr}")
    
    def emit_label(self, label):
        self.codigo.append(f"{label}: NADA")

    def visit(self, node):
        if isinstance(node, Programa):
            self.emit("INPP")
            if node.total_vars > 0:
                self.emit("AMEM", node.total_vars)
            
            self.visit(node.bloco)
            
            if node.total_vars > 0:
                self._emite(f"DMEM {node.total_vars}")

            self.emit("PARA")
            self.emit("FIM")

        elif isinstance(node, Bloco) or isinstance(node, ComandoComposto):
            for cmd in node.comandos:
                self.visit(cmd)

        elif isinstance(node, Atribuicao):
            self.visit(node.expressao)
            if node.var.deslocamento is None:
                raise Exception(f"Erro Interno: Variável {node.var.nome} sem endereço.")
            self.emit("ARMZ", f"0,{node.var.deslocamento}")

        elif isinstance(node, Read):
            for var in node.vars:
                self.emit("LEIT")
                if var.deslocamento is None:
                     pass 
                self.emit("ARMZ", f"0,{var.deslocamento}")

        elif isinstance(node, Write):
            for exp in node.exps:
                self.visit(exp)
                self.emit("IMPR")

        elif isinstance(node, If):
            l_else = self.novo_rotulo()
            l_fim = self.novo_rotulo()

            self.visit(node.condicao)
            self.emit("DSVF", l_else)
            
            self.visit(node.then_cmd)
            self.emit("DSVS", l_fim)
            
            self.emit_label(l_else)
            if node.else_cmd:
                self.visit(node.else_cmd)
            
            self.emit_label(l_fim)

        elif isinstance(node, While):
            l_inicio = self.novo_rotulo()
            l_fim = self.novo_rotulo()

            self.emit_label(l_inicio)
            self.visit(node.condicao)
            self.emit("DSVF", l_fim)
            
            self.visit(node.body)
            self.emit("DSVS", l_inicio)
            
            self.emit_label(l_fim)

        elif isinstance(node, BinOp):
            self.visit(node.esq)
            self.visit(node.dir)
            
            ops = {
                '+': 'SOMA', '-': 'SUBT', '*': 'MULT', 'div': 'DIVI',
                'and': 'CONJ', 'or': 'DISJ',
                '=': 'CMIG', '<>': 'CMDG',
                '<': 'CMME', '<=': 'CMEG',
                '>': 'CMMA', '>=': 'CMAG'
            }
            if node.op in ops:
                self.emit(ops[node.op])

        elif isinstance(node, UnOp):
            self.visit(node.expr)
            if node.op == 'not': self.emit("NEGA")
            elif node.op == '-': self.emit("INVR")

        elif isinstance(node, Var):
            self.emit("CRVL", f"0,{node.deslocamento}")

        elif isinstance(node, Num):
            self.emit("CRCT", node.valor)

        elif isinstance(node, Bool):
            self.emit("CRCT", 1 if node.valor else 0)

    def get_code(self):
        return "\n".join(self.codigo)