# -*- coding: utf-8 -*-
#
# pretty_render_code_generator.py
#
# This file is part of NEST.
#
# Copyright (C) 2004 The NEST Initiative
#
# NEST is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# NEST is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NEST.  If not, see <http://www.gnu.org/licenses/>.

import os
from typing import Sequence

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, load_lexer_from_file

from pynestml.codegeneration.code_generator import CodeGenerator
from pynestml.codegeneration.code_generator_utils import CodeGeneratorUtils
from pynestml.frontend.frontend_configuration import FrontendConfiguration
from pynestml.meta_model.ast_model import ASTModel


class PrettyRenderCodeGenerator(CodeGenerator):
    r"""
    Code generator for a "pretty render" of NESTML model code as a stylised HTML page.
    """

    _default_options = {
        "neuron_models": [],
        "synapse_models": [],
    }

    def generate_code(self, models: Sequence[ASTModel]) -> None:
        neurons, synapses = CodeGeneratorUtils.get_model_types_from_names(models, neuron_models=self.get_option("neuron_models"), synapse_models=self.get_option("synapse_models"))

        # Load the custom lexer
        lexer_fname = os.path.realpath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'extras', 'syntax-highlighting', 'pygments', 'pygments_nestml.py'))
        self.lexer = load_lexer_from_file(lexer_fname, 'NESTMLLexer')

        for neuron in neurons:
            self.generate_code_(neuron, "neuron")

        for synapse in synapses:
            self.generate_code_(synapse, "synapse")

    def generate_code_(self, model, model_type: str):
        # Read the source code file
        with open(model.file_path, 'r') as f:
            code = f.read()

        # Create the HTML formatter
        formatter = HtmlFormatter(full=True, style='colorful')

        # Highlight the code
        result = highlight(code, self.lexer, formatter)

        result += """

    <div class="circ">⬤ ⬤ ⬤ </div>

    <style>
    .circ {
        position: absolute;
    """
        if "neuron" in model_type:
            result += """
        top: 47px;
        left: 80px;"""

        if "synapse" in model_type:
            result += """
        top: 58px;
        left: 70px;"""

        result += """
        transform: translateX(-50%);
        font-size: .8em; /* Adjust the size as needed */
        font-family: Inter;
        font-weight: 500;
        letter-spacing: .32px;
        color: hsla(0,0%,100%,.2);
        padding: 10px 0; /* Optional: Add padding if needed */
        transform: rotateX(20deg) rotateY(20deg);
    }
    </style>


    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@100..900&display=swap" rel="stylesheet">


    <style>
    body {
        padding: 40px;
        color: #FFFFFF;
        background-color: #fff;
    }

    .highlight::before {
    """
        if model_type == "neuron":
            result += """
        content: "Integrate-and-fire NESTML neuron model";
    """

        if model_type == "synapse":
            result += """
        content: "STDP synapse NESTML model";
    """

        result += """
        position: absolute;
        top: 0;
        left: 50%;
        transform: translateX(-52%);
        text-align: center;
        width: 100%;
        font-size: .8em; /* Adjust the size as needed */
        font-family: Inter;
        font-weight: 500;
        letter-spacing: .32px;
        color: hsla(0,0%,100%,.6);
        padding: 10px 0; /* Optional: Add padding if needed */
    }

    .highlight {
        box-shadow: 0 0 0 1px var(--frame-highlight-border),0 0 0 1.5px var(--frame-shadow-border),0 2.8px 2.2px rgba(0,0,0,.034),0 6.7px 5.3px rgba(0,0,0,.048),0 12.5px 10px rgba(0,0,0,.06),0 22.3px 17.9px rgba(0,0,0,.072),0 41.8px 33.4px rgba(0,0,0,.086),0 100px 80px rgba(0,0,0,.12);

        border-radius: 10px;
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
        transform: rotateX(20deg) rotateY(20deg);
    """
        if model_type == "neuron":
            result += """
        width: 800px;
    """

        if model_type == "synapse":
            result += """
        width: 500px;
    """

        result += """
        padding: 40px 20px 20px 20px;
        background-color: #2e273f;
    }

    .mf, .mi {
        color: #7A7FFD !important;
    }

    .nb {
        color: #d3c277 !important;
    }

    .c1 {
        color: #807796 !important;
    }

    .k {
        color: #FF659C !important;
    }

    .o {
        color: #FF659C !important;
    }

    </style>"""

        with open(str(os.path.join(FrontendConfiguration.get_target_path(), model.get_name())) + '.html', 'w+') as f:
            f.write(result)
