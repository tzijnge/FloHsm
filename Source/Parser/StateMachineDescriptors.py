from typing import Set, List, Optional, Any, Dict
from enum import Enum

class Guard(object):
    def to_string(self) -> str:
        assert False, 'Abstract base'

    def guard_conditions(self) -> Set[str]:
        assert False, 'Abstract base'

    def evaluate(self, guard_values:int, bit_index:Dict[str, int] = None) -> bool:
        assert False, 'Abstract base'
    
    def lineno(self) -> int:
        assert False, 'Abstract base'

    @staticmethod
    def generate_bit_index(guard_conditions:Set[str]) -> Dict[str, int]:
        bit_indices = dict()
        index = 0
        sorted_conditions = list(guard_conditions)
        sorted_conditions.sort()
        for c in sorted_conditions:
            bit_indices.update({c : index})
            index += 1

        return bit_indices

    def __eq__(self, other:object) -> bool:
        if isinstance(other, self.__class__):
            return self.to_string() == other.to_string()
        else:
            return False

    def __ne__(self, other:object) -> bool:
        return not self.__eq__(other)

class SimpleGuard(Guard):
    def __init__(self, guard:str, lineno:int):
        self.value = guard
        self.line_number = lineno

    def to_string(self) -> str:
        return self.value

    def guard_conditions(self) -> Set[str]:
        return set([self.value])

    def evaluate(self, guard_values:int, bit_index:Dict[str, int] = None) -> bool:
        bi = bit_index
        if bi is None:
            bi = Guard.generate_bit_index(self.guard_conditions())
         
        return (guard_values & (1 << bi[self.value]) != 0)

    def lineno(self) -> int:
        return self.line_number

class NotGuard(Guard):
    def __init__(self, operand:Guard):
        self.operand = operand

    def to_string(self) -> str:
        guard_expression = '!{}'.format(self.operand.to_string())
        if guard_expression.startswith('!!'):
            guard_expression = guard_expression.lstrip('!')

        return guard_expression

    def guard_conditions(self) -> Set[str]:
        return self.operand.guard_conditions()

    def evaluate(self, guard_values:int, bit_index:Dict[str, int] = None) -> bool:
        bi = bit_index
        if bi is None:
            bi = Guard.generate_bit_index(self.guard_conditions())
        
        return not self.operand.evaluate(guard_values, bi)

    def lineno(self) -> int:
        return self.operand.lineno()

class OrGuard(Guard):
    def __init__(self, operand1:Guard, operand2:Guard):
        self.operands = [operand1, operand2]

    def to_string(self) -> str:
        return '({} || {})'.format(self.operands[0].to_string(), self.operands[1].to_string())

    def guard_conditions(self) -> Set[str]:
        guard_conditions : Set[str] = set()
        guard_conditions = guard_conditions.union(self.operands[0].guard_conditions())
        guard_conditions = guard_conditions.union(self.operands[1].guard_conditions())
        return guard_conditions

    def evaluate(self, guard_values:int, bit_index:Dict[str, int] = None) -> bool:
        bi = bit_index
        if bi is None:
            bi = Guard.generate_bit_index(self.guard_conditions())

        return self.operands[0].evaluate(guard_values, bi) or self.operands[1].evaluate(guard_values, bi)

    def lineno(self) -> int:
        return self.operands[0].lineno()

class AndGuard(Guard):
    def __init__(self, operand1:Guard, operand2:Guard):
        self.operands = [operand1, operand2]

    def to_string(self) -> str:
        return '({} && {})'.format(self.operands[0].to_string(), self.operands[1].to_string())

    def guard_conditions(self) -> Set[str]:
        guard_conditions : Set[str] = set()
        guard_conditions = guard_conditions.union(self.operands[0].guard_conditions())
        guard_conditions = guard_conditions.union(self.operands[1].guard_conditions())
        return guard_conditions

    def evaluate(self, guard_values:int, bit_index:Dict[str, int] = None) -> bool:
        bi = bit_index
        if bi is None:
            bi = Guard.generate_bit_index(self.guard_conditions())

        return self.operands[0].evaluate(guard_values, bi) and self.operands[1].evaluate(guard_values, bi)

    def lineno(self) -> int:
        return self.operands[0].lineno()

class InternalTransition(object):
    def __init__(self, event:str, action:str, guard:Guard=None) -> None:
        self.event = event
        self.action = action
        self.guard = guard

class StateTransition(object):
    def __init__(self, event:str, toState:str, action:str=None, guard:Guard=None) -> None:
        self.toState = toState
        self.event = event
        self.action = action
        self.guard = guard

class InitialTransition(object):
    def __init__(self, toState:str, action:str=None) -> None:
        self.toState = toState
        self.action = action

class ChoiceTransition(object):
    def __init__(self, toState:str, guard:Guard, action:str=None) -> None:
        self.toState = toState
        self.guard = guard
        self.action = action

class EntryExit():
    def __init__(self, action:str, guard:Guard=None):
        self.guard = guard
        self.action = action

    def __eq__(self, other:object) -> bool:
        if isinstance(other, self.__class__):
            return self.guard == other.guard and self.action == other.action
        else:
            return False

class StateType(Enum):
    NORMAL = 0
    CHOICE = 1

