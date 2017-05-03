import logging

import re

operators = {
    '+': {'exec': lambda a, b: a + b, 'precedence': 0},
    '-': {'exec': lambda a, b: a - b, 'precedence': 0},
    '*': {'exec': lambda a, b: a * b, 'precedence': 1},
    '/': {'exec': lambda a, b: a / b, 'precedence': 1},
}

logger = logging.getLogger(__name__)


def calculate(expression):
    return rpn_execute(shunting_yard(validate_input(prepare_input(expression))))


def prepare_input(expression: str):
    parts = re.findall('-?[0-9.?]+|\(|\)|.', str(expression))
    return list(filter(lambda x: len(x), map(str.strip, parts)))


def validate_input(expression: [str]):
    for token in expression:
        if not token in operators and not is_number(token) and not token in ("(", ")"):
            raise SyntaxError("Invalid token %s" % token)

    return expression


def is_number(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def shunting_yard(expression: [str]):
    output_queue = []
    operator_stack = []

    for token in expression:

        if is_number(token):
            output_queue.append(token)
            continue

        if token == "(":
            # If it's a left bracket push it onto the stack
            operator_stack.append(token)
            continue

        if token == ")":
            while operator_stack and operator_stack[-1] != "(":
                # While there's not a left bracket at the top of the stack
                # Pop operators from the stack onto the output queue.
                output_queue.append(operator_stack.pop())

            # Pop the left bracket from the stack and discard it
            operator_stack.pop()

        if token in operators:
            while operator_stack and operator_stack[-1] not in ("(", ")") and operators[operator_stack[-1]][
                'precedence'] >= operators[token]['precedence']:
                # While there's an operator on the top of the stack with greater precedence:
                # Pop operators from the stack onto the output queue
                output_queue.append(operator_stack.pop())

            # Push the current operator onto the stack
            operator_stack.append(token)

    # While there's operators on the stack, pop them to the queue
    while operator_stack:
        output_queue.append(operator_stack.pop())

    logger.debug('RPN: %s' % ' '.join(output_queue))
    return output_queue


def rpn_execute(rpn: [str]):
    stack = []

    for value in rpn:
        if value in operators:
            try:
                b, a = stack.pop(), stack.pop()
            except IndexError:
                raise SyntaxError("Invalid expression")

            function = operators[value]['exec']

            if callable(function):
                stack.append(function(a, b))
        else:
            stack.append(int(value) if value.replace('-', '').isdigit() else float(value))

    return stack.pop()
