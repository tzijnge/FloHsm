from os import path
from mako.template import Template

destination_folder = ''
statemachine_name = ''

def generate_source(states, guard_names, action_names, event_names, global_entry):
    template = path.join(path.dirname(path.realpath(__file__)), 'source.mako')
    prefix = statemachine_name[:1].upper() + statemachine_name[1:]
    file_name = statemachine_name
    dest = path.join(destination_folder, file_name + '.c')
        
    transitions_for_event = dict()

    for event in event_names:
        transitions_for_event[event] = dict()
        for state in states:
            for st in state.state_transitions_for_event(event):
                if state.name not in transitions_for_event[event]:
                    transitions_for_event[event][state.name] = dict()

                if st.guard is None:
                    transitions_for_event[event][state.name]['action'] = st.action.name if st.action else None
                    transitions_for_event[event][state.name]['to'] = st.toState
                else:
                    if 'conditions' not in transitions_for_event[event][state.name]:
                        transitions_for_event[event][state.name]['conditions'] = st.guard.guard_conditions()
                    else:
                        transitions_for_event[event][state.name]['conditions'].union(st.guard.guard_conditions())
                    
                    if 'guards' not in transitions_for_event[event][state.name]:
                        transitions_for_event[event][state.name]['guards'] = set()
                        transitions_for_event[event][state.name]['transition'] = dict()

                    transitions_for_event[event][state.name]['guards'].add(st.guard.to_string())

                    if st.guard.to_string() not in transitions_for_event[event][state.name]['transition']:
                        transitions_for_event[event][state.name]['transition'][st.guard.to_string()] = dict()

                    transitions_for_event[event][state.name]['transition'][st.guard.to_string()]['action'] = st.action.name if st.action else None
                    transitions_for_event[event][state.name]['transition'][st.guard.to_string()]['to'] = st.toState

            for it in state.internal_transitions_for_event(event):
                if state.name not in transitions_for_event[event]:
                    transitions_for_event[event][state.name] = dict()

                if it.guard is None:
                    transitions_for_event[event][state.name]['action'] = it.action.name
                    transitions_for_event[event][state.name]['to'] = None
                else:
                    if 'conditions' not in transitions_for_event[event][state.name]:
                        transitions_for_event[event][state.name]['conditions'] = it.guard.guard_conditions()
                    else:
                        transitions_for_event[event][state.name]['conditions'].union(it.guard.guard_conditions())

                    if 'guards' not in transitions_for_event[event][state.name]:
                        transitions_for_event[event][state.name]['guards'] = set()
                        transitions_for_event[event][state.name]['transition'] = dict()

                    transitions_for_event[event][state.name]['guards'].add(it.guard.to_string())

                    if it.guard.to_string() not in transitions_for_event[event][state.name]['transition']:
                        transitions_for_event[event][state.name]['transition'][it.guard.to_string()] = dict()

                    transitions_for_event[event][state.name]['transition'][it.guard.to_string()]['action'] = it.action.name
                    transitions_for_event[event][state.name]['transition'][it.guard.to_string()]['to'] = None

    for state in states:
      if len(state.choice_transitions) != 0:
        if 'AutoTransition' not in transitions_for_event:
          transitions_for_event['AutoTransition'] = dict()

        transitions_for_event['AutoTransition'][state.name] = dict()
        for ct in state.choice_transitions:

          if 'conditions' not in transitions_for_event['AutoTransition'][state.name]:
              transitions_for_event['AutoTransition'][state.name]['conditions'] = ct.guard.guard_conditions()
          else:
              transitions_for_event['AutoTransition'][state.name]['conditions'].union(ct.guard.guard_conditions())
                    
          if 'guards' not in transitions_for_event['AutoTransition'][state.name]:
              transitions_for_event['AutoTransition'][state.name]['guards'] = set()
              transitions_for_event['AutoTransition'][state.name]['transition'] = dict()

          transitions_for_event['AutoTransition'][state.name]['guards'].add(ct.guard.to_string())

          if ct.guard.to_string() not in transitions_for_event['AutoTransition'][state.name]['transition']:
              transitions_for_event['AutoTransition'][state.name]['transition'][ct.guard.to_string()] = dict()

          transitions_for_event['AutoTransition'][state.name]['transition'][ct.guard.to_string()]['action'] = ct.action.name if ct.action else None
          transitions_for_event['AutoTransition'][state.name]['transition'][ct.guard.to_string()]['to'] = ct.toState


    if global_entry.initial_transition.action is not None:
      initial_action = global_entry.initial_transition.action.name
    else:
      initial_action = None

    desc = dict()
    desc['guard_names'] = guard_names
    desc['action_names'] = action_names
    desc['event_names'] = event_names.copy()
    if 'AutoTransition' in transitions_for_event:
        desc['event_names'].add('AutoTransition')
    desc['state_names'] = [s.name for s in states]
    desc['prefix'] = prefix
    desc['file_name'] = file_name
    desc['initial_state'] = global_entry.initial_transition.toState
    desc['initial_action'] = initial_action
    desc['transitions'] = transitions_for_event

    t = Template(filename=template)
    with open(dest, 'w') as f:
        f.write(t.render(desc=desc))

def generate_header(states, guard_names, action_names, event_names):
    template = path.join(path.dirname(path.realpath(__file__)), 'header.mako')
    prefix = statemachine_name[:1].upper() + statemachine_name[1:]
    file_name = statemachine_name
    dest = path.join(destination_folder, file_name + '.h')
    
    desc = dict()
    desc['guard_names'] = guard_names
    desc['action_names'] = action_names
    desc['event_names'] = event_names
    desc['state_names'] = [s.name for s in states]
    desc['prefix'] = prefix
    desc['file_name'] = file_name

    t = Template(filename=template)
    with open(dest, 'w') as f:
        f.write(t.render(desc=desc))

def generate_c(input, settings) -> None:
    global destination_folder
    global statemachine_name
    destination_folder = settings['destination_folder']
    statemachine_name = settings['statemachine_name']

    global_entry = input.state_for_name['FloHsmInitial_5OdpEA31BEcPrWrNx8u7']

    generate_source(input.states, input.guard_names, input.action_names, input.event_names, global_entry)
    generate_header(input.states, input.guard_names, input.action_names, input.event_names)
