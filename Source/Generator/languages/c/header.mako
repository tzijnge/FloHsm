#ifndef ${desc['file_name'].upper()}_H
#define ${desc['file_name'].upper()}_H

#ifndef __cplusplus
#include <stdbool.h>
#endif

#ifdef __cplusplus
extern "C" {
#endif

typedef void (*${desc['prefix']}Action)(void);
typedef bool (*${desc['prefix']}Guard)(void);

typedef enum
{
% for a in desc['action_names']:
    ${desc['prefix']}Action_${a},
% endfor
} ${desc['prefix']}ActionId;

typedef enum
{
% for g in desc['guard_names']:
    ${desc['prefix']}Guard_${g},
% endfor
} ${desc['prefix']}GuardId;

typedef enum
{
% for n in desc['state_names']:
    ${desc['prefix']}State_${n},
% endfor
} ${desc['prefix']}StateId;

typedef struct
{
    ${desc['prefix']}StateId state;
    ${desc['prefix']}Action actions[5];
    ${desc['prefix']}Guard guards[1];
} ${desc['prefix']}Instance;

const char* ${desc['prefix']}CurrentStateName(const ${desc['prefix']}Instance* instance);

void ${desc['prefix']}InitInstance(${desc['prefix']}Instance* instance);
void ${desc['prefix']}InitAction(${desc['prefix']}Instance* instance, ${desc['prefix']}ActionId actionId, ${desc['prefix']}Action action);
void ${desc['prefix']}InitGuard(${desc['prefix']}Instance* instance, ${desc['prefix']}GuardId guardId, ${desc['prefix']}Guard guard);
void ${desc['prefix']}InitStateMachine(${desc['prefix']}Instance* instance);

% for e in desc['event_names']:
void ${desc['prefix']}_${e}(${desc['prefix']}Instance* instance);
% endfor

#ifdef __cplusplus
}
#endif

#endif