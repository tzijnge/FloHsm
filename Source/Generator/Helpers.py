from Descriptors import State, StateType, Guard, SimpleGuard, EntryExit, \
                                    InternalTransition, StateTransition, InitialTransition, \
                                    ChoiceTransition, Action
import unittest
from typing import Optional, Any, List

class FloHsmTester(unittest.TestCase):

    def assertState(self, s:State, name:str, parent:str=None, 
                    num_int_transitions:int=0, num_state_transitions:int=0,
                    num_choice_transitions:int=0,
                    entry_guard:str=None, entry_action:Action=None,
                    exit_guard:str=None, exit_action:Action=None, is_composite:bool=False,
                    state_type:StateType=StateType.NORMAL) -> None:

        self.assertEqual(name, s.name)
        self.assertEqual(parent, s.parent)
        self.assertEqual(num_int_transitions, len(s.internal_transitions))
        self.assertEqual(num_state_transitions, len(s.state_transitions))
        self.assertEqual(num_choice_transitions, len(s.choice_transitions))
        self.assertEqual(state_type, s.state_type)
        
        if entry_action is None:
            self.assertIsNone(s.entry)
            self.assertIsNone(entry_guard, 'entry guard is only allowed when entry has an action')
        else:
            assert s.entry is not None
            self.assertEqual(entry_action.name, s.entry.action.name)
            self.assertEqual(entry_action.type, s.entry.action.type)
            self.assertEqual(entry_action.value(), s.entry.action.value())
            if entry_guard is None:
                self.assertIsNone(s.entry.guard)
            else:
                assert s.entry.guard is not None
                self.assertEqual(entry_guard, s.entry.guard.to_string())

        if exit_action is None:
            self.assertIsNone(s.exit)
            self.assertIsNone(exit_guard, 'exit guard is only allowed when exit has an action')
        else:
            assert s.exit is not None
            self.assertEqual(exit_action.name, s.exit.action.name)
            if exit_guard is None:
                self.assertIsNone(s.exit.guard)
            else:
                assert s.exit.guard is not None
                self.assertEqual(exit_guard, s.exit.guard.to_string())

        self.assertEqual(is_composite, s.is_composite)

    def assertInternalTransition(self, t:InternalTransition, event:str=None, guard:Guard=None, action:Action=None) -> None:
        self.assertEqual(event, t.event)
        if action:
            self.assertEqual(action.name, t.action.name)

        if guard is None:
            self.assertIsNone(t.guard)
        else:
            assert t.guard is not None
            self.assertIsNotNone(t.guard)
            self.assertEqual(guard.to_string(), t.guard.to_string())

    def assertStateTransition(self, t:StateTransition, to:str=None, 
                              event:str=None, guard:str=None, 
                              action:Action=None) -> None:
        self.assertEqual(to, t.toState)
        self.assertEqual(event, t.event)
        if action:
            assert t.action
            self.assertEqual(action.name, t.action.name)
            self.assertEqual(action.type, t.action.type)
            self.assertEqual(action.value(), t.action.value())

        if guard is None:
            self.assertIsNone(t.guard)
        else:
            assert t.guard is not None
            self.assertIsNotNone(t.guard)
            self.assertEqual(guard, t.guard.to_string())

    def assertChoiceTransition(self, t:ChoiceTransition, to:str, guard:str, action:Action=None) -> None:
        self.assertEqual(to, t.toState)
        self.assertEqual(guard, t.guard.to_string())

        if action:
            assert t.action
            self.assertEqual(action.name, t.action.name)
            self.assertEqual(action.type, t.action.type)
            self.assertEqual(action.value(), t.action.value())

    def assertInitialTransition(self, t:Optional[InitialTransition], to:str, action:Action=None) -> None:
        self.assertIsNotNone(t)
        assert t is not None

        self.assertEqual(to, t.toState)

        if action:
            assert t.action
            self.assertEqual(action.name, t.action.name)
            self.assertEqual(action.type, t.action.type)
            self.assertEqual(action.value(), t.action.value())

    def assertSimpleGuard(self, g:Optional[Guard], guard_expression:str) -> None:
        self.assertGuard(g, guard_expression, [guard_expression])

    def assertGuard(self, g:Optional[Guard], guard_expression:str, guards:List[str]) -> None:
        self.assertIsNotNone(g)
        assert g is not None

        self.assertEqual(guard_expression, g.to_string())
        self.assertEqual(len(guards), len(g.guard_conditions()))
        for guard in guards:
            self.assertIn(guard, g.guard_conditions())

class TestState(State):
    def __init__(self, name:str, lineno:int=0, parent:Optional[str]=None,
                initial_transition:InitialTransition=None, 
                internal_transitions:List[InternalTransition]=None,
                state_transitions:List[StateTransition]=None,
                choice_transitions:List[ChoiceTransition]=None,
                entry:EntryExit=None, exit:EntryExit=None, 
                is_composite:bool=False, state_type:StateType=StateType.NORMAL):
        super().__init__(name=name, lineno=lineno, parent=parent,
                                initial_transition=initial_transition,
                                internal_transitions=internal_transitions,
                                state_transitions=state_transitions,
                                choice_transitions=choice_transitions,
                                entry=entry, exit=exit, is_composite=is_composite,
                                state_type=state_type)

class TestGuard(SimpleGuard):
    def __init__(self, guard:str):
        super().__init__(guard=guard, lineno=0)

class InitialState(State):
    def __init__(self, name:str, initial_action:Action=None):
        super().__init__(name='FloHsmInitial_5OdpEA31BEcPrWrNx8u7',
                                initial_transition=InitialTransition(toState=name, action=initial_action),
                                lineno=0)
