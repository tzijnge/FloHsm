from os import path
import argparse
from Parser import FloHsmParser
from SemanticAnalyzer import SemanticAnalyzer
from typing import List, Dict, Set, Any, Optional
from languages.cpp.generator_cpp import generate_cpp
from languages.c.generator_c import generate_c
import pathlib


def generate(input_file:str, language:str, destination_folder:str) -> None:
    with open(input_file, 'r') as f:
        parser = FloHsmParser()
        parser.parse(f.read())
        if len(parser.errors) != 0:
            for e in parser.errors:
                print (e)
            return

        semantic_analyzer = SemanticAnalyzer()
        semantic_analyzer.analyze(parser.states)
        if len(semantic_analyzer.errors) != 0:
            for e in semantic_analyzer.errors:
                print (e)
            return

        if len(semantic_analyzer.warnings) != 0:
            for w in semantic_analyzer.warnings:
                print (w)
            return
    
    settings = dict()
    settings['destination_folder'] = destination_folder
    settings['statemachine_name'] = pathlib.Path(input_file).stem

    if language == 'cpp':
        generate_cpp(semantic_analyzer, settings)

    if language == 'c':
        generate_c(semantic_analyzer, settings)

parser = argparse.ArgumentParser(description='FloHSM generator')
parser.add_argument('files', nargs='+', help='State machine descriptor files')
parser.add_argument('-o', '--outdir', dest='outdir', help='''Output directory to generate files in. If not specified,
files are generated in the same folder as the input file. Output directory will be created if it doesn't exist''')
parser.add_argument('-l', '--language', dest='language', choices=['c', 'cpp'], default='cpp',
                    help='''Language of generated output. Note that not all languages support all features''')


args = parser.parse_args()

if args.outdir is None:
    destination_folder = path.dirname(path.abspath(args.files[0]))
else:
    destination_folder = path.abspath(args.outdir)

generate(args.files[0], args.language, destination_folder)
