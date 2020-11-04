// This file was generated with FloHsm. Do not edit.

#include "${desc['file_name']}.h"
#include <assert.h>

static void NullAction(void* a) { (void)a; }
static bool NullGuard(void* g) { (void)g; return false; }

% if 'AutoTransition' in desc['transitions']:
static void ${desc['prefix']}_AutoTransition(${desc['prefix']}Instance* instance);
% endif

const char* ${desc['prefix']}CurrentStateName(const ${desc['prefix']}Instance* instance)
{
    switch (instance->state)
    {
    % for n in desc['state_names']:
    case ${desc['prefix']}State_${n}:
        return "${n}";
    % endfor
    default:
        return "Invalid state ID";
    }
}

void ${desc['prefix']}InitInstance(${desc['prefix']}Instance* instance, void* context)
{
    for (int i = 0; i < ${len(desc['action_names'])}; ++i)
    {
        instance->actions[i] = &NullAction;
    }
    for (int i = 0; i < ${len(desc['guard_names'])}; ++i)
    {
        instance->guards[i] = &NullGuard;
    }
    
    instance->context = context;
}

void ${desc['prefix']}InitAction(${desc['prefix']}Instance* instance, ${desc['prefix']}ActionId actionId, ${desc['prefix']}Action action)
{
    instance->actions[actionId] = action;
}

void ${desc['prefix']}InitGuard(${desc['prefix']}Instance* instance, ${desc['prefix']}GuardId guardId, ${desc['prefix']}Guard guard)
{
    instance->guards[guardId] = guard;
}

void ${desc['prefix']}InitStateMachine(${desc['prefix']}Instance* instance)
{
    for (int i = 0; i < ${len(desc['action_names'])}; ++i)
    {
        assert(instance->actions[i] != &NullAction && "Not all actions initialized");
    }
    for (int i = 0; i < ${len(desc['guard_names'])}; ++i)
    {
        assert(instance->guards[i] != &NullGuard && "Not all guards initialized");
    }
    
    % if desc['initial_action'] is not None:
    instance->actions[${desc['prefix']}Action_${desc['initial_action']}](instance->context);
    % endif
    instance->state = ${desc['prefix']}State_${desc['initial_state']};
}

% for e in desc['event_names']:
void ${desc['prefix']}_${e}(${desc['prefix']}Instance* instance)
{
    % for from_state, tr in desc['transitions'][e].items():
    ${'' if loop.first else 'else '}if (instance->state == ${desc['prefix']}State_${from_state})
    {
        % if 'action' in tr:
        % if tr['action'] is not None:
        instance->actions[${desc['prefix']}Action_${tr['action']}](instance->context);
        % endif
        % if tr['to'] is not None:
        instance->state = ${desc['prefix']}State_${tr['to']};
        % if 'AutoTransition' in desc['transitions']:
        ${desc['prefix']}_AutoTransition(instance);
        % endif
        % endif
        % elif 'conditions' in tr:
        % for c in tr['conditions']:
        const bool ${c} = instance->guards[${desc['prefix']}Guard_${c}](instance->context);
        % endfor
        % for g in tr['guards']:
        ${'' if loop.first else 'else '}if (${g})
        {
            % if tr['transition'][g]['action'] is not None:
            instance->actions[${desc['prefix']}Action_${tr['transition'][g]['action']}](instance->context);
            % endif
            % if tr['transition'][g]['to'] is not None:
            instance->state = ${desc['prefix']}State_${tr['transition'][g]['to']};
            % if 'AutoTransition' in desc['transitions']:
            ${desc['prefix']}_AutoTransition(instance);
            %endif
            % endif
        }
        % endfor
        % endif
    }
    % endfor
}

% endfor
