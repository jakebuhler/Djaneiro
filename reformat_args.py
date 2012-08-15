import re

import sublime
import sublime_plugin


class TokenStack(object):

    def __init__(self, tokens):
        self._tokens = tokens
        self._stack = []

    @property
    def empty(self):
        return not self._stack

    def process(self, char):
        if self._stack and char == self._stack[-1]:
            self._stack.pop()
        elif char in self._tokens:
            self._stack.append(self._tokens[char])


class ReformatArgsCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        self.view.run_command('expand_selection', {'to': 'brackets'})
        for sel in self.view.sel():
            self.view.replace(edit, sel, self._reformat_args(sel))

    def is_enabled(self):
        point = self.view.sel()[0].begin()
        return 'source.python' in self.view.scope_name(point)

    def _reformat_args(self, sel):
        bracket_stack = TokenStack({'(': ')', '{': '}', '[': ']'})
        string_stack = TokenStack({'"': '"', "'": "'"})
        args = []
        current_arg = ''
        # the token stacks keep track of arguments that may contain commas
        # so that those arguments are not split
        for char in self.view.substr(sel):
            string_stack.process(char)
            if string_stack.empty:
                bracket_stack.process(char)
            if char == ',' and string_stack.empty and bracket_stack.empty:
                args.append(current_arg)
                current_arg = ''
            else:
                current_arg += char
        args.append(current_arg)
        return self._format_args(sel, args)

    def _format_args(self, sel, args):
        line_str = self.view.substr(self.view.line(sel))
        indent = re.match(r'[ \t]*', line_str).group(0) + '\t'
        separator = ',\n' + indent
        return '\n' + indent + separator.join([arg.strip() for arg in args])
