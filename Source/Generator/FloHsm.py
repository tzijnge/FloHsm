import os
import os.path
import argparse
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Parser'))
from Descriptors import State, StateType, StateTransition, InternalTransition, EntryExit, Action, ActionType
from Parser import FloHsmParser
from SemanticAnalyzer import SemanticAnalyzer
from typing import List, Dict, Set, Any, Optional

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

def generate_event_interface_class(name:str, methods:Set[str]) -> List[str]:
    lines = ['class {}'.format(name),
             '{',
             'public:',
             '    virtual ~{}() {}'.format(name, '{}')]
    lines.extend(['    virtual void {}() {{}}'.format(m) for m in methods])
    lines.append('};')
    return lines

def generate_action_interface_class(name:str, action_prototypes:Set[str]) -> List[str]:
    lines = ['class {}'.format(name),
             '{',
             'public:',
             '    virtual ~{}() {}'.format(name, '{}')]
    lines.extend(['    virtual {} = 0;'.format(ap) for ap in action_prototypes])
    lines.append('};')
    return lines

def generate_guard_interface_class(name:str, methods:Set[str]) -> List[str]:
    lines = ['class {}'.format(name),
             '{',
             'public:',
             '    virtual ~{}() {}'.format(name, '{}')]
    lines.extend(['    virtual bool {}() const = 0;'.format(m) for m in methods])
    lines.append('};')
    return lines

def generate_interfaces(guard_names:Set[str], action_prototypes:Set[str], event_names:Set[str]) -> None:
    file_name = 'Interfaces.hpp'

    with open(os.path.join(destination_folder, file_name), "w") as f:
        lines = ['#pragma once']
        lines.append('')
        lines.append('namespace')
        lines.append('{')
        lines.extend(generate_guard_interface_class('IGuards', guard_names))
        lines.append('')
        lines.extend(generate_action_interface_class('IActions', action_prototypes))
        lines.append('')
        lines.extend(generate_event_interface_class('IEvents', event_names))
        lines.append('')
        lines.append('}')

        f.write('\n'.join(lines))

def generate_state_ids(states:List[State]) -> None:
    file_name = 'StateIds.hpp'

    with open(os.path.join(destination_folder, file_name), "w") as f:
        lines = ['#pragma once',
                 '#include "Hsm/StateId.hpp"',
                 '#include <string>',
                 '#include <map>',
                 '',
                 'namespace',
                 '{',
                 'const uint32_t CompositeStatesRegion = 10;',
                 '']

        composite_state_index = 0
        leaf_state_index: Dict[str, int] = dict()

        for s in states:
            if s.is_composite and s.parent is None:
                lines.append('const StateId StateId_{} = 1 << (CompositeStatesRegion + {});'.format(s.name, composite_state_index))
                composite_state_index += 1
            elif s.is_composite and s.parent is not None:
                lines.append('const StateId StateId_{} = StateId_{} | 1 << (CompositeStatesRegion + {});'.format(s.name, s.parent, composite_state_index))
                composite_state_index += 1
            elif not s.is_composite and s.parent is None:
                if 'TopLevel' not in leaf_state_index:
                    leaf_state_index.update({'TopLevel':1})
                lines.append('const StateId StateId_{} = {};'.format(s.name, leaf_state_index['TopLevel']))
                leaf_state_index['TopLevel'] += 1
            else:
                parent = s.parent
                if parent is not None:
                    if parent not in leaf_state_index:
                        leaf_state_index.update({parent:1})
                    lines.append('const StateId StateId_{} = StateId_{} | {};'.format(s.name, parent, leaf_state_index[parent]))
                    leaf_state_index[parent] += 1


        lines.append('')
        lines.append('const std::map<StateId, std::string> StateNames = ')
        lines.append('{')

        state_names = list()
        for s in states:
            state_names.append('    {{ StateId_{}, "{}" }}'.format(s.name, s.name))

        lines.append(',\n'.join(state_names))
        lines.append('};')
        lines.append('}')

        f.write('\n'.join(lines))

