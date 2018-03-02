import argutil
from argutil import (
    ParserDefinition,
    WorkingDirectory
)
from datetime import datetime
import os
import sys
from fnmatch import fnmatch
from .repl import Repl

parser_def = ParserDefinition()
argparser = None


def get_defaults():
    return [
        line.replace('init.', '')
        for line in parser_def.config()
    ]


def get_defaults_map():
    return {
        parts[0]: '='.join(parts[1:])
        for parts in (
            line.split('=') for line in get_defaults()
        )
    }


def get_repl(opts):
    repl = Repl(date=datetime.now())
    for k, v in Repl(opts.init).items():
        repl[k] = v
    if 'author.name' not in repl:
        repl.author.name = repl.author.username
    repl.description = opts.desc or opts.package
    return repl


def copy_file(src_file, dst_dir, repl, dst_file=None):
    if dst_file is None:
        dst_file = os.path.basename(src_file)
    if repl is None:
        repl = {}
    with open(src_file) as f_src:
        src_contents = f_src.read()
    dst_contents = src_contents.format(**repl)
    dst_file = os.path.join(dst_dir, dst_file)
    with open(dst_file, 'w') as f_dst:
        f_dst.write(dst_contents)


@argutil.callable()
def config(opts):
    if opts.list:
        for line in get_defaults():
            print(line)
    elif opts.get:
        for line in get_defaults():
            if fnmatch(line[:line.index('=')], opts.get):
                print(line)
    elif opts.configs:
        parser_def.config(
            cfg if cfg.startswith('init.') else 'init.' + cfg
            for cfg in opts.configs
        )
    else:
        argparser.parse_args(['config', '-h'])
    return 0


@argutil.callable('pypi')
def gen_pypi(opts):
    repl = get_repl(opts)
    repl.name = opts.package
    files = [
        (
            os.path.join('license', '{}.rst'.format(opts.license)),
            'LICENSE.rst'
        ),
        'setup.cfg',
        'setup.py',
        (os.path.join('Makefiles', 'pypi'), 'Makefile'),
        'CHANGELOG.rst',
        'README.rst',
    ]

    src_dir = os.path.join(os.path.dirname(__file__), 'templates')
    if not os.path.isdir(opts.directory):
        os.makedirs(opts.directory)
    for i in range(len(files)):
        if isinstance(files[i], str):
            files[i] = (files[i], None)
        src, dst = files[i]
        files[i] = (os.path.join(src_dir, src), dst)
    for src_file, dst_file in files:
        copy_file(src_file, opts.directory, repl, dst_file)

    with WorkingDirectory(opts.directory):
        os.mkdir(opts.package)
        with open(os.path.join(opts.package, '__init__.py'), 'w') as f:
            f.write('VERSION="0.0.1"\n')

        os.mkdir('tests')
        with open(os.path.join('tests', '__init__.py'), 'w') as f:
            f.write('')

    return 0


def main():
    opts = argparser.parse_args(sys.argv[1:])
    if hasattr(opts, 'directory'):
        opts.directory = os.path.abspath(opts.directory or '.')
    if opts.init.get('author.name', None) is None:
        opts.init['author.name'] = opts.init['author.username']
    return opts.func(opts)


argparser = parser_def.get_parser()
if __name__ == '__main__':
    sys.exit(main())
