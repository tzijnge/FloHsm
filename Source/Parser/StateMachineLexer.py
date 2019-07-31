import ply.lex as lex
from typing import List

TestData= '''
@startuml

state MyState1{
}

state choice1 <<choice>>

[*] --> S : InitialAction

S : entry / EntryAction
S : exit / ExitAction
S : E1 / A1
S : E4 [G1] / A4
S : E5 [G2] / A5
S : E5 [!G2] / A6

S --> S : E2 / A2
S --> [*] : E3 / A3

@enduml
'''

class StateMachineLexer(object):
    finalTokens : List[str]

    def __init__(self) -> None:
        self.lexer = lex.lex(module=self, debug=False)
        self.finalTokens = list()
        self.finalTokens.append('\n') # final newline to make sure that statements at end of file are also correctly parsed (syntax requires newline after every statement)
            
    def token(self) -> lex.Token:
        t = self.lexer.token()
        return t

    def input(self, s:str) -> None:
        self.lexer.input(s)

    reserved = {
        'state' : 'STATE'
        }

    tokens = [
        'LBRACE',
        'RBRACE',
        'LBRACKET',
        'RBRACKET',
        'LPAREN',
        'RPAREN',
        'COLON',
        'FORWARD_SLASH',
        'NOT',
        'AND',
        'OR',
        'DOUBLE_QUOTE',
        'NAME',
        'STATE_INITIAL_OR_FINAL',
        'CHOICE',
        'ENTRY',
        'EXIT',
        'TRANSITION',
        'INT',
        #'PLANT_UML_START_MARKER',
        #'PLANT_UML_END_MARKER'
        'NEWLINE'
        ] + list(reserved.values())

    t_LBRACE = r'{'
    t_RBRACE = r'}'
    t_LBRACKET = r'\['
    t_RBRACKET = r'\]'
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_COLON = r':'
    t_NOT = r'!'
    t_AND = r'&'
    t_OR = r'\|'
    t_DOUBLE_QUOTE = r'"'
    t_FORWARD_SLASH = r'/'
    t_STATE_INITIAL_OR_FINAL = r'\[[*]\]' # matches '[*]'
    t_CHOICE = r'<<choice>>'
    t_ENTRY = r'<<entry>>'
    t_EXIT = r'<<exit>>'
    t_TRANSITION = r'-->'
    #t_PLANT_UML_START_MARKER = r'@startuml.*' # '@startuml. Everything after it on same line is ignored and included in token'
    #t_PLANT_UML_END_MARKER = r'@enduml.*' # '@enduml. Everything after it on same line is ignored and included in token'
        
    t_ignore = ' \t'

    def t_newline(self,t:lex.Token) -> lex.Token:
        r'\n+'
        t.lexer.lineno += len(t.value)
        t.type = 'NEWLINE'
        return t

    def t_eof(self, t:lex.Token) -> lex.Token:
        if len(self.finalTokens) == 0:
            return None
        else:
            self.lexer.input(self.finalTokens.pop(0))
            return self.lexer.token()

    def t_error(self, t:lex.Token) -> lex.Token:
        t.lexer.skip(1)
        t.value = t.value[0].split(' ')[0]
        t.type = 'lexerror'
        return t

    def t_NAME(self, t:lex.Token) -> lex.Token:
        r'[a-zA-Z_][a-zA-Z0-9_]*'
        if t.value in self.reserved:
            t.type = self.reserved[ t.value ]
        return t

    def t_INT(self, t:lex.Token) -> lex.Token:
        r'(?P<sign>[-+]?)(?P<value>(?P<hex>0[xX][0-9a-fA-F]+)|(?P<dec>[0-9]+))'
        return t

#lexer = lex.lex(debug=0)

#lexer.input(TestData)

#for tok in lexer:
#    print(tok)
