import unittest
from StateMachineParser import StateMachineParser
import StateMachineGenerator
from StateMachineDescriptors import Guard, State, StateType, Action, ActionType
import Helpers

class Test_StateMachineParserTests(Helpers.FloHsmTester):
    def setUp(self) -> None:
        self.parser = StateMachineParser()
                
    def parse(self, state_description:str) -> None:
        self.parser.parse(state_description)

    def assertParseResult(self, num_states:int=0, num_errors:int=0) -> None:
        self.assertEqual(num_states, len(self.parser.states))
        self.assertEqual(num_errors, len(self.parser.errors))

    def test_generated(self) -> None:
        import random

        random.seed(3)

        gen = StateMachineGenerator.Generator()
        description = gen.generate()
                
        self.parse(description)
        self.assertEqual(0, len(self.parser.errors))

    def test_parser_initial_state(self) -> None:
        self.assertParseResult()

    # Valid declarations
    def test_simple_state_declaration(self) -> None:
        description = 'state S'
        
        self.parse(description)
        self.assertParseResult(num_states=1)

        self.assertState(self.parser.states[0], name='S')

    def test_simple_choice_declaration(self) -> None:
        description = 'state S <<choice>>'
        
        self.parse(description)
        self.assertParseResult(num_states=1)

        self.assertState(self.parser.states[0], name='S', state_type=StateType.CHOICE)

    def test_leading_newlines_are_ignored(self) -> None:
        description = '''\n\n\nstate S\n'''
        
        self.parse(description)
        self.assertParseResult(num_states=1)
        self.assertState(self.parser.states[0], name='S')

    def test_simple_state_declaration_with_braces(self) -> None:
        description = '''
        state S{
        }
        '''

        self.parse(description)
        self.assertParseResult(num_states=1)
        self.assertState(self.parser.states[0], name='S')

    def test_composite_state_declaration(self) -> None:
        description = '''
        state S0{
          state S1
        }
        '''

        self.parse(description)
        self.assertParseResult(num_states=2)
        self.assertState(self.parser.states[0], name='S1', parent='S0')
        self.assertState(self.parser.states[1], name='S0', is_composite=True)

    def test_composite_state_with_nested_transition(self) -> None:
        description = '''
        state S0{
          [*] --> S1
        }
        '''

        self.parse(description)
        self.assertParseResult(num_states=2)
        self.assertState(self.parser.states[0], name='S1', parent='S0')
        self.assertState(self.parser.states[1], name='S0', is_composite=True)
        self.assertInitialTransition(self.parser.states[1].initial_transition, to='S1')

    def test_negative_guard(self) -> None:
        description = 'state S1 : E1 [!G1] / A1'

        self.parse(description)
        self.assertParseResult(num_states=1)
        self.assertState(self.parser.states[0], name='S1', num_int_transitions=1)
        g = self.parser.states[0].internal_transitions[0].guard
        
        self.assertGuard(g, '!G1', ['G1']);

    def test_guard_in_parentheses(self) -> None:
        description = 'state S1 : E1 [(G1)] / A1'

        self.parse(description)
        self.assertParseResult(num_states=1)
        self.assertState(self.parser.states[0], name='S1', num_int_transitions=1)
        g = self.parser.states[0].internal_transitions[0].guard
        
        self.assertSimpleGuard(g, 'G1');

    def test_guard_in_triple_parentheses(self) -> None:
        description = 'state S1 : E1 [(((G1)))] / A1'

        self.parse(description)
        self.assertParseResult(num_states=1)
        self.assertState(self.parser.states[0], name='S1', num_int_transitions=1)
        g = self.parser.states[0].internal_transitions[0].guard
        
        self.assertSimpleGuard(g, 'G1');

    def test_parentheses_mismatch(self) -> None:
        description = 'state S1 : E1 [(G1] / A1'

        self.parse(description)
        self.assertParseResult(num_states=0, num_errors=1)

    def test_negative_guard_in_parentheses(self) -> None:
        description = 'state S1 : E1 [!(!(G1))] / A1'

        self.parse(description)
        self.assertParseResult(num_states=1)
        self.assertState(self.parser.states[0], name='S1', num_int_transitions=1)
        g = self.parser.states[0].internal_transitions[0].guard
        
        self.assertSimpleGuard(g, 'G1');

    def test_and_guard(self) -> None:
        description = 'state S1 : E1 [G1 & G2] / A1'

        self.parse(description)
        self.assertParseResult(num_states=1)
        self.assertState(self.parser.states[0], name='S1', num_int_transitions=1)
        g = self.parser.states[0].internal_transitions[0].guard
        
        self.assertGuard(g, '(G1 && G2)', ['G1', 'G2']);

    def test_triple_and_guard(self) -> None:
        description = 'state S1 : E1 [G1 & G2 & G3] / A1'

        self.parse(description)
        self.assertParseResult(num_states=1)
        self.assertState(self.parser.states[0], name='S1', num_int_transitions=1)
        g = self.parser.states[0].internal_transitions[0].guard
        
        self.assertGuard(g, '((G1 && G2) && G3)', ['G1', 'G2', 'G3']);

    def test_or_guard(self) -> None:
        description = 'state S1 : E1 [G1 | G2] / A1'

        self.parse(description)
        self.assertParseResult(num_states=1)
        self.assertState(self.parser.states[0], name='S1', num_int_transitions=1)
        g = self.parser.states[0].internal_transitions[0].guard
        
        self.assertGuard(g, '(G1 || G2)', ['G1', 'G2']);

    def test_triple_or_guard(self) -> None:
        description = 'state S1 : E1 [G1 | G2 | G3] / A1'

        self.parse(description)
        self.assertParseResult(num_states=1)
        self.assertState(self.parser.states[0], name='S1', num_int_transitions=1)
        g = self.parser.states[0].internal_transitions[0].guard
        
        self.assertGuard(g, '((G1 || G2) || G3)', ['G1', 'G2', 'G3']);

    def test_operator_precedence(self) -> None:
        description = '''state S1 : E1 [G1 | G2 & G3] / A1
                         state S2 : E1 [G1 & G2 | G3] / A1
                         state S3 : E1 [!G1 & G2] / A1
                         state S4 : E1 [!G1 | G2] / A1'''

        self.parse(description)
        self.assertParseResult(num_states=4)
        self.assertState(self.parser.states[0], name='S1', num_int_transitions=1)
        self.assertState(self.parser.states[1], name='S2', num_int_transitions=1)
        self.assertState(self.parser.states[2], name='S3', num_int_transitions=1)
        self.assertState(self.parser.states[3], name='S4', num_int_transitions=1)
        
        g1 = self.parser.states[0].internal_transitions[0].guard
        self.assertGuard(g1, '(G1 || (G2 && G3))', ['G1', 'G2', 'G3']);
        g2 = self.parser.states[1].internal_transitions[0].guard
        self.assertGuard(g2, '((G1 && G2) || G3)', ['G1', 'G2', 'G3']);
        g3 = self.parser.states[2].internal_transitions[0].guard
        self.assertGuard(g3, '(!G1 && G2)', ['G1', 'G2']);
        g4 = self.parser.states[3].internal_transitions[0].guard
        self.assertGuard(g4, '(!G1 || G2)', ['G1', 'G2']);

    # Valid internal transitions
    def test_internal_transition_with_event_and_action_using_keyword_state(self) -> None:   
        description = 'state S1 : E1 / A1'

        self.parse(description)
        self.assertParseResult(num_states=1)
        self.assertState(self.parser.states[0], name='S1', num_int_transitions=1)

        it = self.parser.states[0].internal_transitions[0]
        self.assertInternalTransition(it, event='E1', action=Action('A1'))

    def test_internal_transition_with_event_guard_and_action_using_keyword_state(self) -> None:   
        description = 'state S1: E1 [G1] / A1'

        self.parse(description)
        self.assertParseResult(num_states=1)
        self.assertState(self.parser.states[0], name='S1', num_int_transitions=1)
        
        it = self.parser.states[0].internal_transitions[0]
        self.assertInternalTransition(it, event='E1', guard=Helpers.TestGuard('G1'), action=Action('A1'))
    
    def test_entry_with_action_using_keyword_state(self) -> None:   
        description = 'state S1: <<entry>> / A1'

        self.parse(description)
        self.assertParseResult(num_states=1)
        self.assertState(self.parser.states[0], name='S1', entry_action=Action('A1'))

    def test_exit_with_action_and_guard_using_keyword_state(self) -> None:
        description = 'state S1: <<exit>> [G1] / A1'

        self.parse(description)
        self.assertParseResult(num_states=1)
        self.assertState(self.parser.states[0], name='S1', exit_guard='G1', exit_action=Action('A1'))

    def test_internal_transition_with_event_and_action_without_keyword_state(self) -> None:   
        description = 'S1: E1 / A1'

        self.parse(description)
        self.assertParseResult(num_states=1)
        self.assertState(self.parser.states[0], name='S1', num_int_transitions=1)

        it = s = self.parser.states[0].internal_transitions[0]
        self.assertInternalTransition(it, event='E1', action=Action('A1'))

    def test_internal_transition_with_event_guard_and_action_without_keyword_state(self) -> None:   
        description = 'S1: E1 [G1] / A1'

        self.parse(description)
        self.assertParseResult(num_states=1)
        self.assertState(self.parser.states[0], name='S1', num_int_transitions=1)
        
        it = self.parser.states[0].internal_transitions[0]
        self.assertInternalTransition(it, event='E1', guard=Helpers.TestGuard('G1'), action=Action('A1'))

    def test_entry_with_action_without_keyword_state(self) -> None:   
        description = 'S1: <<entry>> / A1'

        self.parse(description)
        self.assertParseResult(num_states=1)
        self.assertState(self.parser.states[0], name='S1', entry_action=Action('A1'))

    def test_exit_with_action_and_guard_without_keyword_state(self) -> None:   
        description = 'S1: <<exit>> [G1] / A1'

        self.parse(description)
        self.assertParseResult(num_states=1)
        self.assertState(self.parser.states[0], name='S1', exit_guard='G1', exit_action=Action('A1'))
    
    # Valid state transitions
    def test_state_transition_with_event(self) -> None:   
        description = 'F --> T : E1'

        self.parse(description)
        self.assertParseResult(num_states=2)

        self.assertState(self.parser.states[0], name='F', num_state_transitions=1)
        self.assertState(self.parser.states[1], name='T')
        self.assertStateTransition(self.parser.states[0].state_transitions[0], to='T', event='E1')

    def test_state_transition_with_event_and_guard(self) -> None:   
        description = 'F --> T: E1 [G1]'

        self.parse(description)
        self.assertParseResult(num_states=2)

        self.assertState(self.parser.states[0], name='F', num_state_transitions=1)
        self.assertState(self.parser.states[1], name='T')
        self.assertStateTransition(self.parser.states[0].state_transitions[0], to='T', event='E1', guard='G1')

    def test_state_transition_with_event_and_action(self) -> None:   
        description = 'F --> T: E1 / A1'

        self.parse(description)
        self.assertParseResult(num_states=2)

        self.assertState(self.parser.states[0], name='F', num_state_transitions=1)
        self.assertState(self.parser.states[1], name='T')
        self.assertStateTransition(self.parser.states[0].state_transitions[0], to='T', event='E1', action=Action('A1'))

    def test_state_transition_with_event_and_guard_and_action(self) -> None:   
        description = 'F --> T: E1 [G1] / A1'

        self.parse(description)
        self.assertParseResult(num_states=2)

        self.assertState(self.parser.states[0], name='F', num_state_transitions=1)
        self.assertState(self.parser.states[1], name='T')
        self.assertStateTransition(self.parser.states[0].state_transitions[0], to='T', event='E1', guard='G1', action=Action('A1'))

    def test_initial_state_transition_without_action(self) -> None:   
        description = '[*] --> T'

        self.parse(description)
        self.assertParseResult(num_states=2)

        self.assertState(self.parser.states[0], name='FloHsmInitial_5OdpEA31BEcPrWrNx8u7')
        self.assertState(self.parser.states[1], name='T')
        self.assertInitialTransition(self.parser.states[0].initial_transition, to='T')

    def test_initial_state_transition_with_action(self) -> None:   
        description = '[*] --> T: A1(10)'

        self.parse(description)
        self.assertParseResult(num_states=2)

        self.assertState(self.parser.states[0], name='FloHsmInitial_5OdpEA31BEcPrWrNx8u7')
        self.assertState(self.parser.states[1], name='T')
        self.assertInitialTransition(self.parser.states[0].initial_transition, to='T', \
            action=Action(name='A1', type='int', value='10'))

    def test_state_transition_to_final_with_event(self) -> None:   
        description = 'F --> [*] : E1'

        self.parse(description)
        self.assertParseResult(num_states=2)

        self.assertState(self.parser.states[0], name='F', num_state_transitions=1)
        self.assertState(self.parser.states[1], name='FloHsmFinal_5OdpEA31BEcPrWrNx8u7')
        self.assertStateTransition(self.parser.states[0].state_transitions[0], to='FloHsmFinal_5OdpEA31BEcPrWrNx8u7', event='E1')

    def test_state_transition_to_final_with_event_and_guard(self) -> None:   
        description = 'F --> [*]: E1 [G1]'

        self.parse(description)
        self.assertParseResult(num_states=2)

        self.assertState(self.parser.states[0], name='F', num_state_transitions=1)
        self.assertState(self.parser.states[1], name='FloHsmFinal_5OdpEA31BEcPrWrNx8u7')
        self.assertStateTransition(self.parser.states[0].state_transitions[0], to='FloHsmFinal_5OdpEA31BEcPrWrNx8u7', event='E1', guard='G1')

    def test_state_transition_to_final_with_event_and_action(self) -> None:   
        description = 'F --> [*]: E1 / A1'

        self.parse(description)
        self.assertParseResult(num_states=2)

        self.assertState(self.parser.states[0], name='F', num_state_transitions=1)
        self.assertState(self.parser.states[1], name='FloHsmFinal_5OdpEA31BEcPrWrNx8u7')
        self.assertStateTransition(self.parser.states[0].state_transitions[0], to='FloHsmFinal_5OdpEA31BEcPrWrNx8u7', event='E1', action=Action('A1'))

    def test_state_transition_to_final_with_event_and_guard_and_action(self) -> None:   
        description = 'F --> [*]: E1 [G1] / A1'

        self.parse(description)
        self.assertParseResult(num_states=2)

        self.assertState(self.parser.states[0], name='F', num_state_transitions=1)
        self.assertState(self.parser.states[1], name='FloHsmFinal_5OdpEA31BEcPrWrNx8u7')
        self.assertStateTransition(self.parser.states[0].state_transitions[0], to='FloHsmFinal_5OdpEA31BEcPrWrNx8u7', event='E1', guard='G1', action=Action('A1'))

    def test_initial_state_transition_to_final_without_action(self) -> None:   
        description = '[*] --> [*]'

        self.parse(description)
        self.assertParseResult(num_states=2)

        self.assertState(self.parser.states[0], name='FloHsmInitial_5OdpEA31BEcPrWrNx8u7')
        self.assertState(self.parser.states[1], name='FloHsmFinal_5OdpEA31BEcPrWrNx8u7')
        self.assertInitialTransition(self.parser.states[0].initial_transition, to='FloHsmFinal_5OdpEA31BEcPrWrNx8u7')

    def test_initial_state_transition_to_final_with_action(self) -> None:   
        description = '[*] --> [*] : A1'

        self.parse(description)
        self.assertParseResult(num_states=2)

        self.assertState(self.parser.states[0], name='FloHsmInitial_5OdpEA31BEcPrWrNx8u7')
        self.assertState(self.parser.states[1], name='FloHsmFinal_5OdpEA31BEcPrWrNx8u7')
        self.assertInitialTransition(self.parser.states[0].initial_transition, to='FloHsmFinal_5OdpEA31BEcPrWrNx8u7', action=Action('A1'))

    def test_internal_initial_transition(self) -> None:
        description = '''
        state S1{
          [*]-->S2
        }
        '''

        self.parse(description)
        self.assertParseResult(num_states=2)
        
        self.assertState(self.parser.states[0], name='S2', parent='S1')
        self.assertState(self.parser.states[1], name='S1', is_composite=True)
        self.assertInitialTransition(self.parser.states[1].initial_transition, to='S2')


    def test_entry_is_a_valid_event_name(self) -> None: 
        description = 'F --> T: entry'

        self.parse(description)
        self.assertParseResult(num_states=2)

    def test_entry_is_a_valid_event_name_2(self) -> None: 
        description = 'F --> T: entry [G1]'

        self.parse(description)
        self.assertParseResult(num_states=2)

    def test_entry_is_a_valid_event_name_3(self) -> None: 
        description = 'F --> T: entry / A1'

        self.parse(description)
        self.assertParseResult(num_states=2)

    def test_entry_is_a_valid_event_name_4(self) -> None: 
        description = 'F --> T: entry [G1] / A1'

        self.parse(description)
        self.assertParseResult(num_states=2)

    def test_exit_is_a_valid_event_name(self) -> None: 
        description = 'F --> T: exit'

        self.parse(description)
        self.assertParseResult(num_states=2)

    def test_exit_is_a_valid_event_name_2(self) -> None: 
        description = 'F --> T: exit [G1]'

        self.parse(description)
        self.assertParseResult(num_states=2)

    def test_exit_is_a_valid_event_name_3(self) -> None: 
        description = 'F --> T: exit / A1'

        self.parse(description)
        self.assertParseResult(num_states=2)

    def test_exit_is_a_valid_event_name_4(self) -> None: 
        description = 'F --> T: exit [G1] / A1'

        self.parse(description)
        self.assertParseResult(num_states=2)

    # Invalid 
    def test_state_transition_without_event(self) -> None: 
        description = 'F --> T'

        self.parse(description)
        self.assertParseResult(num_errors=1)

    def test_state_transition_with_only_guard(self) -> None: 
        description = 'F --> T : [G1]'

        self.parse(description)
        self.assertParseResult(num_errors=1)

    def test_initial_transition_cannot_have_guard(self) -> None: 
        description = '[*] --> S2 : [G1]'

        self.parse(description)
        self.assertParseResult(num_errors=1)

    def test_initial_transition_cannot_have_guard_2(self) -> None: 
        description = '[*] --> S2 : A1 [G1]'

        self.parse(description)
        self.assertParseResult(num_errors=1)

    def test_initial_transition_cannot_have_guard_3(self) -> None: 
        description = '[*] --> S2 : [G1] A1'

        self.parse(description)
        self.assertParseResult(num_errors=1)

    def test_initial_transition_cannot_have_action(self) -> None: 
        description = '[*] --> S2 : A1 / A2'

        self.parse(description)
        self.assertParseResult(num_errors=1)

    def test_initial_transition_cannot_have_guard_and_action(self) -> None: 
        description = '[*] --> S2 : A1 [G1] / A2'

        self.parse(description)
        self.assertParseResult(num_errors=1)

    def test_lexical_error(self) -> None: 
        description = 'state 8 : <<entry>> / A1'

        self.parse(description)
        self.assertParseResult(num_errors=1)

    def test_lexical_error_is_not_skipped(self) -> None: 
        description = 'state 8 S : <<entry>> / A1'

        self.parse(description)
        self.assertParseResult(num_errors=1)

    def test_syntax_error(self) -> None: 
        description = 'state S S : <<entry>> / A1'

        self.parse(description)
        self.assertParseResult(num_errors=1)

    def test_syntax_error_2(self) -> None: 
        description = 'state S : : <<entry>> / A1'

        self.parse(description)
        self.assertParseResult(num_errors=1)

    def test_syntax_error_in_complex_state(self) -> None: 
        description = '''state S0 S1 {
                           state S2
                         }'''

        self.parse(description)
        self.assertParseResult(num_states=1, num_errors=2)

    def test_recover_after_syntax_error(self) -> None: 
        description = '''state S : : <<entry>> / A1
                         state S : <<entry>> / A1'''

        self.parse(description)
        self.assertParseResult(num_states=1, num_errors=1)

    def test_choice_transition_without_action(self) -> None:
        description = 'F --> T: <<choice>> [G1]'
        
        self.parse(description)
        self.assertParseResult(num_states=2)
        self.assertEqual('F', self.parser.states[0].name)
        self.assertEqual(StateType.CHOICE, self.parser.states[0].state_type)

    def test_choice_transition_with_action(self) -> None:
        description = 'F --> T: <<choice>> [G1] / A1'
        
        self.parse(description)
        self.assertParseResult(num_states=2)
        self.assertEqual('F', self.parser.states[0].name)
        self.assertEqual(StateType.CHOICE, self.parser.states[0].state_type)

    def test_choice_transition_without_guard_and_with_action_is_not_valid(self) -> None:
        description = 'F --> T: <<choice>>'
        
        self.parse(description)
        self.assertParseResult(num_errors=1)

    def test_choice_transition_without_guard_is_not_valid(self) -> None:
        description = 'F --> T: <<choice>> / A1'
        
        self.parse(description)
        self.assertParseResult(num_errors=1)

    def test_action_with_argument_int(self) -> None:
        description = 'F --> T: E1 / A1(10)'
        
        self.parse(description)
        self.assertParseResult(num_states=2)
        self.assertState(self.parser.states[0], name='F', num_state_transitions=1)
        self.assertState(self.parser.states[1], name='T')

        t = self.parser.states[0].state_transitions[0]
        self.assertStateTransition(t, to='T', event='E1', 
                                   action=Action(name='A1', type=ActionType.INT, value='10'));

if __name__ == '__main__':
    unittest.main(verbosity=2)
