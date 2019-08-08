from Descriptors import State, StateType, Guard, Action
from typing import Set, List, Dict, Optional

class SemanticAnalyzer(object):
    errors : List[str]
    warnings : List[str]
    states : List[State]
    state_names : List[str]
    event_names : Set[str]
    guard_names : Set[str]
    action_prototypes : Set[str]
    state_for_name : Dict[str, State]

    def __init__(self) -> None:
        self.errors = list()
        self.warnings = list()
        self.states = list()
        self.state_names = list()
        self.event_names = set()
        self.guard_names = set()
        self.action_prototypes = set()
        self.state_for_name = dict()

    def remove_reachable_states(self, reachable_root:State, possibly_unreachable_states:List[str]) -> None:
        if reachable_root.name in possibly_unreachable_states:
            possibly_unreachable_states.remove(reachable_root.name)

        if len(possibly_unreachable_states) == 0:
            return

        reachable_states:List[str] = list()
        
        reachable : Optional[State] = reachable_root
        while reachable is not None:
            # Break on recursion
            if reachable.name in reachable_states:
                break

            # Append current state
            if reachable.name in possibly_unreachable_states:
                reachable_states.append(reachable.name)
            
            # Append current state's initial transition
            if reachable.initial_transition is not None and reachable.initial_transition.toState in possibly_unreachable_states:
                reachable_states.append(reachable.initial_transition.toState)

            # Append current state's state transitions
            reachable_states.extend([stateName.toState for stateName in reachable.state_transitions if stateName.toState in possibly_unreachable_states])

            # TODO: unit test
            # Append choice pseudo state's transitions
            reachable_states.extend([stateName.toState for stateName in reachable.choice_transitions if stateName.toState in possibly_unreachable_states])

            # Up one level in the state hierarchy
            if reachable.parent is not None:
                reachable = self.state_for_name[reachable.parent]
            else:
                reachable = None
        
        
        for stateName in reachable_states:
            self.remove_reachable_states(self.state_for_name[stateName], possibly_unreachable_states)

    def analyze_guard_expressions_always_true_or_false(self) -> None:
        guards = list()
        for state in self.states:
            if state.entry and state.entry.guard:
                guards.append(state.entry.guard)
            if state.exit and state.exit.guard:
                guards.append(state.exit.guard)

            for event in state.events():
                guards.extend(state.guards_for_event(event))
                
        for guard in guards:
            expression_always_true = True
            expression_never_true = True
                    
            for i in range(0, 2**(len(guard.guard_conditions()))):
                result = guard.evaluate(i)
                expression_always_true = expression_always_true and result
                expression_never_true = expression_never_true and not result

            if expression_always_true:
                self.warnings.append('Guard expression {} (State {}, line {}) always evaluates to true'.format(guard.to_string(), state.name, guard.lineno()))

            if expression_never_true:
                self.warnings.append('Guard expression {} (State {}, line {}) always evaluates to false'.format(guard.to_string(), state.name, guard.lineno()))

    def detect_ambiguous_transitions(self) -> None:
        for state in self.states:
            for event in state.events():
                guard_conditions = state.guard_conditions_for_event(event)
                guards = state.guards_for_event(event)

                bit_index = Guard.generate_bit_index(guard_conditions)

                for i in range(0, 2**(len(guard_conditions))):
                    positive_guards = list()
                    for g in guards:
                        if g.evaluate(i, bit_index):
                            positive_guards.append(g)

                    if len(positive_guards) > 1:
                        offending_conditions = list(guard_conditions)
                        offending_conditions.sort()

                        error_message = 'Ambiguous transition for event {} in {}: Guard expressions '.format(event, state.name)
                        error_message += ' and '.join([g.to_string() for g in positive_guards])
                        error_message += ' evaluate to true when '
                        conditions = list()
                        for oc in offending_conditions:
                            conditions.append('{}=={}'.format(oc, str(i & (1 << bit_index[oc]) != 0).lower()))

                        error_message += ' and '.join(conditions)
                        error_message += '. See lines '
                        error_message += ' and '.join([str(g.lineno()) for g in positive_guards])

                        self.errors.append(error_message)
                        break # TODO: remove break

    def detect_ambiguous_choice_transitions(self) -> None:
        for state in [s for s in self.states if s.state_type == StateType.CHOICE]:
            guard_conditions = state.choice_guard_conditions()
            guards = state.choice_guards()

            bit_index = Guard.generate_bit_index(guard_conditions)

            for i in range(0, 2**(len(guard_conditions))):
                positive_guards = list()
                for g in guards:
                    if g.evaluate(i, bit_index):
                        positive_guards.append(g)

                if len(positive_guards) > 1:
                    offending_conditions = list(guard_conditions)
                    offending_conditions.sort()

                    error_message = 'Ambiguous outgoing transition for choice pseudo state {}: Guard expressions '.format(state.name)
                    error_message += ' and '.join([g.to_string() for g in positive_guards])
                    error_message += ' evaluate to true when '
                    conditions = list()
                    for oc in offending_conditions:
                        conditions.append('{}=={}'.format(oc, str(i & (1 << bit_index[oc]) != 0).lower()))

                    error_message += ' and '.join(conditions)
                    error_message += '. See lines '
                    error_message += ' and '.join([str(g.lineno()) for g in positive_guards])

                    self.errors.append(error_message)
                elif len(positive_guards) == 0 and len(guards) > 1:
                    offending_conditions = list(guard_conditions)
                    offending_conditions.sort()

                    error_message = 'No outgoing transition for choice pseudo state {}: Guard expressions '.format(state.name)
                    error_message += ' and '.join([g.to_string() for g in guards])
                    error_message += ' evaluate to false when '
                    conditions = list()
                    for oc in offending_conditions:
                        conditions.append('{}=={}'.format(oc, str(i & (1 << bit_index[oc]) != 0).lower()))

                    error_message += ' and '.join(conditions)
                    error_message += '. See lines '
                    error_message += ' and '.join([str(g.lineno()) for g in guards])

                    self.errors.append(error_message)


    def analyze(self, states:List[State]) -> None:
        # merge states
        for state in states:
            current_states = [s for s in self.states if s.name == state.name]
            assert(len(current_states) < 2)

            if len(current_states) == 0:
                self.states.append(state)
                self.state_for_name[state.name] = state
            else:
                success = current_states[0].merge(state)
                if not success:
                    self.errors.extend(current_states[0].merge_errors)

        # sort states
        levels:List[List[State]] = list()
        levels.append(list())
        numberStates = len(self.states)
        numberSortedStates = 0

        for state in self.states:
            if state.parent is None:
                levels[-1].append(state)
                numberSortedStates += 1

        number_iterations = 0
        while numberSortedStates != numberStates and number_iterations != numberStates:
            number_iterations += 1
            levels.append(list())
            for state in self.states:
                if state.parent in [s.name for s in levels[-2]]:
                    levels[-1].append(state)
                    numberSortedStates += 1

        if number_iterations == numberStates:
            self.errors.append('Failed to sort states hierarchically. Continue with unsorted states.')
        else:
            self.states.clear()
            for level in levels:
                for state in level:
                    self.states.append(state)

        for state in self.states:
            if state.state_type == StateType.CHOICE:
                line_numbers = [str(l) for l in state.lineno]
                if state.entry is not None:
                    self.errors.append('A choice pseudo state cannot have an entry. See line(s) {}'.format(' and '.join(line_numbers)))

                if state.exit is not None:
                    self.errors.append('A choice pseudo state cannot have an exit. See line(s) {}'.format(' and '.join(line_numbers)))

                if len(state.internal_transitions) != 0:
                    self.errors.append('A choice pseudo state cannot have any internal transitions. See line(s) {}'.format(' and '.join(line_numbers)))

                if len(state.state_transitions) != 0:
                    self.errors.append('A choice pseudo state cannot have any state transitions. See line(s) {}'.format(' and '.join(line_numbers)))

                if len(state.choice_transitions) < 2:
                    self.errors.append('A choice pseudo state must have at least two outgoing transitions. See line(s) {}'.format(' and '.join(line_numbers)))


        # Create list of state names, list of events, list of guards, list of action prototypes
        actions: List[Action] = list()

        for state in self.states:
            self.state_names.append(state.name)
            
            initial_transition = state.initial_transition;
            if initial_transition is not None:
                action = initial_transition.action
                if action is not None:
                    actions.append(action)

            for st in state.state_transitions:
                self.event_names.add(st.event)
                if st.guard is not None:
                    self.guard_names.update(st.guard.guard_conditions())
                if st.action is not None:
                    actions.append(st.action)

            for it in state.internal_transitions:
                self.event_names.add(it.event)
                if it.guard is not None:
                    self.guard_names.update(it.guard.guard_conditions())
                if it.action is not None:
                    actions.append(it.action)

            for ct in state.choice_transitions:
                self.guard_names.update(ct.guard.guard_conditions())
                if ct.action is not None:
                    actions.append(ct.action)

            if state.entry is not None:
                actions.append(state.entry.action)
                if state.entry.guard is not None:
                    self.guard_names.update(state.entry.guard.guard_conditions())

            if state.exit is not None:
                actions.append(state.exit.action)
                if state.exit.guard is not None:
                    self.guard_names.update(state.exit.guard.guard_conditions())

        for a in actions:
            self.action_prototypes.add(a.prototype_string())

        action_names = [action.name for action in actions]

        for s in self.state_names:
            if s in self.event_names:
                self.errors.append('State name \'{}\' is also used as event name'.format(s))
            if s in self.guard_names:
                self.errors.append('State name \'{}\' is also used as guard name'.format(s))
            if s in action_names:
                self.errors.append('State name \'{}\' is also used as action name'.format(s))

        for e in self.event_names:
            if e in self.guard_names:
                self.errors.append('Event name \'{}\' is also used as guard name'.format(e))
            if e in action_names:
                self.errors.append('Event name \'{}\' is also used as action name'.format(e))

        for guard in self.guard_names:
            if guard in action_names:
                self.errors.append('Guard name \'{}\' is also used as action name'.format(guard))

        self.analyze_guard_expressions_always_true_or_false()
        self.detect_ambiguous_transitions()
        self.detect_ambiguous_choice_transitions()

        # find inheritance conflicts
        for name, state in self.state_for_name.items():
            current_name = name
            while self.state_for_name[current_name].parent is not None:
                if self.state_for_name[current_name].parent == name:
                    self.errors.append('Detected circular inheritance for state {} on line(s) {}'.format(name, self.state_for_name[current_name].lineno))
                    break
                else:
                    parent = self.state_for_name[current_name].parent 
                    if parent is not None:
                        current_name = parent
                        if current_name not in self.state_for_name:
                            self.errors.append('Detected unknown state \'{}\' at line(s) {}'.format(current_name, self.state_for_name[name].lineno))
                            break

        if 'FloHsmInitial_5OdpEA31BEcPrWrNx8u7' not in self.state_names:
            self.errors.append('No top-level initial transition found')
        else:
            possibly_unreachable_states = self.state_names.copy()
            self.remove_reachable_states(self.state_for_name['FloHsmInitial_5OdpEA31BEcPrWrNx8u7'], possibly_unreachable_states)

            for s in possibly_unreachable_states:
                self.errors.append('State \'{}\' (line(s) {}) is not reachable'.format(s, self.state_for_name[s].lineno))