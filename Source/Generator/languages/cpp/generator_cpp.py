from os import path
from Descriptors import State, StateType, StateTransition, InternalTransition, EntryExit, Action, ActionType
from typing import List, Dict, Set, Any, Optional
import pathlib
from mako.template import Template

class StateWriter(object):
    lines: List[str]
    if_condition: str
    if_body: List[str]

    def __init__(self) -> None:
        self.lines = list()
        self.__indent = 0
        self.if_body = []

    def __enter__(self) -> None:
        self.indent_and_append('{')
        self.indent()

    def __exit__(self, type:Any, value:Any, traceback:Any) -> None:
        self.unindent()
        self.indent_and_append('}')

    def code_block(self) -> 'StateWriter':
        return self

    def if_block(self, condition:str) -> 'StateWriter':
        self.indent_and_append('if ({})'.format(condition))
        return self

    def namespace_block(self, name:str=None) -> 'StateWriter':
        self.indent_and_append('namespace {}'.format(name if name else ''))
        return self;

    def indent(self) -> None:
        self.__indent += 4

    def unindent(self) -> None:
        self.__indent -= 4

    def indent_and_append(self, s:str) -> None:
        self.lines.append(' ' * self.__indent + s)

    def write_if_statement(self, condition:str, body:List[str]) -> None:
        with self.if_block(condition):
            for body_line in body:
                self.indent_and_append(body_line)

    def write_transition_details(self, to_state:str, action:Optional[Action]) -> None:
        action_str:str = ''
        if action is None:
            action_str ='Function()'
        elif action.type == ActionType.NONE:
            action_str = 'Function(&IActions::{}, actions)'.format(action.name)
        else:
            action_str = 'Function(&IActions::{}, actions, {})'.format(action.name, action.value())

        self.indent_and_append('SetTransitionDetails(StateId_{}, {});'.format(to_state, action_str))

    def write_constructor_body(self, state:State) -> None:
        with self.code_block():
            with self.if_block('MustCallEntry(Id, fromState, toState)'):
                if state.entry is not None:
                    if state.entry.guard is not None:
                        for g in state.entry.guard.guard_conditions():
                            self.indent_and_append('const bool {} = guards->{}();'.format(g, g))

                if state.entry is not None:
                    if state.entry.guard is not None:                    
                        self.write_if_statement(state.entry.guard.to_string(), ['actions->{};'.format(state.entry.action.invocation_string())])
                    else:
                        self.indent_and_append('actions->{};'.format(state.entry.action.invocation_string()))

                it = state.initial_transition
                if it is not None:
                    self.write_transition_details(it.toState, it.action)

    def write_choice_constructor(self, state:State) -> None:
        with self.code_block():
            for g in state.choice_guard_conditions():
                self.indent_and_append('const bool {} = guards->{}();'.format(g, g))

            for ct in state.choice_transitions:
                with self.if_block(ct.guard.to_string()):
                    self.write_transition_details(ct.toState, ct.action)

    def write_constructor(self, state:State) -> None:
        if state.parent or state.entry or state.initial_transition:
            self.indent_and_append('{}(StateId fromState, StateId toState, IActions* _actions, IGuards* _guards)'.format(state.name))
        else:
            self.indent_and_append('{}(StateId, StateId, IActions* _actions, IGuards* _guards)'.format(state.name))

        if state.parent is not None:
            self.indent_and_append('    : {}(fromState, toState, _actions, _guards)'.format(state.parent))
        else:
            self.indent_and_append('    : StateBase(_actions, _guards)')

        if state.state_type == StateType.CHOICE:
            self.write_choice_constructor(state)
        elif state.entry is None and state.initial_transition is None:
            self.indent_and_append('{}')
        else:
            self.write_constructor_body(state)

    def write_destructor_body(self, exit:EntryExit) -> None:
        with self.code_block():
            with self.if_block('MustCallExit(Id)'):
                if exit.guard is not None:
                    for g in exit.guard.guard_conditions():
                        self.indent_and_append('const bool {} = guards->{}();'.format(g, g))

                if exit.guard is not None:
                    self.write_if_statement(exit.guard.to_string(), ['actions->{};'.format(exit.action.invocation_string())])
                else:
                    self.indent_and_append('actions->{};'.format(exit.action.invocation_string()))

    def write_destructor(self, state:State) -> None:
        self.indent_and_append('virtual ~{}()'.format(state.name))
        
        if state.exit is None:
            self.indent_and_append('{}')
        else:
            self.write_destructor_body(state.exit)

    def write_state_transition(self, st:StateTransition) -> None:
        if st.guard is not None:
            with self.if_block(st.guard.to_string()):
                self.write_transition_details(st.toState, st.action)
        else:
            self.write_transition_details(st.toState, st.action)

    def write_internal_transition(self, it:InternalTransition) -> None:
        action = 'actions->{};'.format(it.action.invocation_string())

        if it.guard is not None:
            with self.if_block(it.guard.to_string()):
                self.indent_and_append(action)
        else:
            self.indent_and_append(action)

    def write_event_method(self, event:str, state:State) -> None:
        self.indent_and_append('void {}() override'.format(event))
        with self.code_block():
            for g in state.guard_conditions_for_event(event):
                self.indent_and_append('const bool {} = guards->{}();'.format(g, g))

            for st in state.state_transitions_for_event(event):
                self.write_state_transition(st)

            for it in state.internal_transitions_for_event(event):
                self.write_internal_transition(it)

    def write_methods(self, state:State) -> None:
        self.write_constructor(state)
        self.lines.append('')
        self.write_destructor(state)
        self.lines.append('')

        for e in state.events():
            self.write_event_method(e, state)
            self.lines.append('')

    def write_id(self, state:State) -> None:
        self.indent_and_append('StateId GetId() const override { return Id; }')
        self.indent_and_append('')
        self.unindent()
        self.indent_and_append('private:')
        self.indent()
        self.indent_and_append('static const StateId Id = StateId_{};'.format(state.name))
        self.lines.append('')

    def write(self, state:State) -> List[str]:
        self.indent_and_append('class {} : public {}'.format(state.name, state.parent if state.parent is not None else 'StateBase'))
        self.indent_and_append('{')
        self.indent_and_append('public:')
        self.indent()
        self.write_methods(state)
        self.write_id(state)
        self.unindent()
        self.indent_and_append('};')

        return self.lines



