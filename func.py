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

import itertools
from copy import deepcopy


# Collection of helper functions, some of these are essential for the functioning of the model checker

def alternatives(proposition):
    proposition = set([frozenset(infstate) for infstate in proposition if all([not infstate.issubset(x) for x in proposition if infstate != x])])
    return proposition
        
def max(l_alternatives):
    """removes all the non-maximum information states from the list of alternatives"""

    total_alts = deepcopy(l_alternatives)
    for alt in total_alts:
        if any([alt.issubset(x) for x in l_alternatives if alt != x]):
            l_alternatives.remove(alt)

    return l_alternatives

            

def set_powerset(iterable):
    """
    ESSENTIAL FUNCTION
    powerset([1,2,3]) --> {() (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)} 
    
    Note: Tuples are an ordered datastructures. 
        The comparison of propositions (sets) would fail if the information states (tuples) were unordered.
        Therefore this function sorts the information states (tuples) alphabetically.
        The mathematical notion of information states and propositions differ at this point from the computational notions.
        (Ideally information states should be sets too. However a set in python is implemented with a hastable, and sets themselves
          are not hashable. Therefore sets cannot be elements of sets in python. 
          Which leads to the design choice of implementing information states with tuples.)

    Disclosure: this function is adapted from the stackoverflow thread: https://stackoverflow.com/questions/1482308/how-to-get-all-subsets-of-a-set-powerset
    """
    s = list(iterable)
    return set([frozenset(x) for x in itertools.chain.from_iterable(itertools.combinations(s, r) for r in range(len(s)+1))])

def info(iterable):
    """
        ESSENTIAL FUNCTION
        returns the flattened union of an iterable

        info([[1,2], [1,3],[2]]) --> {1,2,3}
    """
    buf = set()
    for el in iterable:
        
        buf = buf.union(set(el))
        
    return buf


def powerset(seq):
    """
        Alternative powerset function; not used
    """
    if len(seq) <= 1:
        yield seq
        yield {}
    else:
        for item in powerset(seq[1:]):
            yield [seq[0]] + item
            yield item

def func_gen(alt_ant, alt_conseq):
    """
        function generator function. Theoretically used to compute the function from alternatives to alternatives 
        in the alternative implementation of the implication.

        Not used.
    """ 
    
    l = len(alt_ant)
    comb_conseq = list(itertools.product(alt_conseq, repeat = l))

    
    def func(alt_in):
        dict()
        return alt_res
    
    yield func

if __name__ == "__main__":
    s = {"w1", "w2", "w3"}
    #s = {}
    for i in range(0,10):
        ps = set_powerset(s)

        print(ps)


