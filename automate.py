# -*- coding: utf-8 -*-
from transition import *
from state import *
import os
import copy
from sp import *
from parser import *
from itertools import product
from automateBase import AutomateBase


class Automate(AutomateBase):
    def succElem(self, state, lettre):
        """State x str -> list[State]
        rend la liste des états accessibles à partir d'un état
        state par l'étiquette lettre
        """
        successeurs = []
        # t: Transitions
        for t in self.getListTransitionsFrom(state):
            if t.etiquette == lettre and t.stateDest not in successeurs:
                successeurs.append(t.stateDest)
        return successeurs

    def succ(self, listStates, lettre):
        """list[State] x str -> list[State]
        rend la liste des états accessibles à partir de la liste d'états
        listStates par l'étiquette lettre
        """
        successeurs = []
        for state in listStates:
            for t in self.getListTransitionsFrom(state):
                if t.etiquette == lettre and t.stateDest not in successeurs:
                    successeurs.append(t.stateDest)
        return successeurs

    """ Définition d'une fonction déterminant si un mot est accepté par un automate.
    Exemple :
            a=Automate.creationAutomate("monAutomate.txt")
            if Automate.accepte(a,"abc"):
                print "L'automate accepte le mot abc"
            else:
                print "L'automate n'accepte pas le mot abc"
    """

    @staticmethod
    def accepte(auto, mot):
        """Automate x str -> bool
        rend True si auto accepte mot, False sinon
        """
        list_states = auto.getListInitialStates()
        for ch in mot:
            list_states = auto.succ(list_states, ch)
        list_fin = auto.getListFinalStates()
        for state in list_states:
            if state in list_fin:
                return True
        return False

    @staticmethod
    def estComplet(auto, alphabet):
        """Automate x str -> bool
        rend True si auto est complet pour alphabet, False sinon
        """
        for state in auto.listStates:
            list_t = auto.getListTransitionsFrom(state)
            list_etiquette = []
            for t in list_t:
                if t.etiquette not in list_etiquette:
                    list_etiquette.append(t.etiquette)
            for ch in alphabet:
                if ch not in list_etiquette:
                    return False
       
        return True

    @staticmethod
    def estDeterministe(auto):
        """Automate  -> bool
        rend True si auto est déterministe, False sinon
        """
        list_int = auto.getListInitialStates()
        if len(list_int) > 1:
            return False
        for state in auto.listStates:
            list_t = auto.getListTransitionsFrom(state)
            list_etiquette = []
            for t in list_t:
                if t.etiquette in list_etiquette:
                    return False
                list_etiquette.append(t.etiquette)
        return True

    @staticmethod
    def completeAutomate(auto, alphabet):
        """Automate x str -> Automate
        rend l'automate complété d'auto, par rapport à alphabet
        """
        if Automate.estComplet(auto, alphabet):
            return auto
        auto_new = copy.deepcopy(auto)
        pur = State(-1, False, False)
        auto_new.addState(pur)
        for state in auto_new.listStates:
            list_t = auto_new.getListTransitionsFrom(state)
            list_etiquette = list(set(t.etiquette for t in list_t))
            for ch in alphabet:
                if ch not in list_etiquette:
                    auto_new.addTransition(Transition(state, ch, pur))
        return auto_new

    @staticmethod
    def determinisation(auto):
        """Automate  -> Automate
        rend l'automate déterminisé d'auto
        """
        list_init = auto.getListInitialStates()
        list_etiquette = auto.getAlphabetFromTransitions()
        list_states_DFA_from_NFA = [list_init]
        list_states_DFA = [State(0, True, False, label=str(list_init))]
        for state in list_init:
            if state in auto.getListFinalStates():
                list_states_DFA = [State(0, True, True, label=str(list_init))]
                break
        list_states = list_init
        list_transitions = []
        i = 0
        list_next = []
        while True:
            for ch in list_etiquette:
                list_temp = auto.succ(list_states, ch)
                if list_temp not in list_states_DFA_from_NFA:
                    add = False
                    for state in list_temp:
                        if state.fin:
                            i += 1
                            list_states_DFA.append(
                                State(i, False, True, label=str(list_temp))
                            )
                            add = True
                            break
                    if not add:
                        i += 1
                        list_states_DFA.append(
                            State(i, False, False, label=str(list_temp))
                        )
                    list_transitions.append(
                        Transition(
                            list_states_DFA[
                                list_states_DFA_from_NFA.index(list_states)
                            ],
                            ch,
                            list_states_DFA[i],
                        )
                    )
                    list_states_DFA_from_NFA.append(list_temp)
                    list_next.append(list_temp)
                else:
                    list_transitions.append(
                        Transition(
                            list_states_DFA[
                                list_states_DFA_from_NFA.index(list_states)
                            ],
                            ch,
                            list_states_DFA[list_states_DFA_from_NFA.index(list_temp)],
                        )
                    )
            if list_next == []:
                break
            list_states = list_next[0]
            del list_next[0]
        new_auto = Automate(list_transitions)
        return new_auto

    @staticmethod
    def complementaire(auto, alphabet):
        """Automate -> Automate
        rend  l'automate acceptant pour langage le complémentaire du langage de a
        """
        auto_complementaire = copy.deepcopy(auto)
        if not auto_complementaire.estDeterministe(auto_complementaire):
            auto_complementaire = Automate.determinisation(auto_complementaire)
        if not auto_complementaire.estComplet(auto_complementaire, alphabet):
            auto_complementaire = Automate.completeAutomate(
                auto_complementaire, alphabet
            )
        for state in auto_complementaire.listStates:
            state.fin = not state.fin
        return auto_complementaire

    @staticmethod
    def intersection(auto0, auto1):
        """Automate x Automate -> Automate
        rend l'automate acceptant pour langage l'intersection des langages des deux automates
        """
        list_etiquette = list(
            set(auto0.getAlphabetFromTransitions())
            & set(auto1.getAlphabetFromTransitions())
        )
        list_states_tuple = list(product(auto0.listStates, auto1.listStates))
        list_states = []
        id = 0
        list_iter_states = []
        dico = {}
        for state0, state1 in list_states_tuple:
            init = state0.init and state1.init
            fin = state0.fin and state1.fin
            state_tmp = State(
                id, init, fin, label="(" + str(state0.id) + "," + str(state1.id) + ")"
            )
            list_states.append(state_tmp)
            dico[state_tmp] = (state0, state1)
            if init:
                list_iter_states.append(state_tmp)
            id += 1
        list_transitions = []
        list_used = []
        while not list_iter_states == []:
            state_current = list_iter_states[0]
            list_used.append(state_current)
            state0, state1 = dico[state_current]
            for etiquette in list_etiquette:
                list0 = auto0.succElem(state0, etiquette)
                list1 = auto1.succElem(state1, etiquette)
                if list0 == [] or list1 == []:
                    continue
                for state0p in list0:
                    for state1p in list1:
                        if (
                            list_states[list_states_tuple.index((state0p, state1p))]
                            not in list_used
                        ):
                            list_iter_states.append(
                                list_states[list_states_tuple.index((state0p, state1p))]
                            )
                        list_transitions.append(
                            Transition(
                                list_states[list_states_tuple.index((state0, state1))],
                                etiquette,
                                list_states[
                                    list_states_tuple.index((state0p, state1p))
                                ],
                            )
                        )
            del list_iter_states[0]
        auto_intersection = Automate(list_transitions)
        return auto_intersection

    @staticmethod
    def union(auto0, auto1):
        """Automate x Automate -> Automate
        rend l'automate acceptant pour langage l'union des langages des deux automates
        """
        alphabet = list(
            set(auto0.getAlphabetFromTransitions())
            & set(auto1.getAlphabetFromTransitions())
        )
        if not auto0.estComplet(auto0, alphabet):
            auto0 = Automate.completeAutomate(auto0, alphabet)
        if not auto1.estComplet(auto1, alphabet):
            auto1 = Automate.completeAutomate(auto1, alphabet)
        list_states_tuple = list(product(auto0.listStates, auto1.listStates))
        list_states = []
        id = 0
        dico = {}
        list_iter_states = []
        for state0, state1 in list_states_tuple:
            init = state0.init and state1.init
            fin = state0.fin or state1.fin
            state_tmp = State(
                id, init, fin, label="(" + str(state0.id) + "," + str(state1.id) + ")"
            )
            list_states.append(state_tmp)
            dico[state_tmp] = (state0, state1)
            if init:
                list_iter_states.append(state_tmp)
            id += 1
        list_transitions = []
        id = 0
        list_itered = []
        while not list_iter_states == []:
            state_current = list_iter_states[0]
            list_itered.append(state_current)
            state0, state1 = dico[state_current]
            for etiquette in alphabet:
                list0 = auto0.succElem(state0, etiquette)
                list1 = auto1.succElem(state1, etiquette)
                if list0 == [] or list1 == []:
                    continue
                for state0p in list0:
                    for state1p in list1:
                        if (
                            list_states[list_states_tuple.index((state0p, state1p))]
                            not in list_itered
                        ):
                            list_iter_states.append(
                                list_states[list_states_tuple.index((state0p, state1p))]
                            )
                        list_transitions.append(
                            Transition(
                                list_states[list_states_tuple.index((state0, state1))],
                                etiquette,
                                list_states[
                                    list_states_tuple.index((state0p, state1p))
                                ],
                            )
                        )
            del list_iter_states[0]
        auto_union = Automate(list_transitions)
        return auto_union

    @staticmethod
    def concatenation(auto1, auto2):
        """Automate x Automate -> Automate
        rend l'automate acceptant pour langage la concaténation des langages des deux automates
        """
        auto_con = copy.deepcopy(auto1)
        auto1_copy = copy.deepcopy(auto1)
        auto2_copy = copy.deepcopy(auto2)
        auto2_list_init = auto2_copy.getListInitialStates()
        idmax = -1
        for state in auto1_copy.listStates:
            if state.id > idmax:
                idmax = state.id
        for state in auto2_copy.listStates:
            idmax += 1
            state.id = idmax
        if not State.isFinalIn(auto1_copy.getListInitialStates()):
            for state in auto2_copy.getListInitialStates():
                state.init = False
        auto1_list_final = auto1_copy.getListFinalStates()
        for state in auto_con.getListFinalStates():
            state.fin = False
        for trans in auto1_copy.listTransitions:
            if trans.stateDest in auto1_list_final:
                for state in auto2_list_init:
                    auto_con.addTransition(
                        Transition(trans.stateSrc, trans.etiquette, state)
                    )
        for trans in auto2_copy.listTransitions:
            auto_con.addTransition(trans)
        return auto_con

    @staticmethod
    def etoile(auto):
        """Automate  -> Automate
        rend l'automate acceptant pour langage l'étoile du langage de a
        """
        auto_etoile = copy.deepcopy(auto)
        list_final = auto_etoile.getListFinalStates()
        list_init = auto_etoile.getListInitialStates()
        auto_etoile.addState(State(-1, True, True, label="ε"))
        for trans in auto_etoile.listTransitions:
            if trans.stateDest in list_final:
                for state in list_init:
                    auto_etoile.addTransition(
                        Transition(trans.stateSrc, trans.etiquette, state)
                    )
        return auto_etoile
