import random
from typing import Callable, List

class Generator(object):
    total_items : int
    current_items : int
    current_indent : int
    nested_items : int
    max_nested_items : int
    generate_functions : List[Callable[[], str]] = list()

    def __init__(self) -> None:
        self.total_items = 500
        self.current_items = 0
        self.current_indent = 0
        self.nested_items = 0
        self.max_nested_items = 200
        self.generate_functions = list()

        self.generate_functions.append(self.generate_nested_state)
        self.generate_functions.append(self.generate_simple_state)
        self.generate_functions.append(self.generate_internal_transition_with_event_and_action_using_keyword_state)
        self.generate_functions.append(self.generate_internal_transition_with_event_guard_and_action_using_keyword_state)
        self.generate_functions.append(self.generate_entry_with_action_using_keyword_state)
        self.generate_functions.append(self.generate_entry_with_guard_and_action_using_keyword_state)
        self.generate_functions.append(self.generate_exit_with_action_using_keyword_state)
        self.generate_functions.append(self.generate_exit_with_guard_and_action_using_keyword_state)
        self.generate_functions.append(self.generate_internal_transition_with_event_and_action_without_keyword_state)
        self.generate_functions.append(self.generate_internal_transition_with_event_guard_and_action_without_keyword_state)
        self.generate_functions.append(self.generate_entry_with_action_without_keyword_state)
        self.generate_functions.append(self.generate_entry_with_guard_and_action_without_keyword_state)
        self.generate_functions.append(self.generate_exit_with_action_without_keyword_state)
        self.generate_functions.append(self.generate_exit_with_guard_and_action_without_keyword_state)
        self.generate_functions.append(self.generate_state_transition_with_event)
        self.generate_functions.append(self.generate_state_transition_with_event_and_guard)
        self.generate_functions.append(self.generate_state_transition_with_event_and_action)
        self.generate_functions.append(self.generate_state_transition_with_event_and_guard_and_action)
        self.generate_functions.append(self.generate_initial_state_transition_without_action)
        self.generate_functions.append(self.generate_initial_state_transition_with_action)
        self.generate_functions.append(self.generate_state_transition_to_final_with_event)
        self.generate_functions.append(self.generate_state_transition_to_final_with_event_and_guard)
        self.generate_functions.append(self.generate_state_transition_to_final_with_event_and_action)
        self.generate_functions.append(self.generate_state_transition_to_final_with_event_and_guard_and_action)
        self.generate_functions.append(self.generate_initial_state_transition_to_final_without_action)
        self.generate_functions.append(self.generate_initial_state_transition_to_final_with_action)

    def next_state_name(self) -> str:
        return 'S{}'.format(random.randrange(0, 15))

    def next_event_name(self) -> str:
        return 'E{}'.format(random.randrange(0, 3))

    def next_guard_name(self) -> str:
        return 'G{}'.format(random.randrange(0, 3))

    def next_action_name(self) -> str:
        return 'A{}'.format(random.randrange(0, 3))

    def generate_nested_state(self) -> str:
        desc = 'state {}{{\n'.format(self.next_state_name())
        self.current_indent += 2

        for i in range(0, random.randrange(5)):
            if self.current_items < self.total_items and self.nested_items < self.max_nested_items:
                self.nested_items += 1
                desc += self.generate()
                
        self.current_indent -= 2
        desc += ' ' * self.current_indent
        desc += '}\n'
        return desc

    def generate_simple_state(self) -> str:
        return 'state {}\n'.format(self.next_state_name())

    def generate_internal_transition_with_event_and_action_using_keyword_state(self) -> str:
        return 'state {}: {} / {}\n'.format(self.next_state_name(), self.next_event_name(), self.next_action_name())

    def generate_internal_transition_with_event_guard_and_action_using_keyword_state(self) -> str:
        return 'state {}: {} [{}] / {}\n'.format(self.next_state_name(), self.next_event_name(), self.next_guard_name(), self.next_action_name())

    def generate_entry_with_action_using_keyword_state(self) -> str:
        return 'state {}: entry / {}\n'.format(self.next_state_name(), self.next_action_name())

    def generate_entry_with_guard_and_action_using_keyword_state(self) -> str:
        return 'state {}: entry [{}] / {}\n'.format(self.next_state_name(), self.next_guard_name(), self.next_action_name())

    def generate_exit_with_action_using_keyword_state(self) -> str:
        return 'state {}: exit / {}\n'.format(self.next_state_name(), self.next_action_name())

    def generate_exit_with_guard_and_action_using_keyword_state(self) -> str:
        return 'state {}: exit [{}] / {}\n'.format(self.next_state_name(), self.next_guard_name(), self.next_action_name())

    def generate_internal_transition_with_event_and_action_without_keyword_state(self) -> str:
        return '{}: {} / {}\n'.format(self.next_state_name(), self.next_event_name(), self.next_action_name())

    def generate_internal_transition_with_event_guard_and_action_without_keyword_state(self) -> str:
        return '{}: {} [{}] / {}\n'.format(self.next_state_name(), self.next_event_name(), self.next_guard_name(), self.next_action_name())

    def generate_entry_with_action_without_keyword_state(self) -> str:
        return '{}: entry / {}\n'.format(self.next_state_name(), self.next_action_name())

    def generate_entry_with_guard_and_action_without_keyword_state(self) -> str:
        return '{}: entry [{}] / {}\n'.format(self.next_state_name(), self.next_guard_name(), self.next_action_name())

    def generate_exit_with_action_without_keyword_state(self) -> str:
        return '{}: exit / {}\n'.format(self.next_state_name(), self.next_action_name())

    def generate_exit_with_guard_and_action_without_keyword_state(self) -> str:
        return '{}: exit [{}] / {}\n'.format(self.next_state_name(), self.next_guard_name(), self.next_action_name())

    def generate_state_transition_with_event(self) -> str:
        return '{} --> {} : {}\n'.format(self.next_state_name(), self.next_state_name(), self.next_event_name())

    def generate_state_transition_with_event_and_guard(self) -> str:
        return '{} --> {} : {} [{}]\n'.format(self.next_state_name(), self.next_state_name(), self.next_event_name(), self.next_guard_name())

    def generate_state_transition_with_event_and_action(self) -> str:
        return '{} --> {} : {} / {}\n'.format(self.next_state_name(), self.next_state_name(), self.next_event_name(), self.next_action_name())

    def generate_state_transition_with_event_and_guard_and_action(self) -> str:
        return '{} --> {} : {} [{}] / {}\n'.format(self.next_state_name(), self.next_state_name(), self.next_event_name(), self.next_guard_name(), self.next_guard_name())

    def generate_initial_state_transition_without_action(self) -> str:
        return '[*] --> {}\n'.format(self.next_state_name())

    def generate_initial_state_transition_with_action(self) -> str:
        return '[*] --> {} : {}\n'.format(self.next_state_name(), self.next_action_name())

    def generate_state_transition_to_final_with_event(self) -> str:
        return '{} --> [*] : {}\n'.format(self.next_state_name(), self.next_event_name())

    def generate_state_transition_to_final_with_event_and_guard(self) -> str:
        return '{} --> [*] : {} [{}]\n'.format(self.next_state_name(), self.next_event_name(), self.next_guard_name())

    def generate_state_transition_to_final_with_event_and_action(self) -> str:
        return '{} --> [*] : {} / {}\n'.format(self.next_state_name(), self.next_event_name(), self.next_action_name())

    def generate_state_transition_to_final_with_event_and_guard_and_action(self) -> str:
        return '{} --> [*] : {} [{}] / {}\n'.format(self.next_state_name(), self.next_event_name(), self.next_guard_name(), self.next_action_name())

    def generate_initial_state_transition_to_final_without_action(self) -> str:
        return '[*] --> [*]\n'

    def generate_initial_state_transition_to_final_with_action(self) -> str:
        return '[*] --> [*] : {}\n'.format(self.next_action_name())


    def generate(self) -> str:
        desc = ''

        local_nested_items = self.nested_items

        while self.current_items < self.total_items and self.nested_items < self.max_nested_items:
            self.current_items += 1
            desc += ' ' * self.current_indent
            desc += self.generate_functions[random.randrange(0, len(self.generate_functions))]()
            if local_nested_items == 0:
                self.nested_items = 0
            else:
                self.nested_items += 1

        return desc


if __name__ == '__main__':
    gen = Generator()
    #random.seed(0)
    f = open("generated.txt", "w")
    f.write('@startuml\n')
    description:str = gen.generate()
    f.write(description)
    print(description)
    f.write('@enduml\n')