def generate_states(states:List[State]) -> None:
    file_name = 'States.hpp'

    with open(os.path.join(destination_folder, file_name), "w") as f:
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

def generate_statemachine_private(states:List[str]) -> List[str]:
    lines = ['private:',
             '    StateBase* ChangeStateInternal(StateId fromState, StateId toState) override',
             '    {',
             '        const StateId previousStateId = fromState;',
             '',
             '        switch (toState)',
             '        {']

    for s in states:
        s_lines = ['        case StateId_{}:'.format(s),
                   '            currentState = new (stateStorage){}(previousStateId, toState, this, this);'.format(s),
                   '            break;']
        lines.extend(s_lines)

    lines.extend(['        default:',
                  '            break;'
                  '        }',
                  '',
                  '        return currentState;',
                  '    }',
                  '',
                  '    uint8_t stateStorage[1000];'])

    return lines

def generate_statemachine_protected() -> List[str]:
    lines = ['protected:',
             '    StateBase* currentState;',
             '']

    return lines

def generate_statemachine_public(events:Set[str]) -> List[str]:
    lines = ['public:',
             '    StateMachine()',
             '        : currentState(nullptr)',
             '    {}',
             '',
             '    void InitStateMachine()',
             '    {',
             '        ChangeState(StateId_Invalid, StateId_FloHsmInitial_5OdpEA31BEcPrWrNx8u7);',
             '        ChangeStateIfNecessary();',
             '    }',
             '',
             '    StateId CurrentState() const override { return currentState->GetId(); }',
             '']

    for e in events:
        e_lines = ['    void {}() override'.format(e),
                   '    {',
                   '        currentState->{}();'.format(e),
                   '        ChangeStateIfNecessary();',
                   '    }',
                   '']
        lines.extend(e_lines)\

    return lines

def generate_statemachine(states:List[str], events:Set[str]) -> None:
    file_name = 'StateMachine.hpp'

    with open(os.path.join(destination_folder, file_name), "w") as f:
        lines = ['#pragma once',
                 '#include "Interfaces.hpp"',
                 '#include "StateIds.hpp"',
                 '#include "States.hpp"',
                 '#include "Hsm/StateMachineBase.hpp"',
                 '',
                 'namespace',
                 '{',
                 'class StateMachine: public hsm::StateMachineBase, public IEvents, private IActions, public IGuards',
                 '{']
        lines.extend(generate_statemachine_public(events))
        lines.extend(generate_statemachine_protected())
        lines.extend(generate_statemachine_private(states))
        lines.append('};')
        lines.append('}')

        f.write('\n'.join(lines))

def generate(input_file:str) -> None:
    with open(input_file, 'r') as f:
        parser = FloHsmParser()
        parser.parse(f.read())
        if len(parser.errors) != 0:
            for e in parser.errors:
                print (e)
            return

        semantic_analyzer = SemanticAnalyzer()
        semantic_analyzer.analyze(parser.states)
        if len(semantic_analyzer.errors) != 0:
            for e in semantic_analyzer.errors:
                print (e)
            return

        if len(semantic_analyzer.warnings) != 0:
            for w in semantic_analyzer.warnings:
                print (w)
            return
    
    generate_interfaces(semantic_analyzer.guard_names, semantic_analyzer.action_prototypes, semantic_analyzer.event_names)
    generate_state_ids(semantic_analyzer.states)
    generate_states(semantic_analyzer.states)
    generate_statemachine(semantic_analyzer.state_names, semantic_analyzer.event_names)


parser = argparse.ArgumentParser(description='FloHSM generator')
parser.add_argument('files', nargs='+', help='State machine descriptor files')
parser.add_argument('-o', '--outdir', dest='outdir', help='''Output directory to generate files in. If not specified,
files are generated in the same folder as the input file. Output directory will be created if it doesn't exist''')


args = parser.parse_args()

# don't use destination_folder
if args.outdir is None:
    destination_folder = os.path.dirname(os.path.abspath(args.files[0]))
else:
    destination_folder = os.path.abspath(args.outdir)

generate(args.files[0])
