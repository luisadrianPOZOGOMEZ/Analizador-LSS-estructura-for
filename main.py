from flask import Flask, request, render_template
import ply.lex as lex
import ply.yacc as yacc

app = Flask(__name__)

# Definición de tokens para el analizador léxico
tokens = (
    'PR_FOR', 'PR_IF', 'PR_ELSE', 'PR_WHILE', 'PR_RETURN', 'TYPE_INT',
    'ID', 'NUM', 'SEMICOLON', 'LBRACE', 'RBRACE', 'LPAREN', 'RPAREN',
    'LBRACKET', 'RBRACKET', 'EQUALS', 'LT', 'GT', 'NOT', 'PLUS', 'MINUS',
    'TIMES', 'DIVIDE', 'STRING', 'DOT'
)

# Reglas para los tokens
t_PR_FOR = r'for'
t_PR_IF = r'if'
t_PR_ELSE = r'else'
t_PR_WHILE = r'while'
t_PR_RETURN = r'return'
t_TYPE_INT = r'int'
t_ID = r'[a-zA-Z_][a-zA-Z_0-9]*'
t_NUM = r'\d+'
t_SEMICOLON = r';'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_EQUALS = r'='
t_LT = r'<='
t_GT = r'>'
t_NOT = r'!'
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_DOT = r'\.'


def t_STRING(t):
    r'"[^"]*"'
    t.value = t.value[1:-1]  # Remueve las comillas
    return t


t_ignore = ' \t'


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_error(t):
    print(f"Carácter ilegal '{t.value[0]}'")
    t.lexer.skip(1)


lexer = lex.lex()

# Variables globales para el análisis semántico
semantic_errors = []
lexical_results = {'PR': 0, 'ID': 0, 'NUM': 0, 'SYM': 0, 'ERR': 0}


# Reglas de la gramática
def p_program(p):
    '''program : statement_list'''


def p_statement_list(p):
    '''statement_list : statement
                     | statement_list statement'''


def p_statement(p):
    '''statement : for_statement
                | print_statement'''


def p_for_statement(p):
    '''for_statement : PR_FOR LPAREN TYPE_INT ID EQUALS NUM SEMICOLON ID LT NUM SEMICOLON ID PLUS PLUS RPAREN LBRACE print_statement RBRACE'''
    if p[4] != 'i' or p[8] != 'i' or p[12] != 'i':
        semantic_errors.append("Error semántico: La variable del bucle 'for' debe ser 'i'.")
    if p[6] != '1':
        semantic_errors.append("Error semántico: El bucle 'for' debe iniciar con 'i = 1'.")
    if p[10] != '19':
        semantic_errors.append("Error semántico: El bucle 'for' debe terminar con 'i <= 19'.")


def p_print_statement(p):
    '''print_statement : ID DOT ID DOT ID LPAREN STRING RPAREN SEMICOLON'''
    if p[1] != 'System' or p[3] != 'out' or p[5] != 'println':
        semantic_errors.append("Error semántico: Uso incorrecto de 'System.out.println'.")
    if p[7] != 'hola':
        semantic_errors.append("Error semántico: El mensaje debe ser exactamente 'hola'.")


def p_error(p):
    if p:
        print(f"Error de sintaxis en el token '{p.value}'")
    else:
        print("Error de sintaxis al final del archivo")


parser = yacc.yacc()


def analyze_lexical(code):
    lexer.input(code)
    global lexical_results
    lexical_results = {'PR': 0, 'ID': 0, 'NUM': 0, 'SYM': 0, 'ERR': 0}
    rows = []
    while True:
        tok = lexer.token()
        if not tok:
            break

        print(f"Token: {tok.type}, Value: {tok.value}")  # Debug print

        # Mapear tipos de tokens a categorías
        if tok.type.startswith('PR_') or tok.type == 'TYPE_INT':
            category = 'PR'
        elif tok.type == 'ID':
            category = 'ID'
        elif tok.type == 'NUM':
            category = 'NUM'
        elif tok.type in ['SEMICOLON', 'LBRACE', 'RBRACE', 'LPAREN', 'RPAREN', 'LBRACKET', 'RBRACKET', 'EQUALS', 'LT',
                          'GT', 'NOT', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'DOT']:
            category = 'SYM'
        elif tok.type == 'STRING':
            category = 'SYM'
            lexical_results['SYM'] += 2  # Contamos las comillas de apertura y cierre
        else:
            category = 'ERR'
            print(f"Error: Token desconocido '{tok.type}'")  # Debug print

        lexical_results[category] += 1

        # Crear una fila para cada token
        row = [''] * len(lexical_results)
        row[list(lexical_results.keys()).index(category)] = 'x'
        rows.append(row)

    print(rows)  # Debug print
    return rows


def analyze_syntactic(code):
    global semantic_errors
    semantic_errors = []
    result = parser.parse(code, lexer=lexer)
    if result is None:
        return "Error sintáctico", code
    elif semantic_errors:
        return " ".join(semantic_errors), code
    else:
        return "Sintaxis y semántica correctas", code


@app.route('/', methods=['GET', 'POST'])
def index():
    code = ''
    lexical_rows = []
    total_results = {'PR': 0, 'ID': 0, 'NUM': 0, 'SYM': 0, 'ERR': 0}
    syntactic_result = ''
    if request.method == 'POST':
        code = request.form['code']
        lexical_rows = analyze_lexical(code)
        total_results = lexical_results
        syntactic_result, _ = analyze_syntactic(code)
    return render_template('index.html', code=code, lexical=lexical_rows, total=total_results,
                           syntactic=syntactic_result)


if __name__ == '__main__':
    app.run(debug=True)