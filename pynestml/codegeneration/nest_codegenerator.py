#
# nest_codegeneration.py
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

import json
import datetime
import os
import re

from jinja2 import Environment, FileSystemLoader, TemplateRuntimeError
from odetoolbox import analysis

from pynestml.codegeneration.codegenerator import CodeGenerator
from pynestml.codegeneration.expressions_pretty_printer import ExpressionsPrettyPrinter
from pynestml.codegeneration.gsl_names_converter import GSLNamesConverter
from pynestml.codegeneration.gsl_reference_converter import GSLReferenceConverter
from pynestml.codegeneration.idempotent_reference_converter import IdempotentReferenceConverter
from pynestml.codegeneration.unitless_expression_printer import UnitlessExpressionPrinter
from pynestml.codegeneration.nest_assignments_helper import NestAssignmentsHelper
from pynestml.codegeneration.nest_declarations_helper import NestDeclarationsHelper
from pynestml.codegeneration.nest_names_converter import NestNamesConverter
from pynestml.codegeneration.nest_printer import NestPrinter
from pynestml.codegeneration.nest_reference_converter import NESTReferenceConverter
from pynestml.frontend.frontend_configuration import FrontendConfiguration
from pynestml.meta_model.ast_equations_block import ASTEquationsBlock
from pynestml.meta_model.ast_ode_shape import ASTOdeShape
from pynestml.meta_model.ast_variable import ASTVariable
from pynestml.solver.solution_transformers import integrate_exact_solution, functional_shapes_to_odes
from pynestml.solver.transformer_base import add_assignment_to_update_block, add_declarations_to_internals
from pynestml.solver.transformer_base import add_declaration_to_initial_values, declaration_in_initial_values
from pynestml.symbols.predefined_functions import PredefinedFunctions
from pynestml.symbols.symbol import SymbolKind
from pynestml.utils.ast_utils import ASTUtils
from pynestml.utils.logger import Logger
from pynestml.utils.logger import LoggingLevel
from pynestml.utils.messages import Messages
from pynestml.utils.model_parser import ModelParser
from pynestml.utils.ode_transformer import OdeTransformer
from pynestml.visitors.ast_symbol_table_visitor import ASTSymbolTableVisitor
from pynestml.symbol_table.symbol_table import SymbolTable
from pynestml.symbols.variable_symbol import BlockType
from pynestml.meta_model.ast_simple_expression import ASTSimpleExpression
from pynestml.meta_model.ast_expression import ASTExpression
from pynestml.visitors.ast_higher_order_visitor import ASTHigherOrderVisitor

def get_shape_by_name(neuron, shape_name):
    assert type(shape_name) is str
    shape_name = shape_name.split("__X__")[0]
    for decl in neuron.get_equations_block().get_declarations():
        if type(decl) is ASTOdeShape and decl.get_variable().get_name() == shape_name:
            print("Is shape " + str(shape_name) + "? YES")
            return decl
    print("Is shape " + str(shape_name) + "? NO")
    return None


def get_all_shapes(neuron):
    shapes = []
    for decl in neuron.get_equations_block().get_declarations():
        if type(decl) is ASTOdeShape:
            shapes.append(decl)
    return shapes


def is_delta_shape(shape):
    if type(shape) is ASTOdeShape:
        expr = shape.get_expression()
    rhs_is_delta_shape = type(expr) is ASTSimpleExpression \
        and expr.is_function_call() \
        and expr.get_function_call().get_scope().resolve_to_symbol(expr.get_function_call().get_name(), SymbolKind.FUNCTION) == PredefinedFunctions.name2function["delta"]
    rhs_is_multiplied_delta_shape = type(expr) is ASTExpression \
        and type(expr.get_rhs()) is ASTSimpleExpression \
        and expr.get_rhs().is_function_call() \
        and expr.get_rhs().get_function_call().get_scope().resolve_to_symbol(expr.get_rhs().get_function_call().get_name(), SymbolKind.FUNCTION) == PredefinedFunctions.name2function["delta"]
    return rhs_is_delta_shape or rhs_is_multiplied_delta_shape


