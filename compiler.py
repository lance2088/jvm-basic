#!/usr/bin/env python3
"""
Compile a basic file to a class file.
"""

import fileinput
import pprint
import struct
import sys

from class_file import ClassFile
from BASIC_parser import parse_to_AST
from lib.pyPEG import Symbol

def create_code(file_name, message):
    """Write the compile code to a class file"""

class Compiler:
    def __init__(self, file_name, functions):
        self.file_name = file_name.replace(".bas","")
        self.class_name = self.file_name.capitalize()
        self.functions = functions
        self.code = ClassFile(self.class_name, self.file_name)
        self.method_bytecode = b""

    def parse(self, _fileinput):
        self.AST = parse_to_AST(_fileinput)
        self._tree_walker(self.AST)

    def _tree_walker(self, tree):
        if type(tree) == list:
            for node in tree:
                self._tree_walker(node)
        if type(tree) == Symbol:
            for function in self.functions:
                if function.__name__ == tree.__name__:
                    function(self, tree.what)
            self._tree_walker(tree.what)

    def save(self):
        method_bytecode = b"\x2a\xb7" + struct.pack("!h",
            self.code.add_method_to_const_pool("java/lang/Object", "<init>", "()V")
        ) + b"\xb1"
        self.code.add_method(0x0000, "<init>", "()V", 1, 1, method_bytecode)
        self.method_bytecode += b"\xb1"
        self.code.add_method(0x0009, "main", "([Ljava/lang/String;)V", 2, 1, self.method_bytecode)

        open(self.class_name + ".class", "wb").write(self.code.write_class())

def print_statement(self,args):
    string_value = args[0].what[0]
    if string_value.__name__ == "string":
        field_print_stream = self.code.add_field_to_const_pool("java/lang/System", "out", "Ljava/io/PrintStream;")
        print_value = self.code.add_string_ref_to_const_pool(string_value.what[0])
        method_print_stream = self.code.add_method_to_const_pool("java/io/PrintStream", "println", "(Ljava/lang/String;)V")
        self.method_bytecode += b"\xb2" + struct.pack("!h", field_print_stream) + b"\x12" + struct.pack("B", print_value) + b"\xb6" + struct.pack("!h", method_print_stream)


def main():
    """Main function. Compiles a basic file to a class file."""
    if len(sys.argv) != 2:
        print("Usage: %s file.bas" % (sys.argv[0]))
        sys.exit(1)
    messages = []

    file_name = sys.argv[1]
    compiler = Compiler(file_name, [print_statement])
    compiler.parse(fileinput.input())
    compiler.save()

if __name__ == "__main__":
    main()
