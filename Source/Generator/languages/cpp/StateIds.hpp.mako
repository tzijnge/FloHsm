#pragma once
#include "Hsm/StateId.hpp"
#include <string>
#include <map>

namespace
{
const uint32_t CompositeStatesRegion = 10;

% for s in states:
const StateId StateId_${s.name} = ${state_ids[s.name]};
% endfor

const std::map<StateId, std::string> StateNames = 
{
    % for s in states:
    { StateId_${s.name}, "${s.name}" },
    % endfor
};
}