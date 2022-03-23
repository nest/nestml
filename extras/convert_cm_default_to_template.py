import os
import argparse


def get_replacement_patterns():
    repl_patterns = {
        # include guards
        'CM_DEFAULT_H'          : 'CM_{cm_unique_suffix | upper }}_H',
        'CM_TREE_H'             : 'CM_TREE_{{cm_unique_suffix | upper }}_H',
        # file names
        'cm_default'            : '{{neuronSpecificFileNamesCmSyns[\"main\"]}}',
        'cm_tree'               : '{{neuronSpecificFileNamesCmSyns[\"tree\"]}}',
        'cm_compartmentcurrents': '{{neuronSpecificFileNamesCmSyns[\"compartmentcurrents\"]}}',
        # class names
        'CompTree'              : 'CompTree{{cm_unique_suffix}}',
        'Compartment'           : 'Compartment{{cm_unique_suffix}}',
        'CompartmentCurrents'   : 'CompartmentCurrents{{cm_unique_suffix}}',
    }
    return repl_patterns


def get_replacement_filenames():
    repl_fnames = {
        'cm_default.h': 'MainHeader.jinja2',
        'cm_default.cpp': 'MainClass.jinja2',
        'cm_tree.h': 'TreeHeader.jinja2',
        'cm_tree.cpp': 'TreeClass.jinja2'
    }
    return repl_fnames


def parse_command_line():
    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--source-path', dest='source_path',
                        action='store', type=str,
                        default='',
                        help='Path to the nest-simulator source code')

    parser.add_argument('-t', '--target-path', dest='target_path',
                        action='store', type=str,
                        default='../pynestml/codegeneration/resources_nest/cm_templates',
                        help='Path to the nest-simulator source code')

    return parser.parse_args()


def replace_in_file(source_path, target_path, source_name, target_name):

    with open(os.path.join(source_path, source_name), "rt") as fin:
        with open(os.path.join(target_path, target_name), "wt") as fout:
            for line in fin:
                for cm_default_str, jinja_templ_str in get_replacement_patterns().items():
                    line = line.replace(cm_default_str, jinja_templ_str)
                fout.write(line)


def convert_cm_default_to_templates(source_path, target_path):
    source_path = os.path.join(source_path, "models/")

    for source_name, target_name in get_replacement_filenames().items():
        replace_in_file(source_path, target_path, source_name, target_name)


if __name__ == "__main__":
    cl_args = parse_command_line()
    convert_cm_default_to_templates(cl_args.source_path, cl_args.target_path)

