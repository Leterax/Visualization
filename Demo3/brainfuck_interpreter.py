import sys


class BrainfuckInterpreter:

    def __init__(self):

        self.operations = {'>': self._increment_pointer, '<': self._decrement_pointer, '+': self._increment_value,
                           '-': self._decrement_value, '.': self._output, ',': self._input}

        self.memory = [0]
        self.pointer = 0
        self.input_buffer = ''

    def _get_current_value(self):
        return self.memory[self.pointer]

    def _set_current_value(self, value):
        self.memory[self.pointer] = value

    def _increment_pointer(self):
        self.pointer += 1
        if len(self.memory) <= self.pointer:
            self.memory.append(0)

    def _decrement_pointer(self):
        self.pointer -= 1
        if self.pointer < 0:
            raise Exception('Referencing Negative Memory Address')

    def _increment_value(self):
        self._set_current_value((self._get_current_value() + 1) % 256)

    def _decrement_value(self):
        self._set_current_value((self._get_current_value() - 1) % 256)

    def _output(self):
        print(str(chr(self._get_current_value())), end='')

    def _input(self):
        try:
            if len(self.input_buffer) == 0:
                self.input_buffer = input('?') + '\n'
            self._set_current_value(ord(self.input_buffer[0]))
            self.input_buffer = self.input_buffer[1:]
        except EOFError:
            pass

    def _currently_zero(self):
        return self._get_current_value() == 0

    def interpret(self, code):

        bracket_stack = []

        current_position = 0
        while current_position < len(code):

            character = code[current_position]

            if character in self.operations.keys():
                self.operations[character]()
            elif character == '[':
                if self._currently_zero():
                    bracket_delta = 1
                    while bracket_delta != 0:
                        current_position += 1
                        if code[current_position] == '[':
                            bracket_delta += 1
                        elif code[current_position] == ']':
                            bracket_delta -= 1
                else:
                    bracket_stack.append(current_position)
            elif character == ']':
                if self._currently_zero():
                    bracket_stack.pop()
                else:
                    current_position = bracket_stack[-1]
            current_position += 1

    def transpile(self, code, name):
        operations = {'>': 'p += 1\n', '<': 'p -= 1\n', '+': 'array[p] += 1\n',
                      '-': 'array[p] -= 1\n', '.': "print(chr(array[p]), end='')\n",
                      ',': "array[p]=ord(input('? '))\n"}
        py_code = """
# header code
p = 0
array = [0]*30_000
# begin trans-pile

"""
        current_position = 0
        current_tab = 0
        while current_position < len(code):
            character = code[current_position]
            if character in operations.keys():
                py_code += "    " * current_tab + operations[character]
            if character == '[':
                py_code += "    " * current_tab + 'while array[p] != 0:\n'
                current_tab += 1
            if character == ']':
                current_tab -= 1
            current_position += 1
        with open(name + '.py', 'w') as f:
            f.write(py_code)


def run_file(file_name):
    with open(file_name, 'r') as file:
        interpreter = BrainfuckInterpreter()
        code = file.read()
        interpreter.interpret(code)


def transpile_file(file_name):
    with open(file_name, 'r') as file:
        interpreter = BrainfuckInterpreter()
        code = file.read()
        interpreter.transpile(code, file_name[:-3])


def optimize(file):
    with open(file, 'r') as f:
        code = f.read()
        lines = code.split('\n')[6:]
        out = []
        occurrences = 0
        for index, line in enumerate(lines):
            if index + 1 > len(lines) - 1: break
            # print(f"{lines[index + 1]} == {line} = {lines[index + 1] == line}")

            if lines[index - 1] == line:
                occurrences += 1
            elif occurrences == 0:
                out.append(lines[index - 1])
            else:
                tab_width = lines[index - 1].split('    ')[:-1]
                statement = lines[index - 1].split('    ')[-1]
                if statement.startswith("print"):
                    # print(chr(array[p]), end='')
                    # >
                    # print(chr(array[p]) * 2, end='')]
                    statement = statement.split(',')
                    out.append(f"{len(tab_width) * '    '}{statement[0]} * {occurrences + 1}, end='')")
                else:
                    out.append(f"{len(tab_width) * '    '}{statement[:-1]}{occurrences+1}")
                occurrences = 0

        py_code = """
# header code
p = 0
array = [0]*30_000
# begin trans-pile

"""
        with open(file, 'w') as of:
            of.write(py_code)
            of.write('\n'.join(out))
            of.write('\n')


if __name__ == '__main__':

    if len(sys.argv) > 1:
        for file_name in sys.argv[1:]:
            run_file(file_name)
    else:
        i = input('? ')
        print(i[-3:])
        if i[-3:] == '.bf':
            print("transpiling")
            transpile_file(i)
        if i[-3:] == '.py':
            print("optimizing")
            optimize(i)
        print('Done')
