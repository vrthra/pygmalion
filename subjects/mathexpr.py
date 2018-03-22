# A really simple expression evaluator supporting the
# four basic math functions, parentheses, and variables.

class Parser:
    def __init__(self, string, vars={}):
        self.ostring = string
        self.string = string
        self._tstr = string
        self.vars = {
            'pi': 3.141592653589793,
            'e': 2.718281828459045
        }
        for var in vars.keys():
            if self.getVarValue(var) != None:
                raise Exception("Cannot redefine the value of " + var)
            self.vars[var] = vars[var]

    def hasVar(self, v):
        for k in self.vars.keys():
            if v == k:
                return True
        return False

    def getVarValue(self, v, default):
        if not self.hasVar(v): return default
        return self.vars[v]

    def getValue(self):
        value = self.parseExpression()
        self.skipWhitespace()
        if self.hasNext():
            raise Exception(
                "Unexpected character found: '" +
                self.peek() +
                "' at " +
                self.ostring[:len(self.string)])
        return value

    def peek(self):
        return self.string[0:1]

    def hasNext(self):
        return self.string != ''

    def skipWhitespace(self):
        while self.hasNext():
            if self.peek().in_(' \t\n\r'):
                self.string = self.string[1:]
                self._tstr = self.string
            else:
                return

    def parseExpression(self):
        return self.parseAddition()

    def parseAddition(self):
        values = [self.parseMultiplication()]
        while True:
            self.skipWhitespace()
            char = self.peek()
            if char == '+':
                self.string = self.string[1:]
                self._tstr = self.string
                values.append(self.parseMultiplication())
            elif char == '-':
                self.string = self.string[1:]
                self._tstr = self.string
                values.append(-1 * self.parseMultiplication())
            else:
                break
        return sum(values)

    def parseMultiplication(self):
        values = [self.parseParenthesis()]
        while True:
            self.skipWhitespace()
            char = self.peek()
            if char == '*':
                self.string = self.string[1:]
                self._tstr = self.string
                values.append(self.parseParenthesis())
            elif char == '/':
                self.string = self.string[1:]
                self._tstr = self.string
                denominator = self.parseParenthesis()
                if denominator == 0:
                    raise Exception(
                        "Division by 0 kills baby whales (occured at index " +
                        len(self.ostring) - len(self.string) +
                        ")")
                values.append(1.0 / denominator)
            else:
                break
        value = 1.0
        for factor in values:
            value *= factor
        return value

    def parseParenthesis(self):
        self.skipWhitespace()
        char = self.peek()
        if char == '(':
            self.string = self.string[1:]
            self._tstr = self.string
            value = self.parseExpression()
            self.skipWhitespace()
            c = self.peek()
            if c != ')':
                raise Exception(
                    "No closing parenthesis found at character "
                    + self.oindex[0:len(self.string)])

            self.string = self.string[1:]
            self._tstr = self.string
            return value
        else:
            return self.parseNegative()

    def parseNegative(self):
        self.skipWhitespace()
        char = self.peek()
        if char == '-':
            self.string = self.string[1:]
            self._tstr = self.string
            return -1 * self.parseParenthesis()
        else:
            return self.parseValue()

    def parseValue(self):
        self.skipWhitespace()
        char = self.peek()
        if char.in_('0123456789.'):
            return self.parseNumber()
        else:
            return self.parseVariable()

    def parseVariable(self):
        self.skipWhitespace()
        var = None
        while self.hasNext():
            char = self.peek()
            if char.lower().in_('_abcdefghijklmnopqrstuvwxyz0123456789'):
                var += char
                self.string = self.string[1:]
                self._tstr = self.string
            else:
                break

        value = self.getVarValue(var, None)
        if value == None:
            raise Exception(
                "Unrecognized variable: '" +
                var +
                "'")
        return float(value)

    def parseNumber(self):
        self.skipWhitespace()
        strValue = ''
        char = ''
        decimal_found = False

        while self.hasNext():
            char = self.peek()
            if char == '.':
                if decimal_found:
                    raise Exception(
                        "Found an extra period in a number at character " +
                        str(self.index) +
                        ". Are you European?")
                decimal_found = True
                strValue += '.'
            elif char.in_('0123456789'):
                strValue += char
            else:
                break
            self.string = self.string[1:]
            self._tstr = self.string

        if len(strValue) == 0:
            if char == '':
                raise Exception("Unexpected end found")
            else:
                raise Exception(
                    "I was expecting to find a number at character " +
                    str(self.index) +
                    " but instead I found a '" +
                    char +
                    "'. What's up with that?")

        return float(strValue)

        # p = Parser(expression, vars)

def main(s):
    parse = Parser(s)
    # if s in ["a", "b", "c"]:
    #     return
    print(parse.getValue())

def inputs():
    import os.path
    if os.path.exists('tests/mathexpr.input'):
        return [l.strip() for l in open('tests/mathexpr.input') if not l[0] == '#']

    return ['1 + 2',
            '2 * 3 + 1',
            '(1-2)/3',
            '22.2 - 0.1',
            '(1)*(2)']

def skip_classes():
    return []

if __name__ == "__main__":
    import sys
    main(taintedstr.tstr(sys.argv[1]))
