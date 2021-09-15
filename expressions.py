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

from InquisitiveLogicModelChecker import Model
import func as fn
from copy import deepcopy
from bitarray import bitarray
import itertools

class Expression ():
    """
        This is the main class for any expression
    """
    pass


class UnaryOp(Expression):
    """
        Main class for unary operators
    """
    def __init__(self, r):
        self.r = r

class BinaryOp(Expression):
    """
        Main class for binary operators
    """
    def __init__(self, l, r):
        self.l = l
        self.r = r

class VariableExp(Expression):
    """
        Main class for variable expressions. This includes atomic propositions, context expressions and information states.

        Note: that this class might seem empty however it is used as indicator for the parser.
    """
    
    pass


class WhetherOp(UnaryOp):
    """
        Implements the whether operator
    """
    def __str__(self):
        return "?(" + str(self.r) + ")"
    
    def eval(self, model):
        newOp = InqOrOp(self.r, NotOp(self.r))
        return newOp.eval(model)

    def eval_alt(self, model):
        return InqOrOp(self.r, NotOp(self.r)).eval_alt(model)

class NotOp(UnaryOp):
    """
        Implements the not operator
    """
    def __str__(self):
        return "not("+ str(self.r) + ")"

    def eval(self, model):
        info=fn.info(self.r.eval(model))
        
        return fn.set_powerset(model.worlds.difference(info))

    def eval_alt(self, model):
        reval = self.r.eval_alt(model)
        diff = frozenset(model.worlds.difference(fn.info(reval)))
        ret = set([diff])
        return ret

class ModelsOp(BinaryOp):
    """
        Implements the Models operator
    """
    def __str__(self):
        return str(self.l) + " |= " + str(self.r) 

    def eval(self, model):
        leval = self.l.eval(model)
        
        reval = self.r.eval(model)
        
        
        if type(leval) == set:
            return leval.issubset(reval)
        
        if type(leval) == frozenset:
            if (type(self.r) == ContextExp):
                return "syntax error"
            return (leval in reval)
        
        if type(reval) == frozenset:
            return "syntax error"
        
    def eval_alt(self, model):
        leval = self.l.eval_alt(model)
        reval = self.r.eval_alt(model)
        if (type(self.l) == InformationStateExp and type(self.r) == ContextExp) or type(self.r) == InformationStateExp:
            return "syntax error"
        return all([any([alt.issubset(x) for x in reval]) for alt in leval])


class AndOp(BinaryOp):
    """
        Implements the and operator
    """
    def __str__(self):
        return "(" + str(self.l) + " and " + str(self.r) + ")"

    def eval(self, model):
        leval = self.l.eval(model)
        reval = self.r.eval(model)
        
        return leval.intersection(reval)
    
    def eval_alt(self, model):
        leval = self.l.eval_alt(model)
        reval = self.r.eval_alt(model)
        
        new_alts = set()
        for s in leval:
            for t in reval:
                new_alts.add(s.intersection(t))
        res = fn.max(new_alts)
        
        return res

class InqOrOp(BinaryOp):
    """
        Implements the inquisitive or operator
    """
    def __str__(self):
        return "(" + str(self.l) + " or " + str(self.r) + ")"

    def eval(self, model):
        leval = self.l.eval(model)
        reval = self.r.eval(model)

        return leval.union(reval)

    def eval_alt(self, model):
        leval = self.l.eval_alt(model)
        reval = self.r.eval_alt(model)
        
        res = fn.max(leval.union(reval))
        return res



class OrOp(BinaryOp):
    """
        Implements the non-inquisitive or operator
    """
    def __str__(self):
        return "(" + str(self.l) + " or " + str(self.r) + ")"

    def eval(self, model):
        leval = self.l.eval(model)
        reval = self.r.eval(model)

        return fn.set_powerset(fn.info(leval.union(reval)))

    def eval_alt(self, model):
        leval = self.l.eval_alt(model)
        reval = self.r.eval_alt(model)
        
        res = set([frozenset(fn.info(leval).union(fn.info(reval)))])
        return res


class ThenOp(BinaryOp):
    """
        Implements the (I think correct) implication operator
    """
    def __str__(self):
        return "(" + str(self.l) + " -> " + str(self.r) + ")"

    def eval(self, model):
        """
            Naively tests for all possible information states.
            
            Explanation:
                Start gathering all possible information states (IS) and sort by length

                for each IS in possible IS:
                    if implication hold
                    Then
                        add to result
                        continue
                    else
                        remove all supersets from possible IS
                        continue
                    endif

            Note: definitely not the most efficient implementation...
        """
        result = set()
        possible = sorted(list(fn.set_powerset(model.worlds)), key=lambda informationState: len(informationState)) 
        while len(possible) > 0:
            informationState = possible.pop(0)
            
            # handles empty information states
            if len(informationState) == 0:
                result.add(informationState)
                continue

            # check implication condition:
            if not ModelsOp(InformationStateExp(None, informationState), self.l).eval(model) or ModelsOp(InformationStateExp(None, informationState), self.r).eval(model):
                result.add(informationState)
            else:
                possible = [x for x in possible if not informationState.issubset(x)] # trim possible information states

        return result

    def eval_alt(self, model):
        reval = self.r.eval_alt(model)
        leval = self.l.eval_alt(model)

        l = len(leval)
        func_res = list(itertools.product(reval, repeat = l))

        infs = set()
        for func in func_res:
            unions = list()
            for i, alternative in enumerate(leval):
                diff = model.worlds.difference(alternative)
                unions.append(diff.union(func[i]))
            
            infs.add(frozenset(set.intersection(*unions)))
            
        alt_res = fn.max(infs)

        return alt_res




class ContextExp(VariableExp):
    """
        Implements a Context expression
    """
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return str(self.name)

    def eval(self, model):
        return model.context

    def eval_alt(self, model):
        return fn.alternatives(model.context)

class PropExp(VariableExp):
    """
        Implements a Proposition expression
    """
    def __init__(self, name):
        self.name = name
    
    def __str__(self):
        return str(self.name)
    
    def eval(self, model):
        return fn.set_powerset(model.valuation[self.name])

    def eval_alt(self, model):
        return set([frozenset(model.valuation[self.name])])

class InformationStateExp(VariableExp):
    """
        Implements an Information State expression
    """
    def __init__(self, *args):
        self.name = args[0]
        if len(args) == 1:
            self.informationState = None
        else:
            self.informationState = args[1]


    def __str__(self):
        return str(self.name)

    def eval(self, model):
        if self.informationState == None:
            self.informationState = model.get_information_state(self.name)

        return frozenset(self.informationState)

    def eval_alt(self, model):
        return set([self.eval(model)])

if __name__ == "__main__":
    e1 = ModelsOp(ContextExp('C'), AndOp(PropExp('p'), PropExp('q')))
    e2 = WhetherOp(PropExp('q'))
    model = Model(worlds = {'w1', 'w2'},
              context = {('w1',), ()},
              valuation = {'q': {'w2'},
                           'p': {'w1', 'w2'}}
            )
    
    print(f"e2 : {e2}")
    print(f"model : {model}")
    print("e2 eval with model: {}".format(e2.eval(model)))
