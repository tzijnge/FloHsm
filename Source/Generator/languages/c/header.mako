// This file was generated with FloHsm. Do not edit.

#ifndef ${desc['include_guard']}
#define ${desc['include_guard']}

#ifndef __cplusplus
#include <stdbool.h>
#endif

#ifdef __cplusplus
extern "C" {
#endif

typedef void (*${desc['prefix']}Action)(void*);
typedef bool (*${desc['prefix']}Guard)(void*);

% if len(desc['action_names']) != 0:
typedef enum
{
% for a in desc['action_names']:
    ${desc['prefix']}Action_${a},
% endfor
} ${desc['prefix']}ActionId;
% endif

% if len(desc['guard_names']) != 0:
typedef enum
{
% for g in desc['guard_names']:
    ${desc['prefix']}Guard_${g},
% endfor
} ${desc['prefix']}GuardId;
% endif

typedef enum
{
% for n in desc['state_names']:
    ${desc['prefix']}State_${n},
% endfor
} ${desc['prefix']}StateId;

typedef struct
{
    ${desc['prefix']}StateId state;
    % if len(desc['action_names']) != 0:
    ${desc['prefix']}Action actions[${len(desc['action_names'])}];
    % endif
    % if len(desc['guard_names']) != 0:
    ${desc['prefix']}Guard guards[${len(desc['guard_names'])}];
    % endif
    void* context;
} ${desc['prefix']}Instance;

const char* ${desc['prefix']}CurrentStateName(const ${desc['prefix']}Instance* instance);

void ${desc['prefix']}InitInstance(${desc['prefix']}Instance* instance, void* context);
% if len(desc['action_names']) != 0:
void ${desc['prefix']}InitAction(${desc['prefix']}Instance* instance, ${desc['prefix']}ActionId actionId, ${desc['prefix']}Action action);
% endif
% if len(desc['guard_names']) != 0:
void ${desc['prefix']}InitGuard(${desc['prefix']}Instance* instance, ${desc['prefix']}GuardId guardId, ${desc['prefix']}Guard guard);
% endif
void ${desc['prefix']}InitStateMachine(${desc['prefix']}Instance* instance);

% for e in desc['event_names']:
void ${desc['prefix']}_${e}(${desc['prefix']}Instance* instance);
% endfor

#ifdef __cplusplus
}
#endif

#endif