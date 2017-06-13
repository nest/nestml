import json
import sys
from shapes import ShapeFunction
from prop_matrix import PropagatorCalculator


class Result:
    """
    The class is used to store computation results that are then easily converted into the json format
    """

    def __init__(self, status, solver, propagator_elements, ode_var_factor, const_input, update_instructions):
        self.status = status
        self.solver = solver
        self.initial_values = []
        self.propagator_elements = propagator_elements
        self.ode_var_factor = ode_var_factor
        self.update_instructions = update_instructions
        self.additional_state_variables = []
        self.const_input = const_input

    def add_state_variables(self, state_variables):
        self.additional_state_variables += state_variables

    def add_initial_values(self, initial_values):
        self.initial_values += initial_values


class OdeAnalyzer(object):
    """
    Orchestrates the execution of analysis activities which lead to a exact solution.
    """

    @staticmethod
    def compute_solution(arguments):
        """
        The function computes a list with propagator matrices.
        :arguments A list starting with an ODE of the first order followed by shape definitions. An ODE is of the form 
        `var_name' = python_expression`. A shape function is of the form: `shape_name = python_expression`
        
        :returns JSON object containing all data necessary to compute an update step.
        """
        assert len(arguments) >= 2
        ode_definition = arguments[0]
        shapes_strings = arguments[1:]

        # extract the name of the ODE and its defining expression
        ode_definition = ode_definition.split('=')  # it is now a list with 2 elements
        ode_var = ode_definition[0].replace("'", "").strip()
        ode_rhs = ode_definition[1].strip()

        shape_functions = [] # contains shape functions as ShapeFunction objects
        for shape in shapes_strings:
            tmp = shape.split('=')
            lhs_var = tmp[0].strip()
            rhs = tmp[1].strip()
            try:
                shape_functions.append(ShapeFunction(lhs_var, rhs))
            except Exception:
                result = Result("failed", None, None, None, None, None)
                return json.dumps(result.__dict__, indent=2)

        calculator = PropagatorCalculator()
        prop_matrices, const_input, step_const = calculator.ode_to_prop_matrices(shape_functions, ode_var, ode_rhs)
        propagator_elements, ode_var_factor, const_input, update_instructions = calculator.prop_matrix_to_prop_step(
            prop_matrices,
            const_input,
            step_const,
            shape_functions,
            ode_var)

        result = Result(propagator_elements, ode_var_factor, const_input, update_instructions)

        for shape in shape_functions:
            result.add_state_variables(shape.additional_state_variables())
            result.add_initial_values(shape.get_initial_values())

        return json.dumps(result.__dict__, indent=2)


# MAIN ENTRY POINT ###
if __name__ == "__main__":
    OdeAnalyzer.compute_solution(sys.argv[1:])
