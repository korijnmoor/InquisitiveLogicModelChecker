# License
# MIT License
#
# Copyright (c) 2021 Korijn Moor
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Author
# Korijn Moor


import expressions as exp
import types

def create_token_lst(sentence):
    """
        Takes an input string and returns a token list.
        Note that tokens are either the class of the expression or a string paranthesis.
        Note also that in the input string the context should always be denoted as "C" and the names of any information state should always start with either "s" or "S".
    """

    tokens_dict = {
        "?": exp.WhetherOp,
        "not": exp.NotOp,
        "models": exp.ModelsOp,
        "and": exp.AndOp,
        "ior": exp.InqOrOp,
        "or": exp.OrOp,
        "then": exp.ThenOp,
        "C": exp.ContextExp("C"), # note: due to the limitations of this parser a context should always be called "C"
        "(": "(",
        ")": ")"
    }

    # adds whitespaces for correct seperation of (unary) operators and parantheses
    sentence = sentence.replace("?", " ? ")
    sentence = sentence.replace("(", " ( ")
    sentence = sentence.replace(")", " ) ")

    ret = []
    for el in sentence.split():
        if el not in tokens_dict.keys():
            # Handle information states or atomic propositions
            if el.startswith("s") or el.startswith("S"): # note: due to the limitations of the parser information states should always start with "S" or "s"
                ret.append(exp.InformationStateExp(el))
            else:
                ret.append(exp.PropExp(el))
        else:
            # Add operator
            ret.append(tokens_dict[el])

    return ret


def pop_operator(op_stack, res_stack):
    """
        Pops operator from op_stack and appends it to resultstack.
    """
    
    op = op_stack.pop()
    if issubclass(op, exp.UnaryOp):
        res_stack.append(op(res_stack.pop()))
    else:
        res_stack.append(op(res_stack.pop(-2), res_stack.pop()))


def handle_operator(op_stack, res_stack, operator):
    """
        handles operator by popping and appending correct operators to and from the operator stack and result stack
    """
    # handle unary operators
    while len(op_stack) > 0 and type(op_stack[-1]) != str and(issubclass(op_stack[-1], exp.UnaryOp)):
        pop_operator(op_stack, res_stack)
    
    #   ^
    #   |
    #   |-- These loops can probably be fused into one...
    #   |
    #   v

    # handle binary operators 
    while len(op_stack) > 0 and type(op_stack[-1]) != str and ((issubclass(op_stack[-1], exp.Expression)) and op_stack[-1] != exp.ModelsOp):
        pop_operator(op_stack, res_stack)
    
    op_stack.append(operator)


def parse(sentence):
    # parses a sentence from the Inquisitive Logic Language and returns the root of a somewhat AST tree.
    # This function implements the Shunting Yard Algorithm.

    res = []
    token_lst = create_token_lst(sentence)
    
    if(len(token_lst) == 0):
        return True
    
    if(len(token_lst) == 1):
        return token_lst[0]


    op_stack = [] # note, this 'stack' is just a list. Appending to lists is not very efficient (in python, due to reallocations), hence, the worst case is not very efficient.
    for el in token_lst:
        
        # if element is the context, a proposition or information state
        if issubclass(type(el), exp.VariableExp):
            res.append(el)
        
        # if element is a binary operator
        elif type(el) != str and issubclass(el, exp.BinaryOp): # Note: ordering of conditionals is important since issubclass(el... would throw error if el is string.
            handle_operator(op_stack, res, el)
        
        # if element is an unary operator
        elif type(el) != str and issubclass(el, exp.UnaryOp):
            op_stack.append(el)
        
        # if element is left paranthesis
        elif el == "(":
            op_stack.append(el)
        
        # if element is right paranthesis
        elif el == ")":
            while (type(op_stack[-1]) != str):
                pop_operator(op_stack, res)

            if op_stack[-1] == "(":
                op_stack.pop()

    while len(op_stack) > 0:
        
        pop_operator(op_stack, res)
    
    return res[0]


# small debugging segment
if __name__ == "__main__":
    root = parse("C models not (?p and not q) and not ?p or q")
    print(root)
