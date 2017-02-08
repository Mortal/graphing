import re
import sys
import argparse
import textwrap


def get_sections(pattern, s, flags=0):
    def sections():
        prev_mo = None
        i = 0
        for mo in re.finditer(pattern, s, flags):
            j = mo.start()
            if prev_mo:
                yield (prev_mo, s[i:j])
            prev_mo = mo
            i = mo.end()
        j = len(s)
        if prev_mo:
            yield (prev_mo, s[i:j])

    mo = re.search(pattern, s, flags)
    if mo is None:
        return s, ()
    else:
        return s[:mo.start()], sections()


def get_classes(s):
    pattern = r'^\n*class ([A-Z]\w+)\((.*)\)\n==*\n+'
    before, classes = get_sections(pattern, s, re.M)
    for mo, rest in classes:
        name = mo.group(1)
        bases = mo.group(2)
        bases = re.sub(r':[a-z]+:(?:[a-z]+:)?`(\w+)`',
                       lambda mo: mo.group(1), bases)

        mo2 = re.search(r'^\n*()\.\.', rest, re.M)
        end_of_docstring = len(s) if mo2 is None else mo2.start()
        beginning_of_rest = len(s) if mo2 is None else mo2.start(1)
        class_docstring = rest[:end_of_docstring]
        methods = rest[beginning_of_rest:]
        yield name, bases, class_docstring, methods


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
    def add_default(arg):
        return '%s=None' % arg if '=' not in arg else arg

    def repl(part, depth):
        if depth:
            return re.sub(r'[^ ,]+', lambda mo: add_default(mo.group()), part)
        else:
            return part

    def parser():
        i = 0
        depth = 0
        for mo in re.finditer(r'[][]|$', s):
            j = mo.start()
            c = mo.group()
            yield repl(s[i:j], depth)
            if c == '[':
                depth += 1
            elif c == ']':
                depth -= 1
            if depth < 0:
                raise ValueError((i, j, s, depth))
            i = mo.end()
        if depth != 0:
            raise ValueError((i, j, s, depth))

    return ''.join(parser())


def get_init_docstring(s):
    mo = re.match(r'^\.\. class:: \w+(?:\((.*)\))?\n+', s)
    if mo is None:
        return None, None, None
    args = parse_args(mo.group(1) or '')

    mo2 = re.search(r'^\n*() *\.\. method::', s, re.M)
    end_of_docstring = len(s) if mo2 is None else mo2.start()
    doc = s[mo.end():end_of_docstring]
    beginning_of_rest = len(s) if mo2 is None else mo2.start(1)
    rest = s[beginning_of_rest:]
    return args, doc, rest


def get_methods(s):
    pattern = r'^\s*\.\. method:: (\w+)\((.*)\)\n+'
    before, methods = get_sections(pattern, s, re.M)
    for mo, body in methods:
        name = mo.group(1)
        args = parse_args(mo.group(2))
        yield (name, args, textwrap.dedent(body))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    parser.add_argument('module')
    args = parser.parse_args()
    real_module = args.module

    with open(args.filename) as fp:
        input_file = fp.read()

    first = True
    for class_name, bases, class_docstring, rest in get_classes(input_file):
        if not first:
            print('')
            print('')
        first = False

        print('class %s(%s):' % (class_name, bases))
        if class_docstring:
            print(render_docstring(class_docstring, 4*' '))
            print('')
        init_args, init_doc, rest = get_init_docstring(rest)
        if init_args is None:
            print('    def __new__(cls, *args, **kwargs):')
            print('        raise NotImplementedError(' +
                  '"no init docstring found")')
            continue

        print('    def __new__(cls, *args, **kwargs):')
        print('        import %s' % real_module)
        print('        return %s.%s(*args, **kwargs)' %
              (real_module, class_name))
        print('')
        print('    def __init__(self%s%s):' % (init_args and ', ', init_args))
        print(render_docstring(init_doc, 8*' '))
        print('        raise NotImplementedError')
        for name, args, doc in get_methods(rest):
            print('')
            print('    def %s(self%s%s):' % (name, args and ', ', args))
            print(render_docstring(doc, 8*' '))
            print('        raise NotImplementedError')


if __name__ == '__main__':
    main()
