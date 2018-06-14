#include <stdio.h>
#include <ctype.h>
#include <math.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
int MAX_I=10000;
struct Parser_t {
  char* string;
};

typedef struct Parser_t Parser;

int hasNext(Parser* parser);
char peek(Parser* parser);
void skipWhitespace(Parser* parser);
float getValue(Parser* parser);
float parseExpression(Parser* parser);
float parseAddition(Parser* parser);
float parseMultiplication(Parser* parser);
float parseNegative(Parser* parser);
float parseValue(Parser* parser);
float parseNumber(Parser* parser);
float parseParenthesis(Parser* parser);

float getValue(Parser* parser) {
  float value = parseExpression(parser);
  skipWhitespace(parser);
  if (hasNext(parser)) {
    exit(-1);
  }
  return value;
}

void skipWhitespace(Parser* parser) {
  while (hasNext(parser)) {
    char r = peek(parser);
    if (r == ' ' || r == '\t' || r == '\n' || r == '\r') {
      parser->string = parser->string + 1;
    } else
      return;
  }
}

char peek(Parser* parser) {
  return parser->string[0];
}

int hasNext(Parser* parser) {
  return strlen(parser->string) != 0;
}

float parseExpression(Parser* parser) {
  return parseAddition(parser);
}

float parseAddition(Parser* parser) {
  float v = parseMultiplication(parser);
  float values[MAX_I];
  int v_i = 0;
  values[v_i] = v;
  v_i += 1;
  for (int i = 0; i < MAX_I && hasNext(parser); i++) {
    skipWhitespace(parser);
    char c = peek(parser);
    if (c == '+') {
      parser->string = parser->string + 1;
      float v = parseMultiplication(parser);
      values[v_i] = v;
      v_i +=1;
    } else if (c == '-') {
      parser->string = parser->string + 1;
      float v = parseMultiplication(parser);
      values[v_i] = v;
      v_i +=1;
    } else
      break;
  }
  float sum = 0.0;
  for (int i = 0; i < v_i; i++) {
    sum += values[i];
  }
  return sum;
}

float parseMultiplication(Parser* parser){
  float v = parseParenthesis(parser);
  float values[MAX_I];
  int v_i = 0;
  values[v_i] = v;
  v_i += 1;
  for (int i = 0; i < MAX_I && hasNext(parser); i++) {
    skipWhitespace(parser);
    char c = peek(parser);
    if (c == '*') {
      parser->string = parser->string + 1;
      float v = parseParenthesis(parser);
      values[v_i] = v;
      v_i += 1;
    } else if (c == '/') {
      parser->string = parser->string + 1;
      float denominator = parseParenthesis(parser);
      if (denominator == 0)
        exit(-1);
      values[v_i] = (1.0 / denominator);
      v_i += 1;
    } else
      break;
  }
  float value = 1.0;
  for (int i = 0; i < v_i; i++) value *= values[i];
  return value;
}

float parseParenthesis(Parser* parser) {
  skipWhitespace(parser);
  char c = peek(parser);
  if (c == '(') {
    parser->string = parser->string + 1;
    float value = parseExpression(parser);
    skipWhitespace(parser);
    c = peek(parser);
    if (c != ')')
      exit(-1);

    parser->string = parser->string + 1;
    return value;
  } else
    return parseNegative(parser);
}

float parseNegative(Parser* parser) {
  skipWhitespace(parser);
  char c = peek(parser);
  if (c == '-') {
    parser->string = parser->string + 1;
    return -1 * parseParenthesis(parser);
  } else
    return parseValue(parser);
}

float parseValue(Parser* parser) {
  skipWhitespace(parser);
  char c = peek(parser);
  if (isdigit(c))
    return parseNumber(parser);
  else
    exit(-1);
}


float parseNumber(Parser* parser) {
  skipWhitespace(parser);
  char strValue[MAX_I];
  int s_i = 0;
  char c;
  bool decimal_found = false;

  for (int i = 0; i < MAX_I && hasNext(parser); i++) {
    c = peek(parser);
    if (c == '.') {
      if (decimal_found)
        exit(-1);
      decimal_found = true;
      strValue[s_i] = '.';
      s_i += 1;
    } else if (isdigit(c)) {
      strValue[s_i] = c;
      s_i += 1;
    } else
      break;
    parser->string = parser->string + 1;
  }
  strValue[s_i] = 0;

  if (strlen(strValue) == 0) {
    exit(-1);
  }
  return atof(strValue);
}

int main(int argc, char** argv) {
  Parser parse;
  parse.string = argv[1];
  printf("%f\n", getValue(&parse));
  return 0;
}