def get_delta_shape_prefactor_expr(shape):
    assert type(shape) is ASTOdeShape
    expr = shape.get_expression()
    if type(expr) is ASTExpression \
     and expr.get_rhs().is_function_call() \
     and expr.get_rhs().get_function_call().get_scope().resolve_to_symbol(expr.get_rhs().get_function_call().get_name(), SymbolKind.FUNCTION) == PredefinedFunctions.name2function["delta"] \
     and expr.binary_operator.is_times_op:
        return expr.lhs


class NESTCodeGenerator(CodeGenerator):

    _variable_matching_template = r'(\b)({})(\b)'

    def __init__(self):
        # setup the template environment
        def raise_helper(msg):
            raise TemplateRuntimeError(msg)
        env = Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'resources_nest')))
        env.globals['raise'] = raise_helper
        env.globals["get_shape_by_name"] = get_shape_by_name
        setup_env = Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'resources_nest', 'setup')))
        setup_env.globals['raise'] = raise_helper
        # setup the cmake template
        self._template_cmakelists = setup_env.get_template('CMakeLists.jinja2')
        # setup the module class template
        self._template_module_class = env.get_template('ModuleClass.jinja2')
        # setup the NEST module template
        self._template_module_header = env.get_template('ModuleHeader.jinja2')
        # setup the SLI_Init file
        self._template_sli_init = setup_env.get_template('SLI_Init.jinja2')
        # setup the neuron header template
        self._template_neuron_h_file = env.get_template('NeuronHeader.jinja2')
        # setup the neuron implementation template
        self._template_neuron_cpp_file = env.get_template('NeuronClass.jinja2')
        self.analytic_solver_dict = None
        self._printer = ExpressionsPrettyPrinter()

    def generate_code(self, neurons):
        self.analyse_transform_neurons(neurons)
        self.generate_neurons(neurons)
        self.generate_module_code(neurons)

    def generate_module_code(self, neurons):
        # type: (list(ASTNeuron)) -> None
        """
        Generates code that is necessary to integrate neuron models into the NEST infrastructure.
        :param neurons: a list of neurons
        :type neurons: list(ASTNeuron)
        """
        namespace = {'neurons': neurons,
                     'moduleName': FrontendConfiguration.get_module_name(),
                     'now': datetime.datetime.utcnow()}
        if not os.path.exists(FrontendConfiguration.get_target_path()):
            os.makedirs(FrontendConfiguration.get_target_path())

        with open(str(os.path.join(FrontendConfiguration.get_target_path(),
                                   FrontendConfiguration.get_module_name())) + '.h', 'w+') as f:
            f.write(str(self._template_module_header.render(namespace)))

        with open(str(os.path.join(FrontendConfiguration.get_target_path(),
                                   FrontendConfiguration.get_module_name())) + '.cpp', 'w+') as f:
            f.write(str(self._template_module_class.render(namespace)))

        with open(str(os.path.join(FrontendConfiguration.get_target_path(),
                                   'CMakeLists')) + '.txt', 'w+') as f:
            f.write(str(self._template_cmakelists.render(namespace)))

        if not os.path.isdir(os.path.realpath(os.path.join(FrontendConfiguration.get_target_path(), 'sli'))):
            os.makedirs(os.path.realpath(os.path.join(FrontendConfiguration.get_target_path(), 'sli')))

        with open(str(os.path.join(FrontendConfiguration.get_target_path(), 'sli',
                                   FrontendConfiguration.get_module_name() + "-init")) + '.sli', 'w+') as f:
            f.write(str(self._template_sli_init.render(namespace)))

        code, message = Messages.get_module_generated(FrontendConfiguration.get_target_path())
        Logger.log_message(None, code, message, None, LoggingLevel.INFO)


    def analyse_transform_neurons(self, neurons):
        # type: (list(ASTNeuron)) -> None
        """
        Analyse and transform a list of neurons.
        :param neurons: a list of neurons.
        """
        for neuron in neurons:
            code, message = Messages.get_analysing_transforming_neuron(neuron.get_name())
            Logger.log_message(None, code, message, None, LoggingLevel.INFO)
            spike_updates = self.analyse_neuron(neuron)
            neuron.spike_updates = spike_updates
            # now store the transformed model
            self.store_transformed_model(neuron)

    def get_convolve_function_calls_(self, equations_block):
        # extract function names and corresponding incoming buffers
        shape_buffers = set()
        convolve_calls = OdeTransformer.get_convolve_function_calls(equations_block)
        for convolve in convolve_calls:
            el = (convolve.get_args()[0], convolve.get_args()[1])
            sym = convolve.get_args()[0].get_scope().resolve_to_symbol(convolve.get_args()[0].get_variable().name, SymbolKind.VARIABLE)
            if sym.block_type == BlockType.INPUT_BUFFER_SPIKE:
                el = (el[1], el[0])
            print("Adding " + el[0].__str__() + ", " + el[1].__str__())
            shape_buffers.add(el)
        return shape_buffers
    
    def replace_convolve_calls_with_buffer_expr_(self, equations_block, shape, spike_input_port, buffer_var):
        def replace_function_call_through_var(_expr=None):
            if _expr.is_function_call() and _expr.get_function_call().get_name() == "convolve":
                convolve = _expr.get_function_call()
                el = (convolve.get_args()[0], convolve.get_args()[1])
                sym = convolve.get_args()[0].get_scope().resolve_to_symbol(convolve.get_args()[0].get_variable().name, SymbolKind.VARIABLE)
                if sym.block_type == BlockType.INPUT_BUFFER_SPIKE:
                    el = (el[1], el[0])
                if shape.get_variable().get_name() == el[0].get_variable().get_name() \
                 and spike_input_port.get_variable().get_name() == el[1].get_variable().get_name():
                    _expr.set_function_call(None)
                    _expr.set_variable(ASTVariable(buffer_var))

        func = lambda x: replace_function_call_through_var(x) if isinstance(x, ASTSimpleExpression) else True

        equations_block.accept(ASTHigherOrderVisitor(func))

    
    def replace_convolve_calls_with_buffers_(self, equations_block, shape_buffers):
        for (shape, spike_input_port) in shape_buffers:
            buffer_var = shape.__str__() + "__X__" + spike_input_port.__str__()
            self.replace_convolve_calls_with_buffer_expr_(equations_block, shape, spike_input_port, buffer_var)
                
        
        
    def analyse_neuron(self, neuron):
        # type: (ASTNeuron) -> None
        """
        Analyse and transform a single neuron.
        :param neuron: a single neuron.
        """
        code, message = Messages.get_start_processing_neuron(neuron.get_name())
        Logger.log_message(neuron, code, message, neuron.get_source_position(), LoggingLevel.INFO)
        equations_block = neuron.get_equations_block()
        if equations_block is not None:

            shape_buffers = self.get_convolve_function_calls_(equations_block)
            print("shape_buffers = " + str([(str(a), str(b)) for a, b in shape_buffers]))
            self.replace_convolve_calls_with_buffers_(equations_block, shape_buffers)

            self.make_functions_self_contained(equations_block.get_ode_functions())
            self.replace_functions_through_defining_expressions(equations_block.get_ode_equations(),
                                                           equations_block.get_ode_functions())
            # transform everything into gsl processable (e.g. no functional shapes) or exact form.
            neuron = self.ode_toolbox_analysis(neuron, shape_buffers)
            spike_updates = self.apply_spikes_from_buffers(neuron, shape_buffers)
            
            # update the symbol table
            SymbolTable.clean_up_table()
            symbol_table_visitor = ASTSymbolTableVisitor()
            symbol_table_visitor.after_ast_rewrite_ = True		# suppress warnings due to AST rewrites
            neuron.accept(symbol_table_visitor)
            SymbolTable.add_neuron_scope(neuron.get_name(), neuron.get_scope())


        return spike_updates


    def generate_neuron_code(self, neuron):
        # type: (ASTNeuron) -> None
        """
        For a handed over neuron, this method generates the corresponding header and implementation file.
        :param neuron: a single neuron object.
        """
        if not os.path.isdir(FrontendConfiguration.get_target_path()):
            os.makedirs(FrontendConfiguration.get_target_path())
        self.generate_model_h_file(neuron)
        self.generate_neuron_cpp_file(neuron)


    def generate_model_h_file(self, neuron):
        # type: (ASTNeuron) -> None
        """
        For a handed over neuron, this method generates the corresponding header file.
        :param neuron: a single neuron object.
        """
        # print("!!!", neuron)
        neuron_h_file = self._template_neuron_h_file.render(self.setup_generation_helpers(neuron))
        with open(str(os.path.join(FrontendConfiguration.get_target_path(), neuron.get_name())) + '.h', 'w+') as f:
            f.write(str(neuron_h_file))


    def generate_neuron_cpp_file(self, neuron):
        # type: (ASTNeuron) -> None
        """
        For a handed over neuron, this method generates the corresponding implementation file.
        :param neuron: a single neuron object.
        """
        neuron_cpp_file = self._template_neuron_cpp_file.render(self.setup_generation_helpers(neuron))
        with open(str(os.path.join(FrontendConfiguration.get_target_path(), neuron.get_name())) + '.cpp', 'w+') as f:
            f.write(str(neuron_cpp_file))


    def setup_generation_helpers(self, neuron):
        """
        Returns a standard namespace with often required functionality.
        :param neuron: a single neuron instance
        :type neuron: ASTNeuron
        :return: a map from name to functionality.
        :rtype: dict
        """
        gsl_converter = GSLReferenceConverter()
        gsl_printer = UnitlessExpressionPrinter(gsl_converter)
        # helper classes and objects
        converter = NESTReferenceConverter(False)
        unitless_pretty_printer = UnitlessExpressionPrinter(converter)

        namespace = dict()

        namespace['neuronName'] = neuron.get_name()
        namespace['neuron'] = neuron
        namespace['moduleName'] = FrontendConfiguration.get_module_name()
        namespace['printer'] = NestPrinter(unitless_pretty_printer)
        namespace['assignments'] = NestAssignmentsHelper()
        namespace['names'] = NestNamesConverter()
        namespace['declarations'] = NestDeclarationsHelper()
        namespace['utils'] = ASTUtils()
        namespace['idemPrinter'] = UnitlessExpressionPrinter()
        namespace['outputEvent'] = namespace['printer'].print_output_event(neuron.get_body())
        namespace['is_spike_input'] = ASTUtils.is_spike_input(neuron.get_body())
        namespace['is_current_input'] = ASTUtils.is_current_input(neuron.get_body())
        namespace['odeTransformer'] = OdeTransformer()
        namespace['printerGSL'] = gsl_printer
        namespace['now'] = datetime.datetime.utcnow()
        namespace['tracing'] = FrontendConfiguration.is_dev

        namespace['initial_values'] = {}
        namespace['uses_analytic_solver'] = not self.analytic_solver is None
        if namespace['uses_analytic_solver']:
            namespace['analytic_state_variables'] = self.analytic_solver["state_variables"]
            namespace['analytic_variable_symbols'] = { sym : neuron.get_equations_block().get_scope().resolve_to_symbol(sym, SymbolKind.VARIABLE) for sym in namespace['analytic_state_variables'] }
            namespace['update_expressions'] = {}
            for sym, expr in self.analytic_solver["initial_values"].items():
                namespace['initial_values'][sym] = expr
            for sym in namespace['analytic_state_variables']:
                expr_str = self.analytic_solver["update_expressions"][sym]
                expr_ast = ModelParser.parse_expression(expr_str)
                expr_ast.update_scope(neuron.get_update_blocks().get_scope()) # pretend that update expressions are in "update" block
                expr_ast.accept(ASTSymbolTableVisitor())
                namespace['update_expressions'][sym] = expr_ast