destination_folder:str

def generate_file(file_name, context):
    generate_dir = pathlib.Path(__file__).parent.absolute()
    template_file = path.join(generate_dir, file_name + '.template')
    template = Template(filename = template_file)

    with open(path.join(destination_folder, file_name), "w") as f:
        f.write(template.render(**context))

def generate_interfaces(guard_names:Set[str], action_prototypes:Set[str], event_names:Set[str]) -> None:
    context = \
      {\
       'guard_names' : guard_names,\
       'action_prototypes' : action_prototypes,\
       'event_names' : event_names,\
      }

    generate_file('Interfaces.hpp', context)

def generate_state_ids(states:List[State]) -> None:
    composite_state_index = 0
    leaf_state_index: Dict[str, int] = dict()
    state_ids: Dict[str, str] = dict()

    for s in states:
        if s.is_composite and s.parent is None:
            state_ids[s.name] = '1 << (CompositeStatesRegion + {})'.format(composite_state_index)
            composite_state_index += 1
        elif s.is_composite and s.parent is not None:
            state_ids[s.name] = 'StateId_{} | 1 << (CompositeStatesRegion + {})'.format(s.parent, composite_state_index)
            composite_state_index += 1
        elif not s.is_composite and s.parent is None:
            if 'TopLevel' not in leaf_state_index:
                leaf_state_index.update({'TopLevel':1})
            state_ids[s.name] = '{}'.format(leaf_state_index['TopLevel'])
            leaf_state_index['TopLevel'] += 1
        else:
            parent = s.parent
            if parent is not None:
                if parent not in leaf_state_index:
                    leaf_state_index.update({parent:1})
                state_ids[s.name] = 'StateId_{} | {}'.format(parent, leaf_state_index[parent])
                leaf_state_index[parent] += 1

    context = \
      {\
        'states' : states,\
        'state_ids' : state_ids,\
      }

    generate_file('StateIds.hpp', context)

def generate_states(states:List[State]) -> None:
    file_name = 'States.hpp'

    with open(path.join(destination_folder, file_name), "w") as f:
        lines = ['#pragma once',
                 '#include "Interfaces.hpp"',
                 '#include "StateIds.hpp"',
                 '#include "Hsm/StateMachineBase.hpp"',
                 '#include "Hsm/Function.hpp"',
                 '',
                 'namespace',
                 '{',
                 'class StateBase : public hsm::StateBase, public IEvents',
                 '{',
                 'public:',
                 '    StateBase(IActions* _actions, IGuards* _guards)',
                 '        : actions(_actions)',
                 '        , guards(_guards)',
                 '    {}',
                 '',
                 '    virtual ~StateBase(){}',
                 '',
                 'protected:',
                 '    IActions* actions;',
                 '    IGuards* guards;',
                 '};',
                 '']

        for s in states:
            state_writer = StateWriter()
            lines.extend(state_writer.write(s))
            lines.append('')

        lines.append('}')

        f.write('\n'.join(lines))

def generate_statemachine(states:List[str], events:Set[str]) -> None:
    context = \
      {\
        'states' : states,\
        'events' : events,\
      }

    generate_file('StateMachine.hpp', context)

def generate_cpp(input, settings) -> None:
    global destination_folder
    destination_folder = settings['destination_folder']

    generate_interfaces(input.guard_names, input.action_prototypes, input.event_names)
    generate_state_ids(input.states)
    generate_states(input.states)
    generate_statemachine(input.state_names, input.event_names)
