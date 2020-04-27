import click
import logging
import os
import sys
from typing import Dict

from .checker import check as check_tree
from .config import Config
from .formatter import format as format_tree
from .syntax_tree import SyntaxTree

# setting logger
logger = logging.getLogger(__name__)


@click.command(context_settings={'ignore_unknown_options': True})
@click.argument('files', nargs=-1, type=click.Path())
@click.option('--config', '-c', 'config_file',
              type=click.Path(),
              help='Path to the config file that will be the authoritative config source.')
@click.option('--format', '-f', 'is_format', is_flag=True, help='Prints formatted sql and exit')
@click.option('--format-replace', '-fr', 'is_format_replace', is_flag=True, help='Reqlace file by formatted sql and exit')
def main(files, config_file, is_format, is_format_replace):
    """

    Args:
        files:
        config_file: path to the user config file.
        is_format: the flage whether outputs formatted sql

    Returns:

    """

    if len(files) == 0:
        # Todo: search *.sql file in current directory recursively.
        return

    config = Config(config_file)
    # constructs syntax tree in each files
    for f in files:
        if not os.path.exists(f):
            logger.warning(f'file is not found: {f}')
            continue

        if os.path.isdir(f):
            logger.warning(f'{f} is a directory')
            continue

        tree: SyntaxTree
        file_contents: str
        with open(f, 'r') as fp:
            file_contents = fp.read()
            if is_format or is_format_replace:
                # constructs syntax tree
                tree = SyntaxTree.sqlptree(file_contents, is_abstract=True)
            else:
                tree = SyntaxTree.sqlptree(file_contents)

        if is_format:
            formatted_tree = format_tree(tree, config)
            logger.info(formatted_tree.sqlftree())
        elif is_format_replace:
            formatted_tree = format_tree(tree, config)
            formattec_contents = formatted_tree.sqlftree()
            if file_contents == formattec_contents:
                sys.exit(0)
            with open(f, 'w') as fp:
                fp.write(formattec_contents)
                sys.exit(1)
        else:
            tree.sqlftree()
            rc = 0
            for v in sorted(check_tree(tree, config)):
                rc = 1
                logger.info('{} {}'.format(f, v))
            sys.exit(rc)

if __name__ == '__main__':
    main()