#            namespace['update_expressions'] = { sym : ModelParser.parse_expression(expr) for sym, expr in self.analytic_solver["update_expressions"].items() }

            #namespace['update_expressions'] = self.analytic_solver["update_expressions"]
            namespace['propagators'] = self.analytic_solver["propagators"]

        namespace['uses_numeric_solver'] = not self.numeric_solver is None
        if namespace['uses_numeric_solver']:
            namespace['numeric_state_variables'] = self.numeric_solver["state_variables"]
            namespace['numeric_variable_symbols'] = { sym : neuron.get_equations_block().get_scope().resolve_to_symbol(sym, SymbolKind.VARIABLE) for sym in namespace['numeric_state_variables'] }
            namespace['numeric_update_expressions'] = {}
            for sym, expr in self.numeric_solver["initial_values"].items():
                namespace['initial_values'][sym] = expr
            for sym in namespace['numeric_state_variables']:
                expr_str = self.numeric_solver["update_expressions"][sym]
                expr_ast = ModelParser.parse_expression(expr_str)
                expr_ast.update_scope(neuron.get_update_blocks().get_scope()) # pretend that update expressions are in "update" block
                expr_ast.accept(ASTSymbolTableVisitor())
                namespace['numeric_update_expressions'][sym] = expr_ast

            namespace['useGSL'] = namespace['uses_numeric_solver']
            namespace['names'] = GSLNamesConverter()
            converter = NESTReferenceConverter(True)
            unitless_pretty_printer = UnitlessExpressionPrinter(converter)
            namespace['printer'] = NestPrinter(unitless_pretty_printer)        

        namespace["spike_updates"] = neuron.spike_updates
        
        return namespace


    def is_functional_shape_present(self, shapes):
        # type: (list(ASTOdeShape)) -> bool
        """
        For a handed over list of shapes this method checks if a single shape exits with differential order of 0.
        :param shapes: a list of shapes
        :type shapes: list(ASTOdeShape)
        :return: True if at leas one shape with diff. order of 0 exits, otherwise False.
        :rtype: bool
        """
        for shape in shapes:
            if shape.get_variable().get_differential_order() == 0:
                return True
        return False


    def ode_toolbox_analysis(self, neuron, shape_buffers):
        # type: (ASTNeuron, map(str, str)) -> ASTNeuron
        """
        Solves all odes and equations in the handed over neuron.

        Precondition: it should be ensured that most one equations block is present.

        :param neuron: a single neuron instance.
        :return: A transformed version of the neuron that can be passed to the GSL.
        """
        assert isinstance(neuron.get_equations_blocks(), ASTEquationsBlock), "only one equation block should be present"

        equations_block = neuron.get_equations_block()

        if len(equations_block.get_ode_shapes()) == 0 and len(equations_block.get_ode_equations()) == 0:
            # no equations defined -> no changes to the neuron
            return neuron

        code, message = Messages.get_neuron_analyzed(neuron.get_name())
        Logger.log_message(neuron, code, message, neuron.get_source_position(), LoggingLevel.INFO)

        parameters_block = neuron.get_parameter_blocks()
        odetoolbox_indict = self.transform_ode_and_shapes_to_json(equations_block, parameters_block, shape_buffers)
        odetoolbox_indict["options"] = {}
        odetoolbox_indict["options"]["output_timestep_symbol"] = "__h"
        print("Invoking ode-toolbox with JSON input:")
        print(odetoolbox_indict)
        solver_result = analysis(odetoolbox_indict, enable_stiffness_check=False)
        print("Got result from ode-toolbox:")
        print(solver_result)
        self.solver_result = solver_result
        analytic_solvers = [x for x in solver_result if x["solver"] == "analytical"]
        assert len(analytic_solvers) <= 1, "More than one analytic solver not presently supported"
        if len(analytic_solvers) > 0:
            self.analytic_solver = analytic_solvers[0]
        else:
            self.analytic_solver = None

        solver_result = analysis(odetoolbox_indict, enable_stiffness_check=False, disable_analytic_solver=True)
        print("Got result from ode-toolbox:")
        print(solver_result)
        numeric_solvers = [x for x in solver_result if x["solver"].startswith("numeric")]
        assert len(numeric_solvers) <= 1, "More than one numeric solver not presently supported"
        if len(numeric_solvers) > 0:
            self.numeric_solver = numeric_solvers[0]
        else:
            self.numeric_solver = None

        assert neuron.get_initial_value("__h") is None, "\"__h\" is a reserved name, please do not use variables by this name in your NESTML file"
        assert not "__h" in [sym.name for sym in neuron.get_internal_symbols()], "\"__h\" is a reserved name, please do not use variables by this name in your NESTML file"
        neuron.add_to_internal_block(ModelParser.parse_declaration('__h ms = resolution()'))

        self.remove_initial_values_for_shapes_(neuron)
        self.create_initial_values_for_shapes_(neuron, [self.analytic_solver, self.numeric_solver])

        if not self.analytic_solver is None:
            neuron = add_declarations_to_internals(neuron, self.analytic_solver["propagators"])
            SymbolTable.clean_up_table()
            neuron.accept(ASTSymbolTableVisitor())
            SymbolTable.add_neuron_scope(neuron.get_name(), neuron.get_scope())

        #self.remove_shape_definitions_from_equations_block(neuron, self.analytic_solver["state_variables"])

        #if not self.numeric_solver is None:
        #    functional_shapes_to_odes(neuron, self.numeric_solver)

        return neuron


    def remove_initial_values_for_shapes_(self, neuron):
        """remove original declarations (e.g. g_in, g_in'); these might conflict with the initial value expressions returned from ode-toolbox"""

        assert isinstance(neuron.get_equations_blocks(), ASTEquationsBlock), "only one equation block should be present"

        equations_block = neuron.get_equations_block()

        symbols_to_remove = []

        for shape in equations_block.get_ode_shapes():
            shape_order = shape.get_variable().get_differential_order()
            for order in range(shape_order):
                symbol_name = shape.get_variable().get_name() + "'" * order
                symbol = equations_block.get_scope().resolve_to_symbol(symbol_name, SymbolKind.VARIABLE)
                print("Would have removed symbol " + str(symbol_name) + " = " + str(symbol))
                symbols_to_remove.append(symbol_name)

        for ode in equations_block.get_ode_equations():
            symbol_name = ode.lhs.get_name()
            symbol = equations_block.get_scope().resolve_to_symbol(symbol_name, SymbolKind.VARIABLE)
            print("Would have removed symbol " + str(symbol_name) + " = " + str(symbol))
            symbols_to_remove.append(symbol_name)

        decl_to_remove = []
        for symbol_name in symbols_to_remove:
            for decl in neuron.get_initial_blocks().get_declarations():
                if decl.get_variables()[0].get_complete_name() == symbol_name:
                    decl_to_remove.append(decl)
                    break

        for decl in decl_to_remove:
            neuron.get_initial_blocks().get_declarations().remove(decl)
                #initial_value_expr = symbol.get_declaring_expression()
                #assert not initial_value_expr is None, "No initial value found for variable name " + symbol_name
                #entry["initial_values"][symbol_name] = gsl_printer.print_expression(initial_value_expr)
            #odetoolbox_indict["dynamics"].append(entry)


    def create_initial_values_for_shapes_(self, neuron, solver_dicts):
        for solver_dict in solver_dicts:
            for var_name in solver_dict["initial_values"].keys():
                assert not declaration_in_initial_values(neuron, var_name)  # original initial value expressions should have been removed to make place for ode-toolbox results

        for solver_dict in solver_dicts:
            for var_name in solver_dict["initial_values"].keys():
                # here, overwrite is allowed because initial values might be repeated between numeric and analytic solver
                if not declaration_in_initial_values(neuron, var_name):
                    # note that for shapes that will be used in a convolution, the "initial value" is actually the value to be incremented by when a spike arrives
                    expr = solver_dict["initial_values"][var_name]
                    add_declaration_to_initial_values(neuron, var_name, expr)
                print("Adding " + str(var_name) + " = " + str(solver_dict["initial_values"][var_name]) + " to initial values")

        # shapes containing delta functions were removed before passing to ode-toolbox; reinstate initial values here
        spike_updates = []
        initial_values = neuron.get_initial_values_blocks()
        for shape in get_all_shapes(neuron):
            print("\t\tshape = " + str(shape))
            if is_delta_shape(shape):
                add_declaration_to_initial_values(neuron, shape.get_variable().get_name(), "0")

    def apply_spikes_from_buffers(self, neuron, shape_buffers):
        """generate the equations that update the dynamical variables when incoming spikes arrive.

        For example, a resulting `assignment_string` could be "I_shape_in += (in_spikes/nS) * 1".

        Note that for shapes, `initial_values` actually contains the increment upon spike arrival, rather than the initial value of the corresponding ODE dimension.

        The definition of the spike kernel shape is then set to 0.
        """

        """how many unique shape/buffer? each shape x each spike input is separate buffer? no, right?
        convolve(G, spikes_inh)
        convolve(G, spikes_exc)
        convolve(F, spikes_exc)"""

        print("in apply_spikes_from_buffers")
        spike_updates = []
        initial_values = neuron.get_initial_values_blocks()

        for shape, spike_input_port in shape_buffers:
            buffer_type = neuron.get_scope().resolve_to_symbol(str(spike_input_port), SymbolKind.VARIABLE).get_type_symbol()

            # apply spikes from input port `spike_input_port` to the state variable named `shape_spike_buf_name` (as well as its higher order derivatives) 
            shape_order = 0
            while True:
                shape_spike_buf_name = shape.__str__() + "__X__" + spike_input_port.__str__() + "__d" * shape_order
                if neuron.get_initial_value(shape_spike_buf_name) is None:
                    break
                shape_order += 1
            print("\tShape " + str(shape.__str__()) + ", order = " + str(shape_order))
            for order in range(shape_order):
                shape_spike_buf_name = shape.__str__() + "__X__" + spike_input_port.__str__() + "__d" * order
                shape_name = shape.get_variable().get_name()
                expr = "1."
                if is_delta_shape(get_shape_by_name(neuron, shape_name)):
                    expr = get_delta_shape_prefactor_expr(get_shape_by_name(neuron, shape_name))
                else:  # not a delta shape

                    expr = str(neuron.get_initial_value(shape_spike_buf_name))
                    assert not expr is None, "Initial value not found for shape " + shape_name

                if expr in ["0", "0.", "0.0"]:
                    print("zero")
                    continue    # skip adding the statement if we're only adding zero

                assignment_string = shape_spike_buf_name + " += "
                assignment_string += "(" + str(spike_input_port) + ")"
                if not expr in ["1.", "1.0", "1"]:
                    assignment_string += " * (" + self._printer.print_expression(ModelParser.parse_expression(expr)) + ")"
                if not buffer_type.print_nestml_type() in ["1.", "1.0", "1"]:
                    assignment_string += " / (" + buffer_type.print_nestml_type() + ")"

                print("\t\t\t--> assignment_string = " + str(assignment_string))
                #spike_updates.append(assignment_string + "\n")
                ast_assignment = ModelParser.parse_assignment(assignment_string)
                ast_assignment.update_scope(neuron.get_equations_blocks().get_scope())
                
                #SymbolTable.clean_up_table()
                symbol_table_visitor = ASTSymbolTableVisitor()
                #symbol_table_visitor.after_ast_rewrite_ = True		# suppress warnings due to AST rewrites
                ast_assignment.accept(symbol_table_visitor)
                #SymbolTable.add_neuron_scope(neuron.get_name(), neuron.get_scope())
                
                spike_updates.append(ast_assignment)
    
        print("spike_updates = " + str(spike_updates))

        return spike_updates
        #for assignment in spike_updates:
            #add_assignment_to_update_block(assignment, neuron)


    def remove_shape_definitions_from_equations_block(self, neuron, shapes_name_list):
        """
        Removes all shapes in this block.
        """
        shapes_name_list_ = [s.replace("'", "__d") for s in shapes_name_list]
        equations_block = neuron.get_equations_block()

        decl_to_remove = []
        for decl in equations_block.get_declarations():
            if type(decl) is ASTOdeShape and decl.lhs.get_name() in shapes_name_list_:
                decl_to_remove.append(decl)

        print("Removing shapes " + ", ".join([str(d) for d in decl_to_remove]))

        for decl in decl_to_remove:
            equations_block.get_declarations().remove(decl)


    def transform_ode_and_shapes_to_json(self, equations_block, parameters_block, shape_buffers):
        # type: (ASTEquationsBlock) -> dict[str, list]
        """Converts AST node to a JSON representation suitable for passing to ode-toolbox

        :param equations_block:equations_block
        :return: dictionary
        """
        odetoolbox_indict = {}

        gsl_converter = IdempotentReferenceConverter()
        gsl_printer = UnitlessExpressionPrinter(gsl_converter)

        odetoolbox_indict["dynamics"] = []
        for equation in equations_block.get_ode_equations():
            lhs = str(equation.lhs) # n.b. includes single quotation marks to indicate differential order
            rhs = gsl_printer.print_expression(equation.get_rhs())
            entry = {"expression": lhs + " = " + rhs}
            symbol_name = equation.get_lhs().get_name()
            symbol = equations_block.get_scope().resolve_to_symbol(symbol_name, SymbolKind.VARIABLE)
            initial_value_expr = symbol.get_declaring_expression()
            if not initial_value_expr is None:
                expr = gsl_printer.print_expression(initial_value_expr)
                entry["initial_value"] = expr
            odetoolbox_indict["dynamics"].append(entry)

        for shape in equations_block.get_ode_shapes():
            shape_variable_names = []
            for shape_, spike_buf in shape_buffers:
                shape_name = shape_.__str__()
                print("Testing " + shape_name + " == " +shape.get_variable().get_name()) 
                if shape_name == shape.get_variable().get_name():
                    shape_variable_names.append(shape.get_variable().get_name() + "__X__" + str(spike_buf) + "'" * shape.get_variable().get_differential_order())
            
            for lhs in shape_variable_names:
                rhs = str(shape.get_expression())

                if is_delta_shape(shape):
                    # delta function -- skip passing this to ode-toolbox
                    continue

                entry = {}
                entry["expression"] = lhs + " = " + rhs
                entry["initial_values"] = {}
                shape_order = shape.get_variable().get_differential_order()
                for order in range(shape_order):
                    symbol_name = shape.get_variable().get_name() + "'" * order
                    assert not equations_block.get_scope() is None, "Undeclared variable: " + symbol_name
                    symbol = equations_block.get_scope().resolve_to_symbol(symbol_name, SymbolKind.VARIABLE)
                    initial_value_expr = symbol.get_declaring_expression()
                    assert not initial_value_expr is None, "No initial value found for variable name " + symbol_name
                    entry["initial_values"][symbol_name] = gsl_printer.print_expression(initial_value_expr)
                odetoolbox_indict["dynamics"].append(entry)

                       
        odetoolbox_indict["parameters"] = {}
        for decl in parameters_block.get_declarations():
            for var in decl.variables:
                odetoolbox_indict["parameters"][var.get_complete_name()] = gsl_printer.print_expression(decl.get_expression())
        print("odetoolbox_indict = " + str(json.dumps(odetoolbox_indict, indent=4)))
        return odetoolbox_indict


    def make_functions_self_contained(self, functions):
        # type: (list(ASTOdeFunction)) -> list(ASTOdeFunction)
        """
        TODO: it should be a method inside of the ASTOdeFunction
        TODO by KP: this should be done by means of a visitor
        Make function definition self contained, e.g. without any references to functions from `functions`.
        :param functions: A sorted list with entries ASTOdeFunction.
        :return: A list with ASTOdeFunctions. Defining expressions don't depend on each other.
        """
        for source in functions:
            source_position = source.get_source_position()
            for target in functions:
                matcher = re.compile(self._variable_matching_template.format(source.get_variable_name()))
                target_definition = str(target.get_expression())
                target_definition = re.sub(matcher, "(" + str(source.get_expression()) + ")", target_definition)
                target.expression = ModelParser.parse_expression(target_definition)

                def log_set_source_position(node):
                    if node.get_source_position().is_added_source_position():
                        node.set_source_position(source_position)

                target.expression.accept(ASTHigherOrderVisitor(visit_funcs=log_set_source_position))

        return functions


    def replace_functions_through_defining_expressions(self, definitions, functions):
        # type: (list(ASTOdeEquation), list(ASTOdeFunction)) -> list(ASTOdeFunction)
        """
        Refactors symbols form `functions` in `definitions` with corresponding defining expressions from `functions`.

        :param definitions: A sorted list with entries {"symbol": "name", "definition": "expression"} that should be made
        free from.
        :param functions: A sorted list with entries {"symbol": "name", "definition": "expression"} with functions which
        must be replaced in `definitions`.
        :return: A list with definitions. Expressions in `definitions` don't depend on functions from `functions`.
        """
        for fun in functions:
            source_position = fun.get_source_position()
            for target in definitions:
                matcher = re.compile(self._variable_matching_template.format(fun.get_variable_name()))
                target_definition = str(target.get_rhs())
                target_definition = re.sub(matcher, "(" + str(fun.get_expression()) + ")", target_definition)
                target.rhs = ModelParser.parse_expression(target_definition)

                def log_set_source_position(node):
                    if node.get_source_position().is_added_source_position():
                        node.set_source_position(source_position)

                target.accept(ASTHigherOrderVisitor(visit_funcs=log_set_source_position))
        return definitions


    def store_transformed_model(self, ast):
        if FrontendConfiguration.store_log:
            with open(str(os.path.join(FrontendConfiguration.get_target_path(), '..', 'report',
                                       ast.get_name())) + '.txt', 'w+') as f:
                f.write(str(ast))
