from spinn_utilities.overrides import overrides
from spinn_front_end_common.interface.ds import DataType
from spinn_front_end_common.utilities.constants import BYTES_PER_WORD
from spynnaker.pyNN.models.neuron.plasticity.stdp.weight_dependence import (
    AbstractWeightDependence, AbstractHasAPlusAMinus)


class MyWeightDependence(AbstractHasAPlusAMinus, AbstractWeightDependence):
    __slots__ = [
        "_my_weight_parameter",
        "_w_max",
        "_w_min"]

    # Must match number of words written by write_parameters() method
    WORDS_PER_SYNAPSE_TYPE = 3

    def __init__(
            self,

            # TODO: update the parameters
            w_min=0.0, w_max=1.0, my_weight_parameter=0.1):
        super().__init__()

        # TODO: Store any parameters
        self._w_min = w_min
        self._w_max = w_max
        self._my_weight_parameter = my_weight_parameter

    # TODO: Add getters and setters for the parameters

    @property
    def w_min(self):
        return self._w_min

    @w_min.setter
    def w_min(self, w_min):
        self._w_min = w_min

    @property
    def w_max(self):
        return self._w_max

    @w_max.setter
    def w_max(self, w_max):
        self._w_max = w_max

    @property
    def my_weight_parameter(self):
        return self._my_weight_parameter

    @my_weight_parameter.setter
    def my_weight_parameter(self, my_weight_parameter):
        self._my_weight_parameter = my_weight_parameter

    @overrides(AbstractWeightDependence.is_same_as)
    def is_same_as(self, weight_dependence):
        # TODO: Update with the correct class name
        if not isinstance(weight_dependence, MyWeightDependence):
            return False

        # TODO: update to check parameters are equal
        # pylint: disable=protected-access
        return (
            (self._w_min == weight_dependence._w_min) and
            (self._w_max == weight_dependence._w_max) and
            (self._my_weight_parameter ==
             weight_dependence._my_weight_parameter))

    @property
    def vertex_executable_suffix(self):
        """ The suffix to be appended to the vertex executable for this rule
        """
        # TODO: Add the extension to be added to the binary executable name
        # to indicate that it is compiled with this weight dependence
        # Note: The expected format of the binary name is:
        #    <neuron_model>_stdp[_mad|]_<timing_dependence>_<weight_dependence>
        return "my_weight"

    @overrides(AbstractWeightDependence.get_parameters_sdram_usage_in_bytes)
    def get_parameters_sdram_usage_in_bytes(
            self, n_synapse_types, n_weight_terms):
        # TODO: update to match the number of bytes used by the parameters
        if n_weight_terms != 1:
            raise NotImplementedError(
                "My weight dependence only supports one term")

        return self.WORDS_PER_SYNAPSE_TYPE * BYTES_PER_WORD * n_synapse_types

    @overrides(AbstractWeightDependence.write_parameters)
    def write_parameters(
            self, spec, global_weight_scale, synapse_weight_scales,
            n_weight_terms):
        # TODO: update to write the parameters
        # Loop through each synapse type's weight scale
        for w in synapse_weight_scales:
            # Scale the maximum and minimum weights to fixed-point values
            # based on the weight scaling that has been done externally
            spec.write_value(
                data=int(round(self._w_min * w)), data_type=DataType.INT32)
            spec.write_value(
                data=int(round(self._w_max * w)), data_type=DataType.INT32)

            # Write my parameter as an appropriately scaled fixed-point number
            spec.write_value(
                data=int(round(self._my_weight_parameter * w)),
                data_type=DataType.INT32)

            if n_weight_terms != 1:
                raise NotImplementedError(
                    "My weight dependence only supports one term")

    @property
    def weight_maximum(self):
        """ The maximum weight that will ever be set in a synapse as a result\
            of this rule
        """
        # TODO: update to return the maximum weight that this rule will ever
        # give to a synapse
        return self._w_max

    @overrides(AbstractWeightDependence.get_parameter_names)
    def get_parameter_names(self):
        return ['w_min', 'w_max', 'my_weight_parameter']
