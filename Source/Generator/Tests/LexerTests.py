﻿import unittest
from Lexer import FloHsmLexer
import ply.lex as lex

class LexerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.lexer = FloHsmLexer()

    def tearDown(self) -> None:
        self.assertToken(self.lexer.token(), 'NEWLINE', '\n')
        self.assertEqual(self.lexer.token(), None)

    def assertToken(self, actual:lex.Token, expectedType:str, expectedValue:str) -> None:
        self.assertEqual(actual.type, expectedType)
        self.assertEqual(actual.value, expectedValue)

    def test_InitialState(self) -> None:
        # actual test in teardown
        pass

    def test_EmptyInput(self) -> None:
        self.lexer.input('')       

    def test_SpacesAndTabsAreIgnored(self) -> None:
        self.lexer.input('  \t    \t')

    def test_State(self) -> None:
        self.lexer.input('state State STATE')
        self.assertToken(self.lexer.token(), 'STATE', 'state')
        self.assertToken(self.lexer.token(), 'STATE', 'state')
        self.assertToken(self.lexer.token(), 'STATE', 'state')

    def test_entry(self) -> None:
        self.lexer.input('<<entry>>')
        self.assertToken(self.lexer.token(), 'ENTRY', '<<entry>>')

    def test_exit(self) -> None:
        self.lexer.input('<<exit>>')
        self.assertToken(self.lexer.token(), 'EXIT', '<<exit>>')

    def test_choice(self) -> None:
        self.lexer.input('<<choice>>')
        self.assertToken(self.lexer.token(), 'CHOICE', '<<choice>>')

    def test_LBrace(self) -> None:
        self.lexer.input('{')
        self.assertToken(self.lexer.token(), 'LBRACE', '{')

    def test_RBrace(self) -> None:
        self.lexer.input('}')
        self.assertToken(self.lexer.token(), 'RBRACE', '}')

    def test_LBracket(self) -> None:
        self.lexer.input('[')
        self.assertToken(self.lexer.token(), 'LBRACKET', '[')

    def test_RBracket(self) -> None:
        self.lexer.input(']')
        self.assertToken(self.lexer.token(), 'RBRACKET', ']')

    def test_LParen(self) -> None:
        self.lexer.input('(')
        self.assertToken(self.lexer.token(), 'LPAREN', '(')

    def test_RParen(self) -> None:
        self.lexer.input(')')
        self.assertToken(self.lexer.token(), 'RPAREN', ')')

    def test_Colon(self) -> None:
        self.lexer.input(':')
        self.assertToken(self.lexer.token(), 'COLON', ':')

    def test_ForwardSlash(self) -> None:
        self.lexer.input('/')
        self.assertToken(self.lexer.token(), 'FORWARD_SLASH', '/')

    def test_Not(self) -> None:
        self.lexer.input('!')
        self.assertToken(self.lexer.token(), 'NOT', '!')

    def test_And(self) -> None:
        self.lexer.input('&')
        self.assertToken(self.lexer.token(), 'AND', '&')

    def test_Or(self) -> None:
        self.lexer.input('|')
        self.assertToken(self.lexer.token(), 'OR', '|')

    def test_Integer(self) -> None:
        self.lexer.input('111-222+333')
        self.assertToken(self.lexer.token(), 'INT', '111')
        self.assertToken(self.lexer.token(), 'INT', '-222')
        self.assertToken(self.lexer.token(), 'INT', '+333')

    def test_IntegerHex(self) -> None:
        self.lexer.input('0xAB 0X6D -0x11 +0x4f')

        self.assertToken(self.lexer.token(), 'INT', '0xAB')
        self.assertToken(self.lexer.token(), 'INT', '0X6D')
        self.assertToken(self.lexer.token(), 'INT', '-0x11')
        self.assertToken(self.lexer.token(), 'INT', '+0x4f')

    def test_Bool(self) -> None:
        self.lexer.input('true false True False tRuE FaLSe')

        self.assertToken(self.lexer.token(), 'TRUE', 'true')
        self.assertToken(self.lexer.token(), 'FALSE', 'false')
        self.assertToken(self.lexer.token(), 'TRUE', 'true')
        self.assertToken(self.lexer.token(), 'FALSE', 'false')
        self.assertToken(self.lexer.token(), 'TRUE', 'true')
        self.assertToken(self.lexer.token(), 'FALSE', 'false')

    def test_Float(self) -> None:
        self.lexer.input('.123 12.34 -1.123 +1.23 12. 1.e2 2.E4 -1.5e+1 +2.3E-9 .44e7')

        self.assertToken(self.lexer.token(), 'FLOAT', '.123')
        self.assertToken(self.lexer.token(), 'FLOAT', '12.34')
        self.assertToken(self.lexer.token(), 'FLOAT', '-1.123')
        self.assertToken(self.lexer.token(), 'FLOAT', '+1.23')
        self.assertToken(self.lexer.token(), 'FLOAT', '12.')
        self.assertToken(self.lexer.token(), 'FLOAT', '1.e2')
        self.assertToken(self.lexer.token(), 'FLOAT', '2.E4')
        self.assertToken(self.lexer.token(), 'FLOAT', '-1.5e+1')
        self.assertToken(self.lexer.token(), 'FLOAT', '+2.3E-9')
        self.assertToken(self.lexer.token(), 'FLOAT', '.44e7')

    def test_String(self) -> None:
        self.lexer.input(r'"Test123:\n \"FloHSM\"" "state" "true" "<<choice>>" ""')

        self.assertToken(self.lexer.token(), 'STRING', r'"Test123:\n \"FloHSM\""')
        self.assertToken(self.lexer.token(), 'STRING', r'"state"')
        self.assertToken(self.lexer.token(), 'STRING', r'"true"')
        self.assertToken(self.lexer.token(), 'STRING', r'"<<choice>>"')
        self.assertToken(self.lexer.token(), 'STRING', r'""')

    def test_Name(self) -> None:
        self.lexer.input('_ _1 _a a A b1 B0 states falsetto')
        self.assertToken(self.lexer.token(), 'NAME', '_')
        self.assertToken(self.lexer.token(), 'NAME', '_1')
        self.assertToken(self.lexer.token(), 'NAME', '_a')
        self.assertToken(self.lexer.token(), 'NAME', 'a')
        self.assertToken(self.lexer.token(), 'NAME', 'A')
        self.assertToken(self.lexer.token(), 'NAME', 'b1')
        self.assertToken(self.lexer.token(), 'NAME', 'B0')
        self.assertToken(self.lexer.token(), 'NAME', 'states')
        self.assertToken(self.lexer.token(), 'NAME', 'falsetto')

    def test_InvalidToken(self) -> None:
        self.lexer.input('^')
        self.assertToken(self.lexer.token(), 'lexerror', '^')

    def test_InvalidTokenBetweenValidTokens(self) -> None:
        self.lexer.input('A ^ B')
        self.assertToken(self.lexer.token(), 'NAME', 'A')
        self.assertToken(self.lexer.token(), 'lexerror', '^')
        self.assertToken(self.lexer.token(), 'NAME', 'B')

    def test_MultipleTokens(self) -> None:
        self.lexer.input('A:B/C[}')
        self.assertToken(self.lexer.token(), 'NAME', 'A')
        self.assertToken(self.lexer.token(), 'COLON', ':')
        self.assertToken(self.lexer.token(), 'NAME', 'B')
        self.assertToken(self.lexer.token(), 'FORWARD_SLASH', '/')
        self.assertToken(self.lexer.token(), 'NAME', 'C')
        self.assertToken(self.lexer.token(), 'LBRACKET', '[')
        self.assertToken(self.lexer.token(), 'RBRACE', '}')

if __name__ == '__main__':
    unittest.main(verbosity=2)
