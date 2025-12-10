from ast_tascal import *

class GeradorMepa:
    mepa_ops = {
        '+': 'SOMA', 
        '-': 'SUBT', 
        '*': 'MULT', 
        'div': 'DIVI', 
        '/': 'DIVI',
        'and': 'CONJ', 
        'or': 'DISJ', 
        '=': 'CMIG', 
        '<>': 'CMDG',
        '<': 'CMME', 
        '<=': 'CMEG',
        '>': 'CMMA', 
        '>=': 'CMAG',
        'not': 'NEGA'
    }

    def __init__(self):
        self.codigo = []
        self.count_rotulos = 0
    
    def _novo_rotulo(self):
        rotulo = f"R{self.count_rotulos:02d}"
        self.count_rotulos += 1
        return rotulo
    
    def _emite(self, instr, arg=""):
        if arg != "":
            self.codigo.append(f"   {instr} {arg}")
        else:
            self.codigo.append(f"   {instr}")
    
    def _emite_rotulo(self, label):
        self.codigo.append(f"{label}: NADA")

    def junta_mepa(self):
        return "\n".join(self.codigo)

    def visita(self, node):
        nome_classe = node.__class__.__name__
        metodo = getattr(self, f'visita_{nome_classe}', self.visita_generica)
        return metodo(node)

    def visita_generica(self, node):
        raise Exception(f"Erro: Nó '{node.__class__.__name__}' não tem método de visita definido.")

    def visita_Programa(self, node):
        self._emite("INPP")
        if node.total_vars > 0:
            self._emite("AMEM", node.total_vars)
        
        self.visita(node.bloco)
        
        if node.total_vars > 0:
            self._emite(f"DMEM {node.total_vars}")

        self._emite("PARA")
        self._emite("FIM")

    def visita_Bloco(self, node):
        for cmd in node.comandos:
            self.visita(cmd)

    def visita_ComandoComposto(self, node):
        self.visita_Bloco(node)

    def visita_Atribuicao(self, node):
        self.visita(node.expressao)
        if node.var.deslocamento is None:
            raise Exception(f"Erro Interno: Variável {node.var.nome} sem endereço.")
        self._emite("ARMZ", f"0,{node.var.deslocamento}")

    def visita_Leitura(self, node):
        for var in node.vars:
            self._emite("LEIT")
            if var.deslocamento is not None:
                self._emite("ARMZ", f"0,{var.deslocamento}")

    def visita_Escrita(self, node):
        for exp in node.exps:
            self.visita(exp)
            self._emite("IMPR")

    def visita_Condicional(self, node):
        l_else = self._novo_rotulo()
        l_fim = self._novo_rotulo()

        self.visita(node.cond)
        self._emite("DSVF", l_else)
        
        self.visita(node.then_cmd)
        self._emite("DSVS", l_fim)
        
        self._emite_rotulo(l_else)
        if node.else_cmd:
            self.visita(node.else_cmd)
        
        self._emite_rotulo(l_fim)

    def visita_Enquanto(self, node):
        l_inicio = self._novo_rotulo()
        l_fim = self._novo_rotulo()

        self._emite_rotulo(l_inicio)
        self.visita(node.cond)
        self._emite("DSVF", l_fim)
        
        self.visita(node.bloco)
        self._emite("DSVS", l_inicio)
        
        self._emite_rotulo(l_fim)

    def visita_CalculoBinario(self, node):
        self.visita(node.esq)
        self.visita(node.dir)
        
        op = node.op.lower()
        if op in self.mepa_ops:
            self._emite(self.mepa_ops[op])
        else:
            raise Exception(f"Operador desconhecido: {op}")

    def visita_CalculoUnario(self, node):
        self.visita(node.expr)
        if node.op == 'not': 
            self._emite("NEGA")
        elif node.op == '-': 
            self._emite("INVR")

    def visita_Identificador(self, node):
        self._emite("CRVL", f"0,{node.deslocamento}")

    def visita_Numero(self, node):
        self._emite("CRCT", node.valor)

    def visita_Booleano(self, node):
        val = 1 if node.valor else 0
        self._emite("CRCT", val)