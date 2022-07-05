"""Tokenize Display Clause"""
# standard library
import re


class literal(str):
    """String literal -- used by tokenizer to return quoted values"""


class TokenizeDisplay:
    """Tokenize Display Clause"""

    def get_actions(self, display):
        """Parse a display clause and return tc_action values."""

        tokens = self.tokenize(display)
        # print('tokens:', tokens)

        actions = set()
        not_actions = set()
        not_in = False
        paren_close = re.compile(r'^\){0,}$')
        paren_open = re.compile(r'^\({0,}$')
        state = 'init'

        unrecognized = 0

        while tokens:
            t = tokens.pop(0)
            # print(f't={t:20} state={state:20}')

            # handle the start of the display clause
            if state == 'init':
                if t != 'tc_action':
                    unrecognized += 1
                    continue
                state = 'in'
                not_in = False
                continue

            # handle "in" of tc_action IN ('Action')
            if state == 'in':
                if t == 'not':
                    if not_in:
                        not_in = False
                    else:
                        not_in = True
                    continue
                if t == 'in':
                    state = 'paren'
                    continue
                if t == '==':
                    state = 'equals'
                    continue
                if t == '!=':
                    state = 'equals'
                    not_in = True
                    continue

            # handle "==|!=" of tc_action == 'Action'
            if state == 'equals':
                if isinstance(t, literal):
                    if not_in:
                        not_actions.add(t)
                    else:
                        actions.add(t)
                state = 'init'
                continue

            # handle "(|)" of tc_action IN ('Action')
            if state == 'paren':
                if re.match(paren_open, t):
                    state = 'list'
                    continue
                break

            # handle "Action" of tc_action IN ('Action')
            if state == 'list':
                if isinstance(t, literal):
                    if not_in:
                        not_actions.add(t)
                    else:
                        actions.add(t)
                    continue
                if t == ',':
                    continue
                if re.match(paren_close, t):
                    state = 'init'
                    continue
                break

        return actions

    def tokenize(self, s, count=None):
        """Split string into tokens"""

        result = []
        while s:
            t = self.tokenizer.match(s)
            if t:
                token, s = t.groups()
                if token[0] in ('"', "'"):
                    token = literal(token[1:-1])
                else:
                    token = token.lower()
                result.append(token)
            else:
                break
            if count:
                count -= 1
                if count < 1:
                    break

        return result

    @property
    def tokenizer(self):
        """Return tokenizer."""
        return re.compile(
            r'''
                \s*
                (
                       [\[\]():=,!><]+
                    |  "[^"]*"
                    |  '[^']*'
                    |  \w+
                )
                \s*
                (.*)
            ''',
            re.VERBOSE,
        )
