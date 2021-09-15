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

import pickle
import json
from collections import defaultdict
import func as fn
import re
from copy import deepcopy

class Model:
    
    def __init__(self, *args, **kwargs):
        self.worlds = kwargs.get("worlds", set())
        self.context = kwargs.get("context", set())
        self.valuation = kwargs.get("valuation", defaultdict(set))
        self.information_states = kwargs.get("information_states", dict())

    def clean_valuations(self):
        """"removes all worlds that are not also in worlds"""
        for key, value in self.valuation.items():
            new_value = [w for w in value if w in self.worlds]
            self.valuation[key] = new_value
    
    def add_world(self, *args):
        """add a world to the set of worlds and also append the world to the correct valuations"""
        
        w = args[0]
        if w not in self.worlds:
            self.worlds.add(w)
        
        if len(args) > 1:
            valuation = ""
            for arg in args[1:]:
                valuation += arg + " "
            valuation = re.split(",|;|\s|:",valuation.strip())
            for val in valuation:
                self.valuation[val].add(w)

    def remove_world(self, *args):
        """Removes a world from the model"""
        w = args[0]
        if w in self.worlds:
            self.worlds.remove(w)

        if len(self.context) > 0:
            for infstate in deepcopy(self.context):
                if w in infstate:
                    self.context.remove(infstate)
        
        if len(self.valuation) > 0:
            for key, value in self.valuation.items():
                if w in value:
                    self.valuation[key].remove(w)

    def set_worlds(self, worlds):
        """"Set the worlds to the set of worlds given"""
        self.worlds = worlds
        self.clean_valuations()

    def set_context(self, context, prune=True):
        """Set current context to context"""
        self.context = set([tuple()])
        for alternative in context:
            self.context = self.context.union(fn.set_powerset(alternative))
        if prune:
            self.prune_context()
        

    def set_ignorant(self):
        """"Set the ignorant context"""
        self.context = fn.set_powerset(self.worlds)

    def update_context(self, proposition):
        """Update the context with proposition"""
        self.context = self.context.intersection(proposition.eval(self))

    def prune_context(self):
        """Removes all information states from the context containing worlds that are not contained in the model"""
        self.context = set([c for c in self.context if all([True if w in self.worlds else False for w in c ])]) 

    def add_information_state(self, name, information_state):
        """Add an information state"""
        self.information_states[name] = information_state

    def get_information_state(self, name):
        """Returns the information state or False when there is none with that name"""
        if name in self.information_states.keys():
            return self.information_states[name]
        else: 
            return False

    def reset_information_states(self):
        self.information_states = dict()

    def freeze_dict(self, this_dict):
        """Searches through dictionairy and freezes all elements into lists"""

        for key, value in this_dict.items():
            if type(value) == set:
                this_dict[key] = list(value)
            if type(value) == dict or type(value) == defaultdict:
                this_dict[key] = self.freeze_dict(value)

        return this_dict


    """Note: These save and load functions are very much not safe! because they just (un)pickle binaries"""
    def save(self, location):
        # prepare location
        if not location.endswith('.p'):
            location += '.p'

        # prepare values
        retdict = self.freeze_dict(self.__dict__)

        # save file
        with open(location, "w") as f:
            json.dump(retdict, f)

        # repair any frozen elements
        self.unfreeze(self.__dict__)

    def unfreeze(self, this_dict):
        """
            unfreezes the dictionary into the right types. Notice how this is dependend on the datatypes used by this model Class.
        """
        this_dict["worlds"] = set(this_dict["worlds"])
        this_dict["context"] = set([frozenset(x) for x in this_dict["context"]])
        new_d = defaultdict(set)
        for k, v in this_dict["valuation"].items():
            new_d[k] = set(v)
        this_dict["valuation"] = new_d
        new_d = dict()
        for k, v in this_dict["information_states"].items():
            new_d[k] = tuple(sorted(v))
        this_dict["information_states"] = new_d

        return this_dict

    @classmethod
    def load(self, location):
        if not location.endswith('.p'):
            location += '.p'
        with open(location, "r") as f:
            res = json.load(f)

        return Model(**self.unfreeze(None, res))

    def __str__(self):
        return str(self.__dict__)




if(__name__ == "__main__"):
    W = ["w1", "w2", "w3"]
    C = list()
    m = Model(worlds = W) #context = set(set(w1,w2), set(w1), set(w2)), valuation = dict("w1":"p", "w2":"q"))
    

    print(m2)
    print(m.worlds)

