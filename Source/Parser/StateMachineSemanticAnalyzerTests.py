import unittest
from StateMachineSemanticAnalyzer import SemanticAnalyzer
from StateMachineDescriptors import State, StateType, InternalTransition, StateTransition, InitialTransition, ChoiceTransition
from StateMachineDescriptors import SimpleGuard, OrGuard, AndGuard, NotGuard, EntryExit
from typing import List, Optional
import Helpers

class Test_StateMachineSemanticAnalyzerTests(Helpers.FloHsmTester):
    def setUp(self) -> None:
        self.analyzer= SemanticAnalyzer()

    def assertContainsErrorMessages(self, error_messages:List[str]) -> None:
        for error_message in error_messages:
            self.assertIn(error_message, self.analyzer.errors)

    def assertContainsErrorMessage(self, error_message:str) -> None:
        self.assertIn(error_message, self.analyzer.errors)

    def assertContainsWarningMessages(self, warning_messages:List[str]) -> None:
        for error_message in warning_messages:
            self.assertIn(error_message, self.analyzer.warnings)

    def assertContainsWarningMessage(self, warning_message:str) -> None:
        self.assertIn(warning_message, self.analyzer.warnings)

    # TODO: Don't use assertDoesNotContainErrorMessage  
    def assertDoesNotContainErrorMessage(self, error_message:str) -> None:
        self.assertNotIn(error_message, self.analyzer.errors)

    def test_merge_two_simple_states(self) -> None:
        s1 = Helpers.TestState(name='S', lineno=111)
        s2 = Helpers.TestState(name='S', lineno=222)
        self.analyzer.analyze([s1, s2])

        self.assertDoesNotContainErrorMessage('Failed to merge state definitions from line 111 and line 222')
        self.assertEqual(0, len(self.analyzer.warnings))
        self.assertEqual(1, len(self.analyzer.states))
        self.assertState(self.analyzer.states[0], name='S')

    def test_merge_two_simple_states_with_third_state(self) -> None:
        s1 = Helpers.TestState(name='S1', lineno=111)
        s2 = Helpers.TestState(name='S2', lineno=222)
        s3 = Helpers.TestState(name='S1', lineno=333)
        self.analyzer.analyze([s1, s2, s3])

        self.assertDoesNotContainErrorMessage('Failed to merge state definitions from line(s) [111] and line(s) [333]')
        self.assertEqual(0, len(self.analyzer.warnings))
        self.assertEqual(2, len(self.analyzer.states))
        self.assertState(self.analyzer.states[0], name='S1')
        self.assertState(self.analyzer.states[1], name='S2')

    def test_states_with_same_name_cannot_have_different_parents(self) -> None:
        s1 = Helpers.TestState(name='S', parent='P1', lineno=7880)
        s2 = Helpers.TestState(name='S', parent='P2', lineno=6312)
        p1 = Helpers.TestState(name = 'P1')
        p2 = Helpers.TestState(name = 'P2')
        self.analyzer.analyze([s1, s2, p1, p2])

        self.assertContainsErrorMessage('Unable to merge different parents P1 and P2 for state S. Possibly involved line(s): [7880, 6312]')
        self.assertEqual(0, len(self.analyzer.warnings))
        self.assertEqual(3, len(self.analyzer.states))
        self.assertState(self.analyzer.states[0], name='P1')
        self.assertState(self.analyzer.states[1], name='P2')
        self.assertState(self.analyzer.states[2], name='S', parent='P1')

    def test_inheritance_from_self(self) -> None:
        s1 = Helpers.TestState(name='S1', parent='S1', lineno=77)
        self.analyzer.analyze([s1])

        self.assertContainsErrorMessage('Detected circular inheritance for state S1 on line(s) [77]')
        self.assertEqual(0, len(self.analyzer.warnings))
        self.assertEqual(1, len(self.analyzer.states))
        self.assertState(self.analyzer.states[0], name='S1', parent='S1')

    def test_direct_circular_inheritance(self) -> None:
        i = Helpers.InitialState('S1')
        s1 = Helpers.TestState(name='S1', parent='S2', lineno=6618)
        s2 = Helpers.TestState(name='S2', parent='S1', lineno=154)
        self.analyzer.analyze([i, s1, s2])

        self.assertContainsErrorMessages(['Failed to sort states hierarchically. Continue with unsorted states.',
                                          'Detected circular inheritance for state S1 on line(s) [154]', 
                                          'Detected circular inheritance for state S2 on line(s) [6618]'])
        self.assertEqual(0, len(self.analyzer.warnings))
        self.assertEqual(3, len(self.analyzer.states))

        self.assertState(self.analyzer.states[0], name='FloHsmInitial_5OdpEA31BEcPrWrNx8u7')
        self.assertState(self.analyzer.states[1], name='S1', parent='S2')
        self.assertState(self.analyzer.states[2], name='S2', parent='S1')

    def test_indirect_circular_inheritance(self) -> None:
        i = Helpers.InitialState('S1')
        s1 = Helpers.TestState(name='S1', parent='S2', lineno=973)
        s2 = Helpers.TestState(name='S2', parent='S3', lineno=3652)
        s3 = Helpers.TestState(name='S3', parent='S1', lineno=570)
        self.analyzer.analyze([i, s1, s2, s3])

        self.assertContainsErrorMessages(['Failed to sort states hierarchically. Continue with unsorted states.',
                                          'Detected circular inheritance for state S1 on line(s) [570]', 
                                          'Detected circular inheritance for state S2 on line(s) [973]',
                                          'Detected circular inheritance for state S3 on line(s) [3652]'])
        self.assertEqual(0, len(self.analyzer.warnings))
        self.assertEqual(4, len(self.analyzer.states))
        self.assertState(self.analyzer.states[0], name='FloHsmInitial_5OdpEA31BEcPrWrNx8u7')
        self.assertState(self.analyzer.states[1], name='S1', parent='S2')
        self.assertState(self.analyzer.states[2], name='S2', parent='S3')
        self.assertState(self.analyzer.states[3], name='S3', parent='S1')

    def test_parent_must_exist(self) -> None:
        s1 = Helpers.TestState(name='S', parent='P1', lineno=9294)
        self.analyzer.analyze([s1])

        self.assertContainsErrorMessage('Detected unknown state \'P1\' at line(s) [9294]')
        self.assertEqual(0, len(self.analyzer.warnings))
        self.assertEqual(1, len(self.analyzer.states))
        self.assertState(self.analyzer.states[0], name='S', parent='P1')

    def test_state_name_cannot_equal_event_name(self) -> None:
        s = Helpers.TestState(name='S', internal_transitions=[ InternalTransition(event='S', action='A') ])
        self.analyzer.analyze([s])

        self.assertContainsErrorMessage('State name \'S\' is also used as event name')
        self.assertEqual(0, len(self.analyzer.warnings))
        self.assertEqual(1, len(self.analyzer.states))
        self.assertState(self.analyzer.states[0], name='S', num_int_transitions=1)

    def test_state_name_cannot_equal_guard_name(self) -> None:
        s = Helpers.TestState(name='S', internal_transitions=[ InternalTransition(event='E', action='A', guard=Helpers.TestGuard('S')) ])
        self.analyzer.analyze([s])

        self.assertContainsErrorMessage('State name \'S\' is also used as guard name')
        self.assertEqual(0, len(self.analyzer.warnings))
        self.assertEqual(1, len(self.analyzer.states))
        self.assertState(self.analyzer.states[0], name='S', num_int_transitions=1)

    def test_state_name_cannot_equal_action_name(self) -> None:
        s = Helpers.TestState(name='S', internal_transitions=[ InternalTransition(event='E', action='S') ])
        self.analyzer.analyze([s])

        self.assertContainsErrorMessage('State name \'S\' is also used as action name')
        self.assertEqual(0, len(self.analyzer.warnings))
        self.assertEqual(1, len(self.analyzer.states))
        self.assertState(self.analyzer.states[0], name='S', num_int_transitions=1)

    def test_event_name_cannot_equal_guard_name(self) -> None:
        s = Helpers.TestState(name='S', internal_transitions=[ InternalTransition(event='EE', action='A', guard=Helpers.TestGuard('EE')) ])
        self.analyzer.analyze([s])

        self.assertContainsErrorMessage('Event name \'EE\' is also used as guard name')
        self.assertEqual(0, len(self.analyzer.warnings))
        self.assertEqual(1, len(self.analyzer.states))
        self.assertState(self.analyzer.states[0], name='S', num_int_transitions=1)

    def test_event_name_cannot_equal_action_name(self) -> None:
        s = Helpers.TestState(name='S', internal_transitions=[ InternalTransition(event='EE', action='EE') ])
        self.analyzer.analyze([s])

        self.assertContainsErrorMessage('Event name \'EE\' is also used as action name')
        self.assertEqual(0, len(self.analyzer.warnings))
        self.assertEqual(1, len(self.analyzer.states))
        self.assertState(self.analyzer.states[0], name='S', num_int_transitions=1)

    def test_guard_name_cannot_equal_action_name(self) -> None:
        s = Helpers.TestState(name='S', internal_transitions=[ InternalTransition(event='E', guard=Helpers.TestGuard('G1'), action='G1') ])
        self.analyzer.analyze([s])

        self.assertContainsErrorMessage('Guard name \'G1\' is also used as action name')
        self.assertEqual(0, len(self.analyzer.warnings))
        self.assertEqual(1, len(self.analyzer.states))
        self.assertState(self.analyzer.states[0], name='S', num_int_transitions=1)

    def test_no_top_level_initial_transition(self) -> None:
        s = Helpers.TestState(name='S')
        self.analyzer.analyze([s])

        self.assertContainsErrorMessage('No top-level initial transition found')

    def test_state_is_not_reachable(self) -> None:
        initial = Helpers.InitialState('xxx')
        s = Helpers.TestState(name='S')
        self.analyzer.analyze([initial, s])
    
        self.assertContainsErrorMessage('State \'S\' (line(s) [0]) is not reachable')

    def test_state_is_reachable(self) -> None:
        initial = Helpers.InitialState('S')
        s = Helpers.TestState(name='S')
        self.analyzer.analyze([initial, s])

        self.assertDoesNotContainErrorMessage('State \'S\' (line(s) [0]) is not reachable')

    def test_state_is_reachable_through_initial_transition(self) -> None:
        initial = Helpers.InitialState('S1')
        s1 = Helpers.TestState(name='S1', initial_transition=InitialTransition(toState='S2'))
        s2 = Helpers.TestState(name='S2')
        self.analyzer.analyze([initial, s1, s2])

        self.assertDoesNotContainErrorMessage('State \'S2\' (line(s) [0]) is not reachable')

    def test_parent_state_is_reachable_when_child_state_is_reachable(self) -> None:
        initial = Helpers.InitialState('S')
        p1 = Helpers.TestState(name='P1')
        p2 = Helpers.TestState(name='P2', parent='P1')
        p3 = Helpers.TestState(name='P3', parent='P2')
        s = Helpers.TestState(name='S', parent='P3')
        self.analyzer.analyze([initial, s, p1, p2, p3])

        self.assertDoesNotContainErrorMessage('State \'P\' (line(s) [0]) is not reachable')

    def test_parent_state_is_reachable_when_child_state_is_reachable2(self) -> None:
        initial = Helpers.InitialState('S')
        p1 = Helpers.TestState(name='P1')
        p2 = Helpers.TestState(name='P2', parent='P1')
        p3 = Helpers.TestState(name='P3', parent='P1', state_transitions=[StateTransition(toState='P2', event='E0')])
        s = Helpers.TestState(name='S', parent='P3')
        self.analyzer.analyze([initial, s, p1, p2, p3])

        self.assertDoesNotContainErrorMessage('State \'P2\' (line(s) [0]) is not reachable')

    def test_states_have_incoming_transitions_but_are_not_reachable(self) -> None:
        initial = Helpers.InitialState('xxx')
        s1= Helpers.TestState(name='S1', state_transitions=[StateTransition(event='E', toState='S2')])
        s2= Helpers.TestState(name='S2', state_transitions=[StateTransition(event='E', toState='S1')])
        self.analyzer.analyze([initial, s1, s2])

        self.assertContainsErrorMessage('State \'S1\' (line(s) [0]) is not reachable')
        self.assertContainsErrorMessage('State \'S2\' (line(s) [0]) is not reachable')

    def test_infinite_transition_loop(self) -> None:
        initial = Helpers.InitialState('S1')
        s1= Helpers.TestState(name='S1', state_transitions=[StateTransition(event='E', toState='S2')])
        s2= Helpers.TestState(name='S2', state_transitions=[StateTransition(event='E', toState='S1')])
        self.analyzer.analyze([initial, s1, s2])

        self.assertEqual(0, len(self.analyzer.errors))

    def test_states_are_sorted_hierarchically(self) -> None:
        s1 = Helpers.TestState(name='S1')
        s2 = Helpers.TestState(name='S2')
        s3 = Helpers.TestState(name='S3', parent='S1')
        s4 = Helpers.TestState(name='S4', parent='S2')
        s5 = Helpers.TestState(name='S5', parent='S2')
        s6 = Helpers.TestState(name='S6', parent='S5')
        s7 = Helpers.TestState(name='S7', parent='S5')
        s8 = Helpers.TestState(name='S8', parent='S6')
        s9 = Helpers.TestState(name='S9', parent='S2')
        s10 = Helpers.TestState(name='S10', parent='S1')

        self.analyzer.analyze([s3, s5, s1, s6, s9, s2, s8, s10, s4, s7, s3, s5])
        self.assertEqual(10, len(self.analyzer.states))
        self.assertEqual(10, len(self.analyzer.state_names))
        # top level
        self.assertState(self.analyzer.states[0], 'S1', parent = None)
        self.assertEqual(self.analyzer.state_names[0], 'S1')
        self.assertState(self.analyzer.states[1], 'S2', parent=None)
        self.assertEqual(self.analyzer.state_names[1], 'S2')
        # level 1
        self.assertState(self.analyzer.states[2], 'S3', parent='S1')
        self.assertEqual(self.analyzer.state_names[2], 'S3')
        self.assertState(self.analyzer.states[3], 'S5', parent='S2')
        self.assertEqual(self.analyzer.state_names[3], 'S5')
        self.assertState(self.analyzer.states[4], 'S9', parent='S2')
        self.assertEqual(self.analyzer.state_names[4], 'S9')
        self.assertState(self.analyzer.states[5], 'S10', parent='S1')
        self.assertEqual(self.analyzer.state_names[5], 'S10')
        self.assertState(self.analyzer.states[6], 'S4', parent='S2')
        self.assertEqual(self.analyzer.state_names[6], 'S4')
        # level 2
        self.assertState(self.analyzer.states[7], 'S6', parent='S5')
        self.assertEqual(self.analyzer.state_names[7], 'S6')
        self.assertState(self.analyzer.states[8], 'S7', parent='S5')
        self.assertEqual(self.analyzer.state_names[8], 'S7')
        # level 3
        self.assertState(self.analyzer.states[9], 'S8', parent='S6')
        self.assertEqual(self.analyzer.state_names[9], 'S8')

    def test_state_transition_to_self(self) -> None:
        i = Helpers.InitialState('S1')
        s1 = Helpers.TestState(name='S1', state_transitions=[StateTransition(toState='S1', event='E1', action='A1')])

        self.analyzer.analyze([i, s1])
        self.assertEqual(2, len(self.analyzer.states))
        self.assertEqual(0, len(self.analyzer.errors))

    def test_state_transition_to_parent(self) -> None:
        i = Helpers.InitialState('S1')
        p1 = Helpers.TestState(name='P1')
        s1 = Helpers.TestState(name='S1', parent='P1', state_transitions=[StateTransition(toState='P1', event='E1', action='A1')])


        self.analyzer.analyze([i, p1, s1])
        self.assertEqual(3, len(self.analyzer.states))
        self.assertEqual(0, len(self.analyzer.errors))

    def test_state_transition_to_child(self) -> None:
        i = Helpers.InitialState('P1')
        p1 = Helpers.TestState(name='P1', state_transitions=[StateTransition(toState='S1', event='E1', action='A1')])
        s1 = Helpers.TestState(name='S1', parent='P1')


        self.analyzer.analyze([i, p1, s1])
        self.assertEqual(3, len(self.analyzer.states))
        self.assertEqual(0, len(self.analyzer.errors))

    def test_extract_all_actions(self) -> None:
        i = Helpers.InitialState('P1', 'A0')
        s1 = Helpers.TestState(name='S1',
                       entry=EntryExit(action='A1'),
                       exit=EntryExit(action='A2'),
                       state_transitions=[StateTransition(toState='S1', event='E1', action='A3')],
                       internal_transitions=[InternalTransition(event='E2', action='A4')])

        choice1 = Helpers.TestState(name='S2', state_type=StateType.CHOICE, choice_transitions=[ChoiceTransition('S3', guard=Helpers.TestGuard('G1'), action='A5')])

        self.analyzer.analyze([i, s1, choice1])
        self.assertEqual(6, len(self.analyzer.action_names))
        self.assertIn('A0', self.analyzer.action_names)
        self.assertIn('A1', self.analyzer.action_names)
        self.assertIn('A2', self.analyzer.action_names)
        self.assertIn('A3', self.analyzer.action_names)
        self.assertIn('A4', self.analyzer.action_names)
        self.assertIn('A5', self.analyzer.action_names)

    def test_extract_all_guards(self) -> None:
        i = Helpers.InitialState('P1', 'A0')
        s1 = Helpers.TestState(name='S1',
                       entry=EntryExit(action='A1', guard=AndGuard(Helpers.TestGuard('G1'), Helpers.TestGuard('G2'))),
                       exit=EntryExit(action='A2', guard=AndGuard(Helpers.TestGuard('G3'), Helpers.TestGuard('G4'))),
                       state_transitions=[StateTransition(toState='S1', event='E1', action='A3', guard=AndGuard(Helpers.TestGuard('G5'), Helpers.TestGuard('G6')))],
                       internal_transitions=[InternalTransition(event='E2', action='A4', guard=AndGuard(Helpers.TestGuard('G7'), Helpers.TestGuard('G8')))])

        choice1 = Helpers.TestState(name='S2', state_type=StateType.CHOICE, choice_transitions=[ChoiceTransition('S3', guard=AndGuard(Helpers.TestGuard('G9'), Helpers.TestGuard('G10')))])

        self.analyzer.analyze([i, s1, choice1])
        self.assertEqual(10, len(self.analyzer.guard_names))
        self.assertIn('G1', self.analyzer.guard_names)
        self.assertIn('G2', self.analyzer.guard_names)
        self.assertIn('G3', self.analyzer.guard_names)
        self.assertIn('G4', self.analyzer.guard_names)
        self.assertIn('G5', self.analyzer.guard_names)
        self.assertIn('G6', self.analyzer.guard_names)
        self.assertIn('G7', self.analyzer.guard_names)
        self.assertIn('G8', self.analyzer.guard_names)
        self.assertIn('G9', self.analyzer.guard_names)
        self.assertIn('G10', self.analyzer.guard_names)

    def test_extract_all_events(self) -> None:
        s1 = Helpers.TestState(name='S1', internal_transitions=[InternalTransition('E1', 'A1'), InternalTransition('E2', 'A2') ])
        s2 = Helpers.TestState(name='S2', state_transitions=[StateTransition('E3', 'S1'), StateTransition('E4', 'S2') ])

        self.analyzer.analyze([s1, s2])
        self.assertEqual(4, len(self.analyzer.event_names))
        self.assertIn('E1', self.analyzer.event_names)
        self.assertIn('E2', self.analyzer.event_names)
        self.assertIn('E3', self.analyzer.event_names)
        self.assertIn('E4', self.analyzer.event_names)

    def test_guard_expression_is_always_true(self) -> None:
        g1 = OrGuard(Helpers.TestGuard('G1'), NotGuard(Helpers.TestGuard('G1')))
        g2 = OrGuard(Helpers.TestGuard('G2'), NotGuard(Helpers.TestGuard('G2')))
        g3 = OrGuard(Helpers.TestGuard('G3'), NotGuard(Helpers.TestGuard('G3')))
        g4 = OrGuard(Helpers.TestGuard('G4'), NotGuard(Helpers.TestGuard('G4')))

        initial = Helpers.InitialState('S1')
        s1 = Helpers.TestState(name='S1',
                       entry=EntryExit(action='A1', guard=g1),
                       exit=EntryExit(action='A2', guard=g2),
                       state_transitions=[StateTransition(toState='S1', event='E1', action='A3', guard=g3)],
                       internal_transitions=[InternalTransition(event='E2', action='A4', guard=g4)])

        self.analyzer.analyze([initial, s1])
        self.assertEqual(4, len(self.analyzer.warnings))
        self.assertEqual(0, len(self.analyzer.errors))
        self.assertContainsWarningMessages(['Guard expression (G1 || !G1) (State S1, line 0) always evaluates to true',
                                            'Guard expression (G2 || !G2) (State S1, line 0) always evaluates to true',
                                            'Guard expression (G3 || !G3) (State S1, line 0) always evaluates to true',
                                            'Guard expression (G4 || !G4) (State S1, line 0) always evaluates to true'])


    def test_guard_expression_is_always_false(self) -> None:
        g1 = AndGuard(Helpers.TestGuard('G1'), NotGuard(Helpers.TestGuard('G1')))
        g2 = AndGuard(Helpers.TestGuard('G2'), NotGuard(Helpers.TestGuard('G2')))
        g3 = AndGuard(Helpers.TestGuard('G3'), NotGuard(Helpers.TestGuard('G3')))
        g4 = AndGuard(Helpers.TestGuard('G4'), NotGuard(Helpers.TestGuard('G4')))

        initial = Helpers.InitialState('S1')
        s1 = Helpers.TestState(name='S1',
                       entry=EntryExit(action='A1', guard=g1),
                       exit=EntryExit(action='A2', guard=g2),
                       state_transitions=[StateTransition(toState='S1', event='E1', action='A3', guard=g3)],
                       internal_transitions=[InternalTransition(event='E2', action='A4', guard=g4)])

        self.analyzer.analyze([initial, s1])
        self.assertEqual(4, len(self.analyzer.warnings))
        self.assertEqual(0, len(self.analyzer.errors))
        self.assertContainsWarningMessages(['Guard expression (G1 && !G1) (State S1, line 0) always evaluates to false',
                                            'Guard expression (G2 && !G2) (State S1, line 0) always evaluates to false',
                                            'Guard expression (G3 && !G3) (State S1, line 0) always evaluates to false',
                                            'Guard expression (G4 && !G4) (State S1, line 0) always evaluates to false'])

    def test_unable_to_choose_between_transitions(self) -> None:
        # A
        g1 = Helpers.TestGuard('A')
        # (B || C)
        g2 = OrGuard(Helpers.TestGuard('B'), Helpers.TestGuard('C'))
        # (B && C)
        g3 = AndGuard(Helpers.TestGuard('B'), Helpers.TestGuard('C'))
        # (D && !E)
        g4 = AndGuard(Helpers.TestGuard('D'), NotGuard(Helpers.TestGuard('E')))
        # (!D || (F && ! E))
        g5 = OrGuard(NotGuard(Helpers.TestGuard('D')), AndGuard(Helpers.TestGuard('F'), NotGuard(Helpers.TestGuard('E'))))

        st1 = StateTransition(toState='S1', event='E1', action='A1', guard=g1) # conflicts with st2
        st2 = StateTransition(toState='S2', event='E1', action='A2', guard=g1)
        st3 = StateTransition(toState='S1', event='E2', action='A3', guard=g2) # conflicts with it3
        it1 = InternalTransition(event='E3', action='A4', guard=g4) # conflicts with it2
        it2 = InternalTransition(event='E3', action='A5', guard=g5)
        it3 = InternalTransition(event='E2', action='A6', guard=g3)

        initial = Helpers.InitialState('S1')
        s1 = Helpers.TestState(name='S1',  state_transitions=[st1, st2, st3], internal_transitions=[it1, it2, it3])

        self.analyzer.analyze([initial, s1])

        self.assertEqual(0, len(self.analyzer.warnings))
        self.assertEqual(3, len(self.analyzer.errors))
        self.assertContainsErrorMessages(['Ambiguous transition for event E1 in S1: Guard expressions A and A evaluate to true when A==true. See lines 0 and 0',
                                          'Ambiguous transition for event E2 in S1: Guard expressions (B && C) and (B || C) evaluate to true when B==true and C==true. See lines 0 and 0',
                                          'Ambiguous transition for event E3 in S1: Guard expressions (D && !E) and (!D || (F && !E)) evaluate to true when D==true and E==false and F==true. See lines 0 and 0'])

    def test_three_ambiguous_transitions(self) -> None:
        # A
        g1 = Helpers.TestGuard('A')
        # (A && !B)
        g2 = AndGuard(Helpers.TestGuard('A'), NotGuard(Helpers.TestGuard('B')))
        # (A && !C)
        g3 = AndGuard(Helpers.TestGuard('A'), NotGuard(Helpers.TestGuard('C')))

        st1 = StateTransition(toState='S1', event='E1', action='A1', guard=g1)
        st2 = StateTransition(toState='S2', event='E1', action='A2', guard=g2)
        st3 = StateTransition(toState='S1', event='E1', action='A3', guard=g3)

        initial = Helpers.InitialState('S1')
        s1 = Helpers.TestState(name='S1',  state_transitions=[st1, st2, st3])

        self.analyzer.analyze([initial, s1])

        self.assertEqual(0, len(self.analyzer.warnings))
        self.assertEqual(1, len(self.analyzer.errors))
        self.assertContainsErrorMessage('Ambiguous transition for event E1 in S1: Guard expressions A and (A && !B) and (A && !C) evaluate to true when A==true and B==false and C==false. See lines 0 and 0 and 0')


    def test_two_out_of_three_transitions_are_ambiguous(self) -> None:
        # A
        g1 = Helpers.TestGuard('A')
        # (A || !B)
        g2 = OrGuard(Helpers.TestGuard('A'), NotGuard(Helpers.TestGuard('B')))
        # (A || !C)
        g3 = OrGuard(Helpers.TestGuard('A'), NotGuard(Helpers.TestGuard('C')))

        st1 = StateTransition(toState='S1', event='E1', action='A1', guard=g1)
        st2 = StateTransition(toState='S2', event='E1', action='A2', guard=g2)
        st3 = StateTransition(toState='S1', event='E1', action='A3', guard=g3)

        initial = Helpers.InitialState('S1')
        s1 = Helpers.TestState(name='S1',  state_transitions=[st1, st2, st3])

        self.analyzer.analyze([initial, s1])

        self.assertEqual(0, len(self.analyzer.warnings))
        self.assertEqual(1, len(self.analyzer.errors))
        self.assertContainsErrorMessage('Ambiguous transition for event E1 in S1: Guard expressions (A || !B) and (A || !C) evaluate to true when A==false and B==false and C==false. See lines 0 and 0')

    def test_choice_pseudo_state_cannot_have_entry(self) -> None:
        initial = Helpers.InitialState('S')
        s1 = Helpers.TestState(name='S', lineno=123, state_type=StateType.CHOICE)
        s2 = Helpers.TestState(name='S', lineno=321, entry=EntryExit(action='A', guard=SimpleGuard('G', 0)))

        self.analyzer.analyze([initial, s1, s2])

        self.assertEqual(0, len(self.analyzer.warnings))
        self.assertEqual(2, len(self.analyzer.errors))
        self.assertContainsErrorMessage('A choice pseudo state cannot have an entry. See line(s) 123 and 321')

    def test_choice_pseudo_state_cannot_have_exit(self) -> None:
        initial = Helpers.InitialState('S')
        s1 = Helpers.TestState(name='S', lineno=111, state_type=StateType.CHOICE)
        s2 = Helpers.TestState(name='S', lineno=333, exit=EntryExit(action='A', guard=SimpleGuard('G', 0)))

        self.analyzer.analyze([initial, s1, s2])

        self.assertEqual(0, len(self.analyzer.warnings))
        self.assertEqual(2, len(self.analyzer.errors))
        self.assertContainsErrorMessage('A choice pseudo state cannot have an exit. See line(s) 111 and 333')

    def test_choice_pseudo_state_cannot_have_internal_transitions(self) -> None:
        initial = Helpers.InitialState('S')
        s1 = Helpers.TestState(name='S', lineno=512, state_type=StateType.CHOICE)
        s2 = Helpers.TestState(name='S', lineno=652, internal_transitions=[InternalTransition(event='E1', action='A1')])
        s3 = Helpers.TestState(name='S', lineno=321, internal_transitions=[InternalTransition(event='E2', action='A2')])

        self.analyzer.analyze([initial, s1, s2, s3])

        self.assertEqual(0, len(self.analyzer.warnings))
        self.assertEqual(2, len(self.analyzer.errors))
        self.assertContainsErrorMessage('A choice pseudo state cannot have any internal transitions. See line(s) 512 and 652 and 321')

    def test_choice_pseudo_state_cannot_have_state_transitions(self) -> None:
        initial = Helpers.InitialState('S')
        s1 = Helpers.TestState(name='S', lineno=553, state_type=StateType.CHOICE)
        s2 = Helpers.TestState(name='S', lineno=981, state_transitions=[StateTransition(event='E1', toState='S1')])
        s3 = Helpers.TestState(name='S', lineno=658, state_transitions=[StateTransition(event='E2', toState='S2')])

        self.analyzer.analyze([initial, s1, s2, s3])

        self.assertEqual(0, len(self.analyzer.warnings))
        self.assertEqual(2, len(self.analyzer.errors))
        self.assertContainsErrorMessage('A choice pseudo state cannot have any state transitions. See line(s) 553 and 981 and 658')

    def test_choice_pseudo_state_with_no_choice_transitions(self) -> None:
        initial = Helpers.InitialState('S')
        s1 = Helpers.TestState(name='S', lineno=741, state_type=StateType.CHOICE)

        self.analyzer.analyze([initial, s1])

        self.assertEqual(0, len(self.analyzer.warnings))
        self.assertEqual(1, len(self.analyzer.errors))
        self.assertContainsErrorMessage('A choice pseudo state must have at least two outgoing transitions. See line(s) 741')

    def test_choice_pseudo_state_with_one_choice_transition(self) -> None:
        initial = Helpers.InitialState('S')
        s1 = Helpers.TestState(name='S', lineno=741, state_type=StateType.CHOICE, choice_transitions=[ChoiceTransition(toState='S2', guard=Helpers.TestGuard('G1'))])

        self.analyzer.analyze([initial, s1])

        self.assertEqual(0, len(self.analyzer.warnings))
        self.assertEqual(1, len(self.analyzer.errors))
        self.assertContainsErrorMessage('A choice pseudo state must have at least two outgoing transitions. See line(s) 741')

    def test_choice_pseudo_state_with_conflicting_guards_1(self) -> None:
        initial = Helpers.InitialState('S')
        s1 = Helpers.TestState(name='S', lineno=741, state_type=StateType.CHOICE, choice_transitions=[
            ChoiceTransition(toState='S2', guard=Helpers.TestGuard('G1')), 
            ChoiceTransition(toState='S3', guard=Helpers.TestGuard('G1'))])

        self.analyzer.analyze([initial, s1])

        self.assertEqual(0, len(self.analyzer.warnings))
        self.assertEqual(2, len(self.analyzer.errors))
        self.assertContainsErrorMessage('Ambiguous outgoing transition for choice pseudo state S: Guard expressions G1 and G1 evaluate to true when G1==true. See lines 0 and 0')
        self.assertContainsErrorMessage('No outgoing transition for choice pseudo state S: Guard expressions G1 and G1 evaluate to false when G1==false. See lines 0 and 0')

    def test_choice_pseudo_state_with_conflicting_guards_2(self) -> None:
        initial = Helpers.InitialState('S1')
        s1 = Helpers.TestState(name='S1', lineno=741, state_type=StateType.CHOICE, choice_transitions=[
            ChoiceTransition(toState='S2', guard=AndGuard(SimpleGuard(guard='A', lineno=2155), SimpleGuard(guard='B', lineno=2155))), 
            ChoiceTransition(toState='S3', guard=OrGuard(SimpleGuard(guard='A', lineno=529), SimpleGuard(guard='B', lineno=529)))])

        self.analyzer.analyze([initial, s1])

        self.assertEqual(0, len(self.analyzer.warnings))
        self.assertEqual(2, len(self.analyzer.errors))
        self.assertContainsErrorMessage('Ambiguous outgoing transition for choice pseudo state S1: Guard expressions (A && B) and (A || B) evaluate to true when A==true and B==true. See lines 2155 and 529')
        self.assertContainsErrorMessage('No outgoing transition for choice pseudo state S1: Guard expressions (A && B) and (A || B) evaluate to false when A==false and B==false. See lines 2155 and 529')

if __name__ == '__main__':
    unittest.main(verbosity=2)
