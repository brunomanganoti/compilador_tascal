import sys
from lexico_tascal_mepa import make_lexer
from parser_tascal_mepa import make_parser
from sem_tascal import AnalisadorSemantico
from codegen_tascal import GeradorMepa

def main():
    if sys.stdin.isatty():
        print("Erro: Utilize redirecionamento de entrada.")
        print("Exemplo: python main.py < programa.tascal")
        return

    try:
        dados = sys.stdin.read()
    except Exception as e:
        print(f"Erro ao ler entrada: {e}")
        return

    lexer = make_lexer()
    parser = make_parser()
    
    print("Iniciando Parser...", file=sys.stderr)
    ast_raiz = parser.parse(dados, lexer=lexer)
    
    if not ast_raiz:
        print("Erro: Falha ao gerar a árvore sintática.", file=sys.stderr)
        return

    print("Iniciando Análise Semântica...", file=sys.stderr)
    semantico = AnalisadorSemantico()
    try:
        semantico.visita(ast_raiz)
    except Exception as e:
        print(f"\nERRO SEMÂNTICO: {e}")
        return

    print("Gerando Código MEPA...", file=sys.stderr)
    gerador = GeradorMepa()
    try:
        gerador.visita(ast_raiz)
    except Exception as e:
        print(f"\nERRO DE GERAÇÃO: {e}")
        return

    print(gerador.junta_mepa()) # Saída MEPA

if __name__ == "__main__":
    main()