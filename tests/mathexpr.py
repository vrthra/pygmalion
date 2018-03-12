# A really simple expression evaluator supporting the
# four basic math functions, parentheses, and variables.

class Parser:
    def __init__(self, string, vars={}):
        self.string = string
        self._tstr = string
        self.index = 0
        self.vars = {
            'pi': 3.141592653589793,
            'e': 2.718281828459045
        }
        for var in vars.keys():
            if self.vars.get(var) != None:
                raise Exception("Cannot redefine the value of " + var)
            self.vars[var] = vars[var]

    def getValue(self):
        value = self.parseExpression()
        self.skipWhitespace()
        if self.hasNext():
            raise Exception(
                "Unexpected character found: '" +
                self.peek() +
                "' at index " +
                str(self.index))
        return value

    def peek(self):
        return self.string[self.index:self.index + 1]

    def hasNext(self):
        return self.index < len(self.string)

    def skipWhitespace(self):
        while self.hasNext():
            if self.peek() in ' \t\n\r':
                self.index += 1
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
                self.index += 1
                values.append(self.parseMultiplication())
            elif char == '-':
                self.index += 1
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
                self.index += 1
                values.append(self.parseParenthesis())
            elif char == '/':
                div_index = self.index
                self.index += 1
                denominator = self.parseParenthesis()
                if denominator == 0:
                    raise Exception(
                        "Division by 0 kills baby whales (occured at index " +
                        str(div_index) +
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
            self.index += 1
            value = self.parseExpression()
            self.skipWhitespace()
            if self.peek() != ')':
                raise Exception(
                    "No closing parenthesis found at character "
                    + str(self.index))
            self.index += 1
            return value
        else:
            return self.parseNegative()

    def parseNegative(self):
        self.skipWhitespace()
        char = self.peek()
        if char == '-':
            self.index += 1
            return -1 * self.parseParenthesis()
        else:
            return self.parseValue()

    def parseValue(self):
        self.skipWhitespace()
        char = self.peek()
        if char in '0123456789.':
            return self.parseNumber()
        else:
            return self.parseVariable()

    def parseVariable(self):
        self.skipWhitespace()
        var = ''
        while self.hasNext():
            char = self.peek()
            if char.lower() in '_abcdefghijklmnopqrstuvwxyz0123456789':
                var += char
                self.index += 1
            else:
                break

        value = self.vars.get(var, None)
        if value == None:
            raise Exception(
                "Unrecognized variable: '" +
                var +
                "'")
        return float(value)

    def parseNumber(self):
        self.skipWhitespace()
        strValue = ''
        decimal_found = False
        char = ''

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
            elif char in '0123456789':
                strValue += char
            else:
                break
            self.index += 1

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
    return [
        '1 + 2',
        '200 / 10',
        '(22 + 32)',
        '(12 * 13 - 2)',
        '((2 + 1) + 2)',
        '-1 + (3 * 2)',
    ]

if __name__ == "__main__":
    import sys
    main(sys.argv[1])
