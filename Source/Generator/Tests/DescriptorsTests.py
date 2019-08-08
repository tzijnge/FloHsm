import unittest
from Descriptors import State, StateType, InternalTransition, InitialTransition,\
                                    StateTransition, ChoiceTransition, Action, ActionType
from Descriptors import Guard, SimpleGuard, NotGuard, AndGuard, OrGuard, EntryExit
import Helpers

class DescriptorTests(Helpers.FloHsmTester):
    def test_cannot_merge_states_with_different_names(self) -> None:
        s1 = Helpers.TestState(name='S1')
        s2 = Helpers.TestState(name='S2')
        self.assertFalse(s1.merge(s2))
        
    def test_merge_states_with_same_name(self) -> None:
        s1 = Helpers.TestState(name='S1')
        s2 = Helpers.TestState(name='S1')

        self.assertTrue(s1.merge(s2))
        self.assertState(s1, name='S1')

    def test_merge_state_and_choice_pseudo_state_with_same_name(self) -> None:
        s1 = Helpers.TestState(name='S1')
        s2 = State(name='S1', lineno=0, state_type=StateType.CHOICE)

        self.assertTrue(s1.merge(s2))
        self.assertState(s1, name='S1', state_type=StateType.CHOICE)

    def test_merge_states_with_different_parents(self) -> None:
        s1_1 = Helpers.TestState(name='S1', parent='P1')
        s1_2 = Helpers.TestState(name='S1', parent='P2')
        self.assertFalse(s1_1.merge(s1_2))

        s1_1 = Helpers.TestState(name='S1', parent=None)
        s1_2 = Helpers.TestState(name='S1', parent='P2')
        self.assertTrue(s1_1.merge(s1_2))
        self.assertState(s1_1, name='S1', parent='P2')

        s1_1 = Helpers.TestState(name='S1', parent='P1')
        s1_2 = Helpers.TestState(name='S1', parent=None)
        self.assertTrue(s1_1.merge(s1_2))
        self.assertState(s1_1, name='S1', parent='P1')

    def test_merge_equal_entry_statements(self) -> None:
        s1_1 = Helpers.TestState(name='S1', entry=EntryExit(action=Action('A1'), guard=Helpers.TestGuard('G1')))
        s1_2 = Helpers.TestState(name='S1', entry=EntryExit(action=Action('A1'), guard=Helpers.TestGuard('G1')))

        self.assertFalse(s1_1.merge(s1_2))

    def test_merge_different_entry_statements(self) -> None:
        s1_1 = Helpers.TestState(name='S1', entry=EntryExit(action=Action('A1'), guard=Helpers.TestGuard('G1')))
        s1_2 = Helpers.TestState(name='S1', entry=EntryExit(action=Action('A2'), guard=Helpers.TestGuard('G2')))

        self.assertFalse(s1_1.merge(s1_2))

    def test_merge_entry(self) -> None:
        s1_1 = Helpers.TestState(name='S1', entry=EntryExit(action=Action('A1'), guard=Helpers.TestGuard('G1')))
        s1_2 = Helpers.TestState(name='S1')

        self.assertTrue(s1_1.merge(s1_2))
        self.assertState(s1_1, name='S1', entry_action=Action('A1'), entry_guard='G1')

        s1_1 = Helpers.TestState(name='S1')
        s1_2 = Helpers.TestState(name='S1', entry=EntryExit(action=Action('A1'), guard=Helpers.TestGuard('G1')))

        self.assertTrue(s1_1.merge(s1_2))
        self.assertState(s1_1, name='S1', entry_action=Action('A1'), entry_guard='G1')

    def test_merge_equal_exit_statements(self) -> None:
        s1_1 = Helpers.TestState(name='S1', exit=EntryExit(action=Action('A1'), guard=Helpers.TestGuard('G1')))
        s1_2 = Helpers.TestState(name='S1', exit=EntryExit(action=Action('A1'), guard=Helpers.TestGuard('G1')))

        self.assertFalse(s1_1.merge(s1_2))

    def test_merge_different_exit_statements(self) -> None:
        s1_1 = Helpers.TestState(name='S1', exit=EntryExit(action=Action('A1'), guard=Helpers.TestGuard('G1')))
        s1_2 = Helpers.TestState(name='S1', exit=EntryExit(action=Action('A2'), guard=Helpers.TestGuard('G2')))

        self.assertFalse(s1_1.merge(s1_2))

    def test_merge_exit(self) -> None:
        s1_1 = Helpers.TestState(name='S1', exit=EntryExit(action=Action('A1'), guard=Helpers.TestGuard('G1')))
        s1_2 = Helpers.TestState(name='S1')

        self.assertTrue(s1_1.merge(s1_2))
        self.assertState(s1_1, name='S1', exit_action=Action('A1'), exit_guard='G1')

        s1_1 = Helpers.TestState(name='S1')
        s1_2 = Helpers.TestState(name='S1', exit=EntryExit(action=Action('A1'), guard=Helpers.TestGuard('G1')))

        self.assertTrue(s1_1.merge(s1_2))
        self.assertState(s1_1, name='S1', exit_action=Action('A1'), exit_guard='G1')

    def test_merge_internal_transitions_with_empty_list(self) -> None:
        s1_1 = Helpers.TestState(name='S1', internal_transitions=[InternalTransition(event='E1', action=Action('A1'))])
        s1_2 = Helpers.TestState(name='S1')

        self.assertTrue(s1_1.merge(s1_2))
        self.assertState(s1_1, name='S1', num_int_transitions=1)
        self.assertInternalTransition(s1_1.internal_transitions[0], event='E1', action=Action('A1'))

        s1_1 = Helpers.TestState(name='S1')
        s1_2 = Helpers.TestState(name='S1', internal_transitions=[InternalTransition(event='E1', action=Action('A1'))])

        self.assertTrue(s1_1.merge(s1_2))
        self.assertState(s1_1, name='S1', num_int_transitions=1)
        self.assertInternalTransition(s1_1.internal_transitions[0], event='E1', action=Action('A1'))

    def test_merge_internal_transitions_from_two_states(self) -> None:
        s1_1 = Helpers.TestState(name='S1', internal_transitions=[InternalTransition(event='E1', action=Action('A1'))])
        s1_2 = Helpers.TestState(name='S1', internal_transitions=[InternalTransition(event='E1', action=Action('A1'))])

        self.assertTrue(s1_1.merge(s1_2))
        self.assertState(s1_1, name='S1', num_int_transitions=2)
        self.assertInternalTransition(s1_1.internal_transitions[0], event='E1', action=Action('A1'))
        self.assertInternalTransition(s1_1.internal_transitions[1], event='E1', action=Action('A1'))

        s1_1 = Helpers.TestState(name='S1', internal_transitions=[InternalTransition(event='E1', action=Action('A1'))])
        s1_2 = Helpers.TestState(name='S1', internal_transitions=[InternalTransition(event='E2', action=Action('A1'))])

        self.assertTrue(s1_1.merge(s1_2))
        self.assertState(s1_1, name='S1', num_int_transitions=2)
        self.assertInternalTransition(s1_1.internal_transitions[0], event='E1', action=Action('A1'))
        self.assertInternalTransition(s1_1.internal_transitions[1], event='E2', action=Action('A1'))

    def test_merge_state_transitions_with_empty_list(self) -> None:
        s1_1 = Helpers.TestState(name='S1', state_transitions=[StateTransition(toState='S2', event='E1')])
        s1_2 = Helpers.TestState(name='S1')

        self.assertTrue(s1_1.merge(s1_2))
        self.assertState(s1_1, name='S1', num_state_transitions=1)
        self.assertStateTransition(s1_1.state_transitions[0], to='S2', event='E1')

        s1_1 = Helpers.TestState(name='S1')
        s1_2 = Helpers.TestState(name='S1', state_transitions=[StateTransition(toState='S2', event='E1')])

        self.assertTrue(s1_1.merge(s1_2))
        self.assertState(s1_1, name='S1', num_state_transitions=1)
        self.assertStateTransition(s1_1.state_transitions[0], to='S2', event='E1')

    def test_merge_state_transitions_from_two_states(self) -> None:
        s1_1 = Helpers.TestState(name='S1', state_transitions=[StateTransition(toState='S2', event='E1')])
        s1_2 = Helpers.TestState(name='S1', state_transitions=[StateTransition(toState='S2', event='E1')])

        self.assertTrue(s1_1.merge(s1_2))
        self.assertState(s1_1, name='S1', num_state_transitions=2)
        self.assertStateTransition(s1_1.state_transitions[0], to='S2', event='E1')
        self.assertStateTransition(s1_1.state_transitions[1], to='S2', event='E1')

        s1_1 = Helpers.TestState(name='S1', state_transitions=[StateTransition(toState='S2', event='E1')])
        s1_2 = Helpers.TestState(name='S1', state_transitions=[StateTransition(toState='S3', event='E2')])

        self.assertTrue(s1_1.merge(s1_2))
        self.assertState(s1_1, name='S1', num_state_transitions=2)
        self.assertStateTransition(s1_1.state_transitions[0], to='S2', event='E1')
        self.assertStateTransition(s1_1.state_transitions[1], to='S3', event='E2')

    def test_merge_choice_transition(self) -> None:
        s1_1 = Helpers.TestState(name='Choice', choice_transitions=[ChoiceTransition('S2', Helpers.TestGuard('G1'))])
        s1_2 = Helpers.TestState(name='Choice', choice_transitions=[ChoiceTransition('S3', Helpers.TestGuard('G2'))])

        self.assertTrue(s1_1.merge(s1_2))
        self.assertState(s1_1, name='Choice', num_choice_transitions=2)
        self.assertChoiceTransition(s1_1.choice_transitions[0], to='S2', guard='G1')
        self.assertChoiceTransition(s1_1.choice_transitions[1], to='S3', guard='G2')

    def test_merge_equal_composite_statements(self) -> None:
        s1_1 = Helpers.TestState(name='S1', is_composite=True)
        s1_2 = Helpers.TestState(name='S1', is_composite=True)

        self.assertTrue(s1_1.merge(s1_2))
        self.assertState(s1_1, name='S1', is_composite=True)

        s1_1 = Helpers.TestState(name='S1', is_composite=False)
        s1_2 = Helpers.TestState(name='S1', is_composite=False)

        self.assertTrue(s1_1.merge(s1_2))
        self.assertState(s1_1, name='S1', is_composite=False)

    def test_merge_different_composite_statements(self) -> None:
        s1_1 = Helpers.TestState(name='S1', is_composite=True)
        s1_2 = Helpers.TestState(name='S1', is_composite=False)

        self.assertTrue(s1_1.merge(s1_2))
        self.assertState(s1_1, name='S1', is_composite=True)

        s1_1 = Helpers.TestState(name='S1', is_composite=False)
        s1_2 = Helpers.TestState(name='S1', is_composite=True)

        self.assertTrue(s1_1.merge(s1_2))
        self.assertState(s1_1, name='S1', is_composite=True)

    def test_merge_line_numbers_from_two_states(self) -> None:
        s1_1 = Helpers.TestState(name='S1', lineno=1)
        s1_2 = Helpers.TestState(name='S1', lineno=2)

        self.assertTrue(s1_1.merge(s1_2))
        self.assertEqual(s1_1.name, 'S1')
        self.assertEqual(s1_1.lineno, [1, 2])

    def test_merge_initial_transition(self) -> None:
        s1_1 = Helpers.TestState(name='S1', lineno=1, initial_transition=InitialTransition(toState='S2'))
        s1_2 = Helpers.TestState(name='S1', lineno=2)

        self.assertTrue(s1_1.merge(s1_2))
        self.assertEqual(s1_1.name, 'S1')
        self.assertEqual(s1_1.lineno, [1, 2])

        self.assertInitialTransition(s1_1.initial_transition, to='S2')

        s2_1 = Helpers.TestState(name='S2', lineno=1)
        s2_2 = Helpers.TestState(name='S2', lineno=2, initial_transition=InitialTransition(toState='S3', action=Action('A1')))

        self.assertTrue(s2_1.merge(s2_2))
        self.assertEqual(s2_1.name, 'S2')
        self.assertEqual(s2_1.lineno, [1, 2])
        self.assertInitialTransition(s2_1.initial_transition, to='S3', action=Action('A1'))

    def test_merge_two_initial_transitions_is_not_possible(self) -> None:
        s1_1 = Helpers.TestState(name='S1', lineno=1, initial_transition=InitialTransition(toState='S2'))
        s1_2 = Helpers.TestState(name='S1', lineno=2, initial_transition=InitialTransition(toState='S3'))

        self.assertFalse(s1_1.merge(s1_2))

    def test_simple_guard(self) -> None:
        g = SimpleGuard('G1', 0)
        self.assertEqual('G1', g.to_string())
        self.assertEqual(1, len(g.guard_conditions()))
        self.assertIn('G1', g.guard_conditions())

    def test_not_guard(self) -> None:
        g = NotGuard(Helpers.TestGuard('G1'))
        self.assertEqual('!G1', g.to_string())
        self.assertEqual(1, len(g.guard_conditions()))
        self.assertIn('G1', g.guard_conditions())

    def test_simplify_not_guard_1(self) -> None:
        g = NotGuard(NotGuard(Helpers.TestGuard('G1')))
        self.assertEqual('G1', g.to_string())
        self.assertEqual(1, len(g.guard_conditions()))
        self.assertIn('G1', g.guard_conditions())

    def test_simplify_not_guard_2(self) -> None:
        g = NotGuard(NotGuard(NotGuard(Helpers.TestGuard('G1'))))
        self.assertEqual('!G1', g.to_string())
        self.assertEqual(1, len(g.guard_conditions()))
        self.assertIn('G1', g.guard_conditions())

    def test_and_guard(self) -> None:
        g = AndGuard(Helpers.TestGuard('G1'), Helpers.TestGuard('G2'))
        self.assertEqual('(G1 && G2)', g.to_string())
        self.assertEqual(2, len(g.guard_conditions()))
        self.assertIn('G1', g.guard_conditions())
        self.assertIn('G2', g.guard_conditions())

    def test_or_guard(self) -> None:
        g = OrGuard(Helpers.TestGuard('G1'), Helpers.TestGuard('G2'))
        self.assertEqual('(G1 || G2)', g.to_string())
        self.assertEqual(2, len(g.guard_conditions()))
        self.assertIn('G1', g.guard_conditions())
        self.assertIn('G2', g.guard_conditions())

    def test_complex_guard(self) -> None:
        g = OrGuard(Helpers.TestGuard('G1'), NotGuard(AndGuard(OrGuard(Helpers.TestGuard('G2'), Helpers.TestGuard('G3')), NotGuard(Helpers.TestGuard('G4')))))
        self.assertEqual('(G1 || !((G2 || G3) && !G4))', g.to_string())
        self.assertEqual(4, len(g.guard_conditions()))
        self.assertIn('G1', g.guard_conditions())
        self.assertIn('G2', g.guard_conditions())
        self.assertIn('G3', g.guard_conditions())
        self.assertIn('G4', g.guard_conditions())

    def test_guards_can_appear_in_complex_expression_more_than_once(self) -> None:
        g = OrGuard(Helpers.TestGuard('G1'), Helpers.TestGuard('G1'))
        self.assertEqual('(G1 || G1)', g.to_string())
        self.assertEqual(1, len(g.guard_conditions()))
        self.assertIn('G1', g.guard_conditions())

    def test_evaluate_simple_guard(self) -> None:
        g = SimpleGuard('G1', 0)
        self.assertFalse(g.evaluate(0))
        self.assertTrue(g.evaluate(1))

    def test_evaluate_not_guard(self) -> None:
        g = NotGuard(Helpers.TestGuard('G1'))
        self.assertTrue(g.evaluate(0))
        self.assertFalse(g.evaluate(1))

    def test_evaluate_and_guard(self) -> None:
        g = AndGuard(Helpers.TestGuard('G1'), Helpers.TestGuard('G2'))
        self.assertFalse(g.evaluate(0))
        self.assertFalse(g.evaluate(1))
        self.assertFalse(g.evaluate(2))
        self.assertTrue(g.evaluate(3))

    def test_evaluate_or_guard(self) -> None:
        g = OrGuard(Helpers.TestGuard('G1'), Helpers.TestGuard('G2'))
        self.assertFalse(g.evaluate(0))
        self.assertTrue(g.evaluate(1))
        self.assertTrue(g.evaluate(2))
        self.assertTrue(g.evaluate(3))

    def test_evaluate_complex_guard(self) -> None:
        # (!G1 || ((!G2 || G3) && G1))
        g = OrGuard(NotGuard(Helpers.TestGuard('G1')), AndGuard(OrGuard(NotGuard(Helpers.TestGuard('G2')), Helpers.TestGuard('G3')), Helpers.TestGuard('G1')))
        
        self.assertTrue(g.evaluate(0))
        self.assertTrue(g.evaluate(1))
        self.assertTrue(g.evaluate(2))
        self.assertFalse(g.evaluate(3))
        self.assertTrue(g.evaluate(4))
        self.assertTrue(g.evaluate(5))
        self.assertTrue(g.evaluate(6))
        self.assertTrue(g.evaluate(7))

    def test_evaluate_guard_with_custom_bit_index(self) -> None:
        g = Helpers.TestGuard('G1')
        bit_index = {'G1' : 5}
        for i in range(0, 31):
            self.assertFalse(g.evaluate(i, bit_index))

        self.assertTrue(g.evaluate(32, bit_index))

    def test_guard_lineno(self) -> None:
        g1 = SimpleGuard('G1', 1234)
        g2 = SimpleGuard('G2', 4321)

        self.assertEqual(1234, g1.lineno())
        self.assertEqual(1234, NotGuard(g1).lineno())
        self.assertEqual(1234, OrGuard(g1, g2).lineno())
        self.assertEqual(4321, OrGuard(g2, g1).lineno())
        self.assertEqual(1234, AndGuard(g1, g2).lineno())
        self.assertEqual(4321, AndGuard(g2, g1).lineno())

    def test_all_events_of_state(self) -> None:
        it1 = InternalTransition(event='E1', action=Action('A1'))
        it2 = InternalTransition(event='E2', action=Action('A2'))
        st1 = StateTransition(event='E3', toState='S2')
        st2 = StateTransition(event='E4', toState='S2')
        st3 = StateTransition(event='E4', toState='S3')
        s = State(name='S', lineno=0, internal_transitions=[it1, it2], state_transitions=[st1, st2, st3]);

        self.assertEqual(4, len(s.events()))
        self.assertIn('E1', s.events())
        self.assertIn('E2', s.events())
        self.assertIn('E3', s.events())
        self.assertIn('E4', s.events())

    def test_all_guard_conditions_for_event(self) -> None:
        it1 = InternalTransition(event='E2', action=Action('A2'), guard=Helpers.TestGuard('G1'))
        st1 = StateTransition(event='E2', toState='S2', guard=AndGuard(NotGuard(Helpers.TestGuard('G1')), Helpers.TestGuard('G2')))

        s = State(name='S', lineno=0, internal_transitions=[it1], state_transitions=[st1]);

        self.assertEqual(0, len(s.guard_conditions_for_event('E1')))
        self.assertEqual(2, len(s.guard_conditions_for_event('E2')))
        self.assertIn('G1', s.guard_conditions_for_event('E2'))
        self.assertIn('G2', s.guard_conditions_for_event('E2'))

    def test_all_internal_transitions_for_event(self) -> None:
        it1 = InternalTransition(event='E1', action=Action('A1'))
        it2 = InternalTransition(event='E2', action=Action('A2'))
        st1 = StateTransition(event='E1', toState='S2')
        st2 = StateTransition(event='E4', toState='S2')
        st3 = StateTransition(event='E4', toState='S3')
        s = State(name='S', lineno=0, internal_transitions=[it1, it2], state_transitions=[st1, st2, st3]);

        self.assertEqual(1, len(s.internal_transitions_for_event('E1')))
        it = s.internal_transitions_for_event('E1')

    def test_all_state_transitions_for_event(self) -> None:
        it1 = InternalTransition(event='E1', action=Action('A1'))
        it2 = InternalTransition(event='E2', action=Action('A2'))
        st1 = StateTransition(event='E1', toState='S2')
        st2 = StateTransition(event='E4', toState='S2')
        st3 = StateTransition(event='E4', toState='S3')
        s = State(name='S', lineno=0, internal_transitions=[it1, it2], state_transitions=[st1, st2, st3]);

        self.assertEqual(1, len(s.state_transitions_for_event('E1')))
        st = s.state_transitions_for_event('E1')

    def test_action_prototype_and_invocation_strings(self) -> None:
        a1 = Action(name='A1', type=ActionType.INT, value='10')
        a2 = Action(name='A2', type=ActionType.FLOAT, value='12.34')
        a3 = Action(name='A3', type=ActionType.BOOL, value='true')
        a4 = Action(name='A4', type=ActionType.STRING, value='"Test123"')
        a5 = Action(name='A5')

        self.assertEqual('void A1(int i)', a1.prototype_string())
        self.assertEqual('A1(10)', a1.invocation_string())
        self.assertEqual('void A2(float f)', a2.prototype_string())
        self.assertEqual('A2(12.34f)', a2.invocation_string())
        self.assertEqual('void A3(bool b)', a3.prototype_string())
        self.assertEqual('A3(true)', a3.invocation_string())
        self.assertEqual('void A4(const char* s)', a4.prototype_string())
        self.assertEqual('A4("Test123")', a4.invocation_string())
        self.assertEqual('void A5()', a5.prototype_string())
        self.assertEqual('A5()', a5.invocation_string())

if __name__ == '__main__':
    unittest.main(verbosity=2)