class State(object):
    lineno: List[int]
    merge_errors: List[str]
    name: str
    parent: Optional[str]
    initial_transition: InitialTransition
    internal_transitions: List[InternalTransition]
    state_transitions: List[StateTransition]
    choice_transitions: List[ChoiceTransition]

    def __init__(self, name:str, lineno:int, parent:str=None,
                 initial_transition:InitialTransition=None,
                 internal_transitions:List[InternalTransition]=None,
                 state_transitions:List[StateTransition]=None,
                 choice_transitions:List[ChoiceTransition]=None,
                 entry:EntryExit=None, exit:EntryExit=None, is_composite:bool=False,
                 state_type:StateType=StateType.NORMAL):
        self.name = name
        self.parent = parent
        self.initial_transition = initial_transition
        self.internal_transitions = list() if internal_transitions is None else internal_transitions
        self.state_transitions = list() if state_transitions is None else state_transitions
        self.choice_transitions = list() if choice_transitions is None else choice_transitions
        self.entry = entry
        self.exit = exit
        self.is_composite = is_composite
        self.state_type = state_type
        self.lineno = list()
        self.lineno.append(lineno)
        self.merge_errors = list()

    def merge(self, s:'State') -> bool:
        # internal transitions must be merged as sets (wrt to the event). All internal transitions
        # on a common event must have a mutually exclusive guard or equal guard and action
        #
        # state transitions must be merged as sets(wrt to the destination state). All state transitions
        # to a common destination must have
        # - different event
        # or
        # - same event but mutually exclusive guard
        # or
        # - same event and guard and action

        # name
        if self.name != s.name:
            self.merge_errors.append('Unable to merge states with different names ({} and {}). Possibly involved line(s): {}'.format(self.name, s.name, self.lineno + s.lineno))
            return False
        
        if self.state_type == StateType.NORMAL and s.state_type == StateType.CHOICE:
            self.state_type = StateType.CHOICE

        #parent
        if self.parent is None and s.parent is None:
            pass
        elif self.parent is None and s.parent is not None:
            self.parent = s.parent
        elif self.parent is not None and s.parent is None:
            pass
        elif self.parent is not None and s.parent is not None:
            if self.parent != s.parent:
                self.merge_errors.append('Unable to merge different parents {} and {} for state {}. Possibly involved line(s): {}'.format(self.parent, s.parent, self.name, self.lineno + s.lineno))
                return False

        #entry
        if self.entry is not None and s.entry is not None:
            self.merge_errors.append('Unable to merge. Only one entry is allowed for state {}, but detected two. Possibly involved line(s): {})'.format(self.name, self.lineno + s.lineno))
            return False
        elif self.entry is not None and s.entry is None:
            pass
        elif self.entry is None and s.entry is not None:
            self.entry = s.entry
        elif self.entry is None and s.entry is None:
            pass


        #exit
        if self.exit is not None and s.exit is not None:
            self.merge_errors.append('Unable to merge. Only one exit is allowed for state {}, but detected two. Possibly involved line(s): {})'.format(self.name, self.lineno + s.lineno))
            return False
        elif self.exit is not None and s.exit is None:
            pass
        elif self.exit is None and s.exit is not None:
            self.exit = s.exit
        elif self.exit is None and s.exit is None:
            pass

        #initial transition
        if self.initial_transition and s.initial_transition:
            self.merge_errors.append('Unable to merge. Only one initial transition is allowed for state {}, but detected two. Possibly involved line(s): {})'.format(self.name, self.lineno + s.lineno))
            return False

        self.initial_transition = s.initial_transition or self.initial_transition

        #internal transitions
        self.internal_transitions.extend(s.internal_transitions)
        # TODO: detect invalid combinations

        #state transitions
        self.state_transitions.extend(s.state_transitions)
        # TODO: detect invalid combinations

        #choice transitions
        self.choice_transitions.extend(s.choice_transitions)

        #is_composite
        self.is_composite = self.is_composite or s.is_composite
        
        # lineno
        self.lineno.extend(s.lineno)

        return True

    def events(self) -> Set[str]:
        return set([it.event for it in self.internal_transitions] + [st.event for st in self.state_transitions])

    def guards_for_event(self, event:str) -> List[Guard]:
        guards: List[Guard] = list()
        for it in self.internal_transitions:
            if it.guard is not None and it.event == event:
                guards.append(it.guard)

        for st in self.state_transitions:
            if st.guard is not None and st.event == event:
                guards.append(st.guard)

        return guards

    def guard_conditions_for_event(self, event:str) -> Set[str]:
        guard_conditions: Set[str] = set()

        for g in self.guards_for_event(event):
            guard_conditions = guard_conditions.union(g.guard_conditions())

        return guard_conditions

    def internal_transitions_for_event(self, event:str) -> List[InternalTransition]:
        return [it for it in self.internal_transitions if it.event == event]

    def state_transitions_for_event(self, event:str) -> List[StateTransition]:
        return [st for st in self.state_transitions if st.event == event]

    def choice_guard_conditions(self) -> Set[str]:
        guard_conditions: Set[str] = set()

        for ct in self.choice_transitions:
            guard_conditions = guard_conditions.union(ct.guard.guard_conditions())

        return guard_conditions

    def choice_guards(self) -> List[Guard]:
        guards: List[Guard] = list()
        
        for ct in self.choice_transitions:
            guards.append(ct.guard)
        
        return guards