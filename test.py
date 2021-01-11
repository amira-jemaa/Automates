# -*- coding: utf-8 -*-
"""
Code modifiable.
"""

from automate import Automate
from state import State
from transition import Transition
from parser import *


i1 = Automate.creationAutomate("Fichiers de test/i1")
i1.show("u1")
i2 = Automate.creationAutomate("Fichiers de test/i2")
i2.show("u2")
i2det= Automate.determinisation(i2)
i2det.show("determinisationU2")
c = Automate.concatenation(i1, i2)
c.show("con")

e = Automate.intersection(i1, i2)
print e
e.show("intersect")

auto = Automate.creationAutomate("exempleAutomate.txt")
auto_etoile = Automate.etoile(auto)
auto_etoile.show("auto*")
