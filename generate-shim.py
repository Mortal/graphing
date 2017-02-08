import re
import argparse
import textwrap


def get_class_docstring(s):
    mo = re.search(r'^class ([A-Z]\w+)\(\)\n==*\n+', s, re.M)
    assert mo
    name = mo.group(1)
    rest = s[mo.end():]

    mo2 = re.search(r'^\n*()\.\.', rest, re.M)
    assert mo2
    class_docstring = rest[:mo2.start()]
    methods = rest[mo2.start(1):]
    return name, class_docstring, methods


def render_docstring(s, indent):
    assert isinstance(s, str)
    rendered = repr(s)
    delim = rendered[0]
    rendered = 2*delim + rendered + 2*delim

    def repl(mo):
        if mo.group(1) == delim:
            return delim
        elif mo.group(1) == 'n':
            return '\n'
        else:
            return mo.group()

    rendered = re.sub(r'\\(.)', repl, rendered)
    assert eval(rendered) == s

    return textwrap.indent(rendered, indent)


def parse_args(s):
    def repl(mo):
        return '%s*args, **kwargs' % (mo.group(1) or ', ')
    return re.sub(r'(, )?\[.*', repl, s)


def get_init_docstring(s):
    mo = re.match(r'^\.\. class:: \w+\((.*)\)\n+', s)
    assert mo
    args = parse_args(mo.group(1))

    mo2 = re.search(r'^\n*() *\.\. method::', s, re.M)
    doc = s[mo.end():mo2.start()]
    rest = s[mo2.start(1):]
    return args, doc, rest


def get_methods(s):
    prev = None
    i = 0
    for mo in re.finditer(r'^\s*\.\. method:: (\w+)\((.*)\)\n+', s, re.M):
        j = mo.start()
        if prev:
            yield prev + (textwrap.dedent(s[i:j]),)
        prev = mo.group(1, 2)
        i = mo.end()
    j = len(s)
    if prev:
        yield prev + (textwrap.dedent(s[i:j]),)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    parser.add_argument('template')
    args = parser.parse_args()

    with open(args.template) as fp:
        print(fp.read(), end='')

    with open(args.filename) as fp:
        input_file = fp.read()

    class_name, class_docstring, rest = get_class_docstring(input_file)
    print(render_docstring(class_docstring, 4*' '))
    print('')
    init_args, init_doc, rest = get_init_docstring(rest)
    print('    def __init__(self%s%s):' % (init_args and ', ', init_args))
    print(render_docstring(init_doc, 8*' '))
    print('        super().__init__(%s)' % init_args)
    for name, args, doc in get_methods(rest):
        args = parse_args(args)
        print('')
        print('    def %s(self%s%s):' % (name, args and ', ', args))
        print(render_docstring(doc, 8*' '))
        print('        return super().%s(%s)' % (name, args))


if __name__ == '__main__':
    main()
