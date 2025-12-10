import re
import json
import os

class Tokenizer:
    def __init__(self, source_code):
        self.source = source_code
        self.tokens = []

    def tokenize(self):
        token_pattern = re.compile(r'"([^"]*)"|(\d+\.?\d*)|({|}|\[|\]|=|:|,)|([A-Za-z_]\w*)')
        lines = self.source.splitlines()
        line_no = 0

        for raw_line in lines:
            line_no += 1
            line = raw_line.strip()
            if not line or line.startswith('#'):
                continue

            for match in token_pattern.finditer(line):
                str_val, num_val, op_val, id_val = match.groups()

                if str_val is not None:
                    self.tokens.append(('STRING', str_val, line_no))

                elif num_val is not None:
                    val = float(num_val) if '.' in num_val else int(num_val)
                    self.tokens.append(('NUMBER', val, line_no))

                elif op_val is not None:
                    self.tokens.append(('OPERATOR', op_val, line_no))

                elif id_val is not None:
                    self.tokens.append(('IDENTIFIER', id_val, line_no))

        return self.tokens


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.i = 0
        self.symbol_table = {}

    def get_token(self):
        if self.i < len(self.tokens):
            t = self.tokens[self.i]
            self.i += 1
            return t
        return None

    def peek_token(self):
        if self.i < len(self.tokens):
            return self.tokens[self.i]
        return None

    def expect(self, expected_values, msg=None):
        tok = self.get_token()
        if tok is None:
            raise SyntaxError(msg or "Token esperado {} pero se encontró EOF.".format(expected_values))

        expected = (expected_values,) if isinstance(expected_values, str) else expected_values
        if tok[1] not in expected:
            lineno = tok[2]
            raise SyntaxError(
                msg or "Token inesperado '{}' en línea {}. Se esperaba uno de {}."
                .format(tok[1], lineno, expected)
            )
        return tok

    def parse(self):
        while self.peek_token() is not None:
            key_tok = self.get_token()
            if key_tok[0] not in ('IDENTIFIER', 'STRING'):
                raise SyntaxError("Se esperaba identificador o cadena, se encontró {}.".format(key_tok))

            key = key_tok[1]

            eq_tok = self.get_token()
            if eq_tok is None or eq_tok[1] != '=':
                raise SyntaxError("Se esperaba '=' después de la clave '{}'.".format(key))

            value = self.parse_value()

            if key in self.symbol_table:
                print("Warning: redefinición de '{}'.".format(key))

            self.symbol_table[key] = value

        return self.symbol_table

    def parse_value(self):
        tok = self.peek_token()
        if tok is None:
            raise SyntaxError("Se esperaba un valor pero llegó EOF.")

        ttype, tval, _ = tok

        if ttype in ('STRING', 'NUMBER'):
            self.get_token()
            return tval

        if ttype == 'OPERATOR' and tval == '{':
            return self.parse_block()

        if ttype == 'OPERATOR' and tval == '[':
            return self.parse_list()

        if ttype == 'IDENTIFIER':
            self.get_token()
            return tval

        raise SyntaxError("Valor inesperado '{}'.".format(tval))

    def parse_block(self):
        self.get_token()  # consume '{'
        block = {}

        while True:
            peek = self.peek_token()
            if peek is None:
                raise SyntaxError("Bloque no cerrado: se llegó a EOF.")

            if peek[0] == 'OPERATOR' and peek[1] == '}':
                self.get_token()
                break

            key_tok = self.get_token()
            if key_tok[0] not in ('IDENTIFIER', 'STRING'):
                raise SyntaxError("Se esperaba clave, se encontró {}.".format(key_tok))

            key = key_tok[1]

            sep_tok = self.get_token()
            if sep_tok is None or sep_tok[1] not in ('=', ':'):
                raise SyntaxError("Se esperaba ':' o '=' después de la clave '{}'.".format(key))

            value = self.parse_value()
            block[key] = value

            peek2 = self.peek_token()
            if peek2 and peek2[0] == 'OPERATOR' and peek2[1] == ',':
                self.get_token()
                continue

        return block

    def parse_list(self):
        self.get_token()  # consume '['
        items = []

        while True:
            peek = self.peek_token()
            if peek is None:
                raise SyntaxError("Lista no cerrada: EOF inesperado.")

            if peek[0] == 'OPERATOR' and peek[1] == ']':
                self.get_token()
                break

            if peek[0] == 'OPERATOR' and peek[1] == '[':
                item = self.parse_list()
            elif peek[0] == 'OPERATOR' and peek[1] == '{':
                item = self.parse_block()
            else:
                item = self.parse_value()

            items.append(item)

            peek2 = self.peek_token()
            if peek2 and peek2[0] == 'OPERATOR' and peek2[1] == ',':
                self.get_token()
                continue

        return items


# ---- funciones IO ----
def load_file(filepath):
    if not os.path.exists(filepath):
        print("Error: archivo '{}' no encontrado.".format(filepath))
        return None

    f = open(filepath, 'r')
    content = f.read()
    f.close()
    return content


def save_ast(ast, input_path):
    base = os.path.basename(input_path)
    name, _ = os.path.splitext(base)
    out_name = "arbol_{}.ast".format(name)

    try:
        f = open(out_name, 'w')
        json.dump(ast, f, indent=4, ensure_ascii=False)
        f.close()
        print("AST guardado en '{}'".format(out_name))
    except Exception as e:
        print("Error al guardar AST:", e)


# ---- main ----
def main():
    path = raw_input("Ingrese el nombre del archivo .brik: ").strip()
    if not path:
        print("No se especificó archivo.")
        return

    source = load_file(path)
    if source is None:
        return

    tokenizer = Tokenizer(source)
    tokens = tokenizer.tokenize()

    print("--- Tokens reconocidos (tipo, valor, línea) ---")
    for t in tokens:
        print(t)
    print("Total tokens:", len(tokens))

    parser = Parser(tokens)
    try:
        ast = parser.parse()
        print("\n--- AST construido ---")
        print(json.dumps(ast, indent=4, ensure_ascii=False))
        save_ast(ast, path)
    except SyntaxError as e:
        print("Error durante el análisis:", e)


if __name__ == "__main__":
    main()
