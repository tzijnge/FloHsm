# FloHsm
Code generation tool written in Python for C++ hierarchical state machines.

## Introduction
The basic idea is to design your state machine graphically in PlantUml and then use the PlantUml input file also as an input file for FloHsm.py to generate C++ code. PlantUml can draw states and transitions, but does not have knowledge of basic state machine concepts such as event, actions and guards. A state transition in PlantUml is simply written as
```
State1 --> State2 : comment
```
Here, 'comment' is a free format string that is printed along with the transition arrow in the state diagram. This is fine for a diagram, but in a concrete state machine implementation a state transition must be triggered by an event and it may or may not have an action attached to it. Also, depending on some guard condition, the transition may or may not be performed.

FloHsm has solved this problem by defining additional state machine language elements that are ignored by PlantUml, but shown in the diagram as plain text. Here are some examples of valid FloHsm transitions. Basically everything before the semicolon is standard PlantUml syntax, everything after the semicolon is FloHsm syntax.

Transition triggered by event E1
```
S1 --> S2 : E1
```
Transition triggerd by event E1, but only if boolean guard expression G1 evaluates to true
```
S1 --> S2 : E1 [G1]
```
Transition with action A1, with and without guard
```
S1 --> S2 : E1 / A1
S1 --> S2 : E1 [G1] / A1
```

## Usage
### Generate code
```
python FloHsm.py statemachine.txt
```
See Source/Generated/TestCompositeState for an example. Open the .puml file in plantuml and have a look at the test for using the generated code in C++

For now, FloHsm does not parse the @startuml and @enduml keywords that are required by PlantUml. The solution is to write the state machine description in a text file sm.txt. This file is used for FloHsm. A second file sm.puml only contains the following lines and is used to render the diagram in PlantUml
```
@startuml
!include sm.txt
@enduml
```

### Using the generated state machine
After running FloHsm.py, most of your state machine code is generated, but there are two things that the tool cannot generate. The implementation of the actions and the guards. You need to write them yourself in your state machine class. They are however present in as pure virtual functions in the state machine base class from which your state machine derives, so you just need to override and implement them. You also need to initialize the state machine before use.

In short
- Derive your state machine class from *StateMachineBase*
- Implement al pure virtual functions from *StateMachineBase* (the actions and guards)
- Make sure to call *InitStateMachine()* from your state machine class before using it, e.g. from the constructor or an init method
- Calling the event methods (inherited from *StateMachineBase*, you don't need to do anything here) on your state machine will now cause state transitions, execution of actions, etc...

## Examples
There are a couple of tests that demonstrate most of the FloHsm capabilities. Please find them in ```Source/Generated/Test*```. There is a .puml file for viewing in PlantUml and a .txt file that is used for FloHsm. Generate the state machine files and run the tests. This is as easy as building the project in Visual Studio 2017 and running the test executable. The tests should be easy to compile on other platforms and compilers, but development and testing was only done on Windows with Visual Studio

## Future
More documentation and implementation coming soon. See the issues page for identified open issues
