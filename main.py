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

import os
import func
from InquisitiveLogicModelChecker import Model
from ILL_parser import parse

class App():

    def __init__(self):
        self.curr_input = ""

        # this is fairly unconventional and not really pythonic, possible solution is using argparse
        self.input_funcs = {'clr': self.clear_func,
            'a': self.add_func,
            'rm': self.remove_world_func,
            'q': self.quit_func,
            'p': self.print_func,
            'h': self.help_func,
            's': self.save_func,
            'l': self.load_func,
            'i': self.ignorant_func,
            'c': self.set_context_func,
            'is': self.add_information_state_func,
            'r': self.reset_func,
            'u': self.update_func,
            'e': self.eval_func,
            'ea': self.eval_alt_func}

        self.model = Model()
        self.variables = dict()

    def handle_input(self):
        args = self.curr_input.split()
        if len(args) == 0:
            return
        try:
            if args[0] not in self.input_funcs.keys():
                print("wrong command")
                return

            self.input_funcs[args[0]](*args[1:])
        except IndexError as e:
            print("index error")
        except FileNotFoundError as e:
            print("file location invalid")

    def reset_func(self):
        self.model = Model()

    def clear_func(self):
        os.system("cls" if os.name == "nt" else "clear") # Windows(nt) and Linux compatability :)

    def add_func(self, *args):
        try:
            self.model.add_world(*args)
        except:
            print("syntax error")

    def remove_world_func(self, *args):
        self.model.remove_world(*args)


    def quit_func(self):
        self.running = False

    def print_func(self):
        print(self.model)

    def save_func(self, *args):
        self.model.save(args[0])

    def load_func(self, *args):
        self.model = Model.load(args[0])

    def ignorant_func(self, *args):
        self.model.set_ignorant()

    def set_context_func(self, *args):
        string = str()
        for arg in args:
            string += arg
        
        alternatives = eval(string)
        self.model.set_context(alternatives)

    def add_information_state_func(self, *args):
        name = args[0]
        string = str()
        for arg in args[1:]:
            string += arg

        information_state = eval(string)
        if type(information_state) != tuple:
            information_state = tuple(sorted(list(information_state)))

        self.model.add_information_state(name, information_state)


    def update_func(self, *args):
        """
            Update the context of the model with the given string.
            Note: there is no error catching or correction. This function assumes that the delivered input is well formed.
        """
        string = ""
        for el in args:
            string += " " + el
        string = string.strip()
        self.model.update_context(parse(string))

    def eval_func(self, *args):
        """
            Evaluate the given string.
            Note: there is no error catching or correction. This function assumes that the delivered input string is well formatted.
        """
        string = ""
        for el in args:
            string += " " + el
        string = string.strip()
        
        tree = parse(string)
        print(tree.eval(self.model))

    def eval_alt_func(self, *args):

        string = ""
        for el in args:
            string += " " + el

        string = string.strip()

        tree = parse(string)
        print(tree.eval_alt(self.model))

        # implemented, but at what cost? No really, the implementations do not seem to be efficient at all...

    def help_func(self):
        """Display "help" message, in quotes because it is not quite explanatory"""
        help_message = \
"""===============================
Main helper functions:

(h)elp: print this help message
(clr)clear: clear the terminal
(p)rint: to print model 
(q)uit: to quit


Main model creation functions:

(s)ave [x]: saves model to location x
(l)oad [x]: loads model from location x
    x specifies a path    

(r)eset: reset model

Worlds and propositions:
(a)dd [w] [p]: add atomic propositions p to world w
    Note: You can add multiple propositions in one go. The propositions need to be deliniated with semicolons (;), comma's (,) or whitespaces ( )
    example:
    >>a w1 p;q,prop3 otherprop; t
    would add propsitions {p, q, prop3, otherprop, t} to w1
(rm)remove [w]: removes world w

Information States
(is) [name] [information state]: adds information state with name to model

    Note: the name should start with either an 's' or 'S'

    Note: Information state is interpreted directly with the python interpreter and should be of the form:

    ["w1", "w2"]

    example:
      >> is Stest ["w1","w2"]
      will add information state ("w1", "w2") with name "Stest" to model


Contexts:
(i)gnorant: set Context to ignorant (simply computes the powerset of the worlds of the model)
(c)ontext [alt]: set alternatives for context
    Note: this context is interpreted directly by the python interpreter so the context should be of the form:
        
    [alternative1, alternative2, alternative3]
    
    The alternatives themselves should be lists containing the world names e.g.:
        alternative1: ["w1", "w2"]
        alternative2: ["w3"]            # note how this is actually not an alternative and could be omitted
        alternative3: ["w1", "w3"]

    Total example:
    >> c [["w1","w2"],["w3"],["w1","w3"]]
    will result in a model with context: {(), ("w1",), ("w2",), ("w3",), ("w1","w2"), ("w1","w3")}

    Note how the so called 'alternatives' do not strictly have to be alternatives since the algorithm just computes the powerset.
    Note: One should first specify all worlds with the add function, since during interpreting the context all information states wich contain non-existing worlds will be pruned.

(u)pdate [s]: update context model with the sentence s


(e)val [s]: evaluates sentence s
(ea) eval alternative [s]: experimental method of evaluation using only alternatives instead of full propositions. This is functional and (hopefully) correct.

Language specification:

    operators:
        and, or, ior, then, models, not, ?
        Note: where ior is the inquisitive or and or is the 'normal' or

    Context:
        C

    Information states:
        s* or S*    Where "*" is a wildcard

    Atomic Propositions:
        any other character

    Examples:
        >> e C models not(p then (?q or t))      Does the context model not if p then whether q or t?
        >> u p or q                              updates the context with p or q
        >> e p and t                             Returns the standard proposition (p and t) which is a set of information states
        >> ea p and t                            return the set of alternatives of "e p and t". 
================================"""

        print(help_message)

    def get_input(self):
        self.curr_input = input(
            "input (h)elp (clr)clear: ")

    def mainloop(self):
        self.running = True

        while (self.running):
            self.get_input()
            self.handle_input()

if __name__ == "__main__":
    # This is the actual code that (should) run.
    app = App()
    app.mainloop()
