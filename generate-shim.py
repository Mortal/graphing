import re
import argparse
import textwrap


def get_sections(pattern, s, flags=0):
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


def get_classes(s):
    pattern = r'^\n*class ([A-Z]\w+)\((.*)\)\n==*\n+'
    for mo, rest in get_sections(pattern, s, re.M):
        name = mo.group(1)
        bases = mo.group(2)
        bases = re.sub(r':[a-z]+:(?:[a-z]+:)?`(\w+)`',
                       lambda mo: mo.group(1), bases)

        mo2 = re.search(r'^\n*()\.\.', rest, re.M)
        assert mo2
        class_docstring = rest[:mo2.start()]
        methods = rest[mo2.start(1):]
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
    def repl(mo):
        return '%s*args, **kwargs' % (mo.group(1) or ', ')
    return re.sub(r'(, )?\[.*', repl, s)


def get_init_docstring(s):
    mo = re.match(r'^\.\. class:: \w+(?:\((.*)\))?\n+', s)
    assert mo
    args = parse_args(mo.group(1) or '')

    mo2 = re.search(r'^\n*() *\.\. method::', s, re.M)
    end_of_docstring = len(s) if mo2 is None else mo2.start()
    doc = s[mo.end():end_of_docstring]
    beginning_of_rest = len(s) if mo2 is None else mo2.start(1)
    rest = s[beginning_of_rest:]
    return args, doc, rest


def get_methods(s):
    pattern = r'^\s*\.\. method:: (\w+)\((.*)\)\n+'
    for mo, body in get_sections(pattern, s, re.M):
        name = mo.group(1)
        args = parse_args(mo.group(2))
        yield (name, args, textwrap.dedent(body))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--bases', action='append', default=())
    parser.add_argument('filename')
    parser.add_argument('template')
    args = parser.parse_args()

    base_override = {k: v for kv in args.bases for k, v in [kv.split(':')]}

    with open(args.template) as fp:
        print(fp.read(), end='')

    with open(args.filename) as fp:
        input_file = fp.read()

    for class_name, bases, class_docstring, rest in get_classes(input_file):
        if bases == '':
            superclass = '_%s' % class_name
            bases = ('%s, ' % superclass +
                     'metaclass=superclass_of(%s)' % superclass)
            super_obj = 'self.wrapped'
            init_call = 'self.wrapped = %s(%%s)' % superclass
        else:
            superclass = bases.split(',')[0]
            super_obj = 'super()'
            init_call = 'super().__init__(%s)'

        bases = base_override.get(class_name, bases)
        print('')
        print('')
        print('class %s(%s):' % (class_name, bases))
        print(render_docstring(class_docstring, 4*' '))
        print('')
        init_args, init_doc, rest = get_init_docstring(rest)
        print('    def __init__(self%s%s):' % (init_args and ', ', init_args))
        print(render_docstring(init_doc, 8*' '))
        print(8*' ' + init_call % init_args)
        for name, args, doc in get_methods(rest):
            print('')
            print('    def %s(self%s%s):' % (name, args and ', ', args))
            print(render_docstring(doc, 8*' '))
            print('        return %s.%s(%s)' % (super_obj, name, args))
        if super_obj != 'super()':
            print('')
            print('    def __getattr__(self, k):')
            print('        return getattr(%s, k)' % super_obj)


if __name__ == '__main__':
    main()
