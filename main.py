import sys
import os

from anytree.exporter import UniqueDotExporter

import syntax as syn
import semantics as sem
import generate_code as gen

def main():
    test_file = open(sys.argv[1], 'r', encoding = 'utf-8').read()
    file_num_lines = sum(1 for line in open(sys.argv[1], 'r', encoding = 'utf-8'))

    # Syntax
    tree, syntax_success = syn.parser(test_file, file_num_lines)
    
    # Semantics
    if (syntax_success):
        tree, symbol_table, sema_success = sem.semantics(tree)
        UniqueDotExporter(tree).to_picture("program.png")

        if(sema_success):
            gen.gen_code(tree, symbol_table, sema_success)

main()
