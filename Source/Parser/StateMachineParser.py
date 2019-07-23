import ply.yacc as yacc
from StateMachineLexer import StateMachineLexer
from StateMachineDescriptors import State, StateType, EntryExit, StateTransition, InitialTransition, InternalTransition, ChoiceTransition
from StateMachineDescriptors import SimpleGuard, NotGuard, AndGuard, OrGuard
import binascii
from typing import List

class StateMachineParser(object):
    states : List[State]
    errors : List[str]

    precedence = (
     ('left', 'OR'),
     ('left', 'AND'),
     ('right', 'NOT')
    )

    def __init__(self) -> None:
        self.lexer = StateMachineLexer()
        self.tokens = self.lexer.tokens
        self.parser = yacc.yacc(module=self, debug=False)
        self.states = list()
        self.errors = list()

    def parse(self, data:str) -> None:
        self.parser.parse(data, lexer=self.lexer)

    def p_top_level_states(self, p:yacc.Production) -> None:
        '''top_level_states : state_list
                            | empty'''

        for state in p[1]:
            if state.name == '[*]_Initial':
                initial = State(name='FloHsmInitial_5OdpEA31BEcPrWrNx8u7', lineno=-1, initial_transition=state.initial_transition)
                self.states.append(initial)
            else:
                self.states.append(state)
    
    def p_state_list_first_empty(self, p:yacc.Production) -> None:
        'state_list : ignore'
        p[0] = list()

    def p_state_list_first_state(self, p:yacc.Production) -> None:
        'state_list : state'
        p[0] = list()
        p[0].append(p[1])

    def p_state_list_first_states(self, p:yacc.Production) -> None:
        'state_list : states_from_transition'
        p[0] = p[1]

    def p_state_list_next_empty(self, p:yacc.Production) -> None:
        'state_list : state_list ignore'
        p[0] = p[1]

    def p_state_list_next_state(self, p:yacc.Production) -> None:
        'state_list : state_list state'
        p[0] = p[1]
        p[0].append(p[2])

    def p_state_list_next(self, p:yacc.Production) -> None:
        'state_list : state_list states_from_transition'
        p[0] = p[1]
        p[0].extend(p[2])

    def p_state_or_transition_transition(self, p:yacc.Production) -> None:
        '''states_from_transition : transition NEWLINE'''
        f = p[1].get('from')
        t = p[1].get('to')
        p[0] = list()
        p[0].append(f)
        p[0].append(t)

    def p_transition(self, p:yacc.Production) -> None:
        '''transition : transition_from_state
                      | transition_from_initial 
                      | transition_from_choice'''
        p[0] = p[1]

    def p_transition_from_state(self, p:yacc.Production) -> None:
        '''transition_from_state : NAME TRANSITION NAME event_with_optional_guard optional_action
                                 | NAME TRANSITION STATE_INITIAL_OR_FINAL event_with_optional_guard optional_action'''

        fromState = State(name=p[1], lineno=p.slice[1].lineno)
        
        event=p[4].get('event', None) if p[4] is not None else None
        to_state = p[3]
        guard = p[4].get('guard', None) if p[4] is not None else None
        action = p[5]

        fromState.state_transitions.append(StateTransition(event, to_state, action, guard))
        
        toState = State(name=p[3], lineno=p.slice[3].lineno)

        p[0] = {'from' : fromState, 'to' : toState}

    def p_transition_from_initial(self, p:yacc.Production) -> None:
        '''transition_from_initial : STATE_INITIAL_OR_FINAL TRANSITION NAME optional_action_at_initial_transition
                                   | STATE_INITIAL_OR_FINAL TRANSITION STATE_INITIAL_OR_FINAL optional_action_at_initial_transition'''

        fromState = State('[*]_Initial', lineno=p.slice[1].lineno)
        
        to_state = p[3]
        action = p[4]
        fromState.initial_transition = InitialTransition(to_state, action)
        
        toState = State(name=p[3], lineno=p.slice[3].lineno)

        p[0] = {'from' : fromState, 'to' : toState}

    def p_action_at_initial_transition(self, p:yacc.Production) -> None:
        'action_at_initial_transition : COLON NAME'
        p[0] = p[2]

    def p_optional_action_at_initial_transition(self, p:yacc.Production) -> None:
        ''' optional_action_at_initial_transition : action_at_initial_transition
                                                  | empty'''
        p[0] = p[1]

    def p_transition_from_choice(self, p:yacc.Production) -> None:
        '''transition_from_choice : NAME TRANSITION NAME COLON CHOICE LBRACKET guard_exp RBRACKET optional_action'''

        fromState = State(name=p[1], lineno=p.slice[1].lineno, state_type=StateType.CHOICE)
        fromState.choice_transitions.append(ChoiceTransition(p[3], p[7], p[9]))
        
        toState = State(name=p[3], lineno=p.slice[3].lineno)

        p[0] = {'from' : fromState, 'to' : toState}

    def p_action(self, p:yacc.Production) -> None:
        'action : FORWARD_SLASH NAME'
        p[0] = p[2]

    def p_optional_action(self, p:yacc.Production) -> None:
        ''' optional_action : action
                            | empty'''
        
        p[0] = p[1]

    def p_event_with_optional_guard(self, p:yacc.Production) -> None:
        '''event_with_optional_guard : event
                                     | event_with_guard'''
        p[0] = p[1]

    def p_event(self, p:yacc.Production) -> None:
        'event : COLON NAME'
        p[0] = {'event': p[2], 'guard' : None}

    def p_event_with_guard(self, p:yacc.Production) -> None:
        'event_with_guard : COLON NAME LBRACKET guard_exp RBRACKET'
        p[0] = {'event': p[2], 'guard' : p[4]}

    def p_entry_with_optional_guard(self, p:yacc.Production) -> None:
        '''entry_with_optional_guard : entry_pseudo_event
                                     | entry_with_guard'''
        p[0] = p[1]

    def p_entry_pseudo_event(self, p:yacc.Production) -> None:
        'entry_pseudo_event : COLON ENTRY'
        p[0] = None

    def p_entry_with_guard(self, p:yacc.Production) -> None:
        'entry_with_guard : COLON ENTRY LBRACKET guard_exp RBRACKET'
        p[0] = p[4]

    def p_exit_with_optional_guard(self, p:yacc.Production) -> None:
        '''exit_with_optional_guard : exit_pseudo_event
                                    | exit_with_guard'''
        p[0] = p[1]

    def p_exit_pseudo_event(self, p:yacc.Production) -> None:
        'exit_pseudo_event : COLON EXIT'
        p[0] = None

    def p_exit_with_guard(self, p:yacc.Production) -> None:
        'exit_with_guard : COLON EXIT LBRACKET guard_exp RBRACKET'
        p[0] = p[4]

    def p_guard_exp(self, p:yacc.Production) -> None:
        '''guard_exp : simple_guard_exp
                     | negative_guard_exp'''
        p[0] = p[1]

    def p_guard_exp_in_parenthes(self, p:yacc.Production) -> None:
        '''guard_exp : LPAREN guard_exp RPAREN'''
        p[0] = p[2]

    def p_guard_exp_and(self, p:yacc.Production) -> None:
        '''guard_exp : guard_exp AND guard_exp'''
        
        p[0] = AndGuard(p[1], p[3])

    def p_guard_exp_or(self, p:yacc.Production) -> None:
        '''guard_exp : guard_exp OR guard_exp'''
        
        p[0] = OrGuard(p[1], p[3])

    def p_simple_guard_exp(self, p:yacc.Production) -> None:
        'simple_guard_exp : NAME'
        p[0] = SimpleGuard(guard=p[1], lineno=p.slice[1].lineno)

    def p_negative_guard_exp(self, p:yacc.Production) -> None:
        'negative_guard_exp : NOT guard_exp'
        p[0] = NotGuard(operand=p[2])

    def p_state_simple(self, p:yacc.Production) -> None:
        'state : STATE NAME NEWLINE'
        p[0] = State(name=p[2], lineno=p.slice[2].lineno)

    def p_state_choice(self, p:yacc.Production) -> None:
        'state : STATE NAME CHOICE NEWLINE'
        p[0] = State(name=p[2], lineno=p.slice[2].lineno, state_type=StateType.CHOICE)

    def p_ignore_line_with_error(self, p:yacc.Production) -> None:
        'ignore : error NEWLINE'
        pass
        
    def p_state_composite(self, p:yacc.Production) -> None:
        '''state : STATE NAME LBRACE NEWLINE state_list RBRACE NEWLINE
                 | STATE NAME LBRACE NEWLINE empty RBRACE NEWLINE'''
        children = p[5] or list()
        composite = len(children) != 0

        p[0] = State(name=p[2], lineno=p.slice[2].lineno, is_composite=composite)
        
        for child in children:
            if child.name == '[*]_Initial':
                p[0].initial_transition = child.initial_transition
            elif child.name == '[*]': # final pseudo state is always at top level
                self.states.append(child)
            else:
                child.parent = p[2]
                self.states.append(child)

    def p_state_with_internal_transition(self, p:yacc.Production) -> None:
        '''state : STATE NAME event_with_optional_guard action NEWLINE'''
        s = State(name=p[2], lineno=p.slice[2].lineno)
        transition = InternalTransition(event=p[3].get('event'), guard=p[3].get('guard'), action=p[4])
        s.internal_transitions.append(transition)
        p[0] = s

    def p_state_with_entry(self, p:yacc.Production) -> None:
        '''state : STATE NAME entry_with_optional_guard action NEWLINE'''
        s = State(name=p[2], lineno=p.slice[2].lineno)
        s.entry = EntryExit(guard=p[3], action=p[4])
        p[0] = s

    def p_state_with_exit(self, p:yacc.Production) -> None:
        '''state : STATE NAME exit_with_optional_guard action NEWLINE'''
        s = State(name=p[2], lineno=p.slice[2].lineno)
        s.exit = EntryExit(guard=p[3], action=p[4])
        p[0] = s

    def p_state_with_internal_transition_without_keyword_state(self, p:yacc.Production) -> None:
        '''state : NAME event_with_optional_guard action NEWLINE
                 | NAME event action NEWLINE'''
        s = State(name=p[1], lineno=p.slice[1].lineno)
        transition = InternalTransition(event=p[2].get('event'), guard=p[2].get('guard'), action=p[3])
        s.internal_transitions.append(transition)
        p[0] = s

    def p_state_with_entry_without_keyword_state(self, p:yacc.Production) -> None:
        '''state : NAME entry_with_optional_guard action NEWLINE'''
        s = State(name=p[1], lineno=p.slice[1].lineno)
        s.entry = EntryExit(guard=p[2], action=p[3])
        p[0] = s

    def p_state_with_exit_without_keyword_state(self, p:yacc.Production) -> None:
        '''state : NAME exit_with_optional_guard action NEWLINE'''
        s = State(name=p[1], lineno=p.slice[1].lineno)
        s.exit = EntryExit(guard=p[2], action=p[3])
        p[0] = s

    def p_empty(self, p:yacc.Production) -> None:
        'empty :'
        pass

    def p_newline(self, p:yacc.Production) -> None:
        'ignore : NEWLINE'
        pass

    def p_error(self, p:yacc.Production) -> None:
        if p is None:
            a = [token.value for token in self.parser.symstack[1:]]
            stack = ' '.join([token.value for token in self.parser.symstack[1:] if token.value is not None])
            self.errors.append('Unexpected end of file')
        elif p.type == 'lexerror':
            self.errors.append('Lexical error: illegal token \'{}\' (hex: {}) of type ({}, {})'.format(p.value, binascii.hexlify(bytes(p.value, 'utf-8')), p.type, p.lineno, p.lexpos))
        else:
            self.errors.append('Syntax error: unexpected token \'{}\' (hex: {}) of type {} ({}, {})'.format(p.value, binascii.hexlify(bytes(p.value, 'utf-8')), p.type, p.lineno, p.lexpos))