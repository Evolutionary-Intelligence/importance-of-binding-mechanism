import myokit
import numpy as np
import pandas as pd

import modelling


class SensitivityAnalysis(object):
    """
    To create a class to run the model comparison.
    """

    def __init__(self):
        super(SensitivityAnalysis, self).__init__()

        self.param_names = ['Vhalf', 'Kmax', 'Ku', 'N', 'EC50']

    def param_explore_drug(self, drug, param):

        param_lib = modelling.BindingParameters()

        interest_param_value = param_lib.binding_parameters[drug][param]

        interest_param_list = []
        for i in param_lib.drug_compounds:
            interest_param_list.append(param_lib.binding_parameters[i][param])

        low_group, high_group = \
            modelling.ParameterCategory().param_ranges[param]
        mid_range = [i for i in interest_param_list if i > low_group and
                     i < high_group]
        mid_range_minmax = (min(mid_range), max(mid_range))

        low_range = [i for i in interest_param_list if i <= low_group]
        if len(low_range) > 1 and param != 'Kmax':
            low_range_minmax = (min(low_range), max(low_range))
        elif param == 'Kmax':
            low_range_minmax = (1, 30)
        else:
            low_range_minmax = (0.9 * low_range[0], 1.1 * low_range[0])

        high_range = [i for i in interest_param_list if i >= high_group]
        if len(high_range) > 1:
            high_range_minmax = (min(high_range), max(high_range))
        else:
            high_range_minmax = (0.9 * high_range[0], 1.1 * high_range[0])

        if param in ['Kmax', 'Ku', 'EC50']:
            small_range = np.linspace(0.9 * np.log10(interest_param_value),
                                      1.1 * np.log10(interest_param_value), 10)
            param_range = np.concatenate((
                small_range,
                np.linspace(np.log10(low_range_minmax[0]),
                            np.log10(low_range_minmax[1]), 10),
                np.linspace(np.log10(mid_range_minmax[0]),
                            np.log10(mid_range_minmax[1]), 10),
                np.linspace(np.log10(high_range_minmax[0]),
                            np.log10(high_range_minmax[1]), 10)))
            param_range = np.concatenate((small_range, param_range))
            param_range = 10**param_range
        else:
            small_range = np.linspace(0.9 * interest_param_value,
                                      1.1 * interest_param_value, 10)
            param_range = np.concatenate((small_range,
                                          np.linspace(*low_range_minmax, 10),
                                          np.linspace(*mid_range_minmax, 10),
                                          np.linspace(*high_range_minmax, 10)))

        return param_range

    def param_explore(self, param, res_points=10):

        param_lib = modelling.BindingParameters()

        interest_param_list = []
        for i in param_lib.drug_compounds:
            interest_param_list.append(param_lib.binding_parameters[i][param])

        low_group, high_group = \
            modelling.ParameterCategory().param_ranges[param]
        mid_range = [i for i in interest_param_list if i > low_group and
                     i < high_group]
        mid_range_minmax = (min(mid_range), max(mid_range))

        low_range = [i for i in interest_param_list if i <= low_group]
        if len(low_range) > 1 and param != 'Kmax':
            low_range_minmax = (min(low_range), max(low_range))
        elif param == 'Kmax':
            low_range_minmax = (1, 30)
        else:
            low_range_minmax = (0.9 * low_range[0], 1.1 * low_range[0])

        high_range = [i for i in interest_param_list if i >= high_group]
        if len(high_range) > 1:
            high_range_minmax = (min(high_range), max(high_range))
        else:
            high_range_minmax = (0.9 * high_range[0], 1.1 * high_range[0])

        if param in ['Kmax', 'Ku', 'EC50']:
            param_range = np.concatenate((
                np.linspace(np.log10(low_range_minmax[0]),
                            np.log10(low_range_minmax[1]), res_points),
                np.linspace(np.log10(mid_range_minmax[0]),
                            np.log10(mid_range_minmax[1]), res_points),
                np.linspace(np.log10(high_range_minmax[0]),
                            np.log10(high_range_minmax[1]), res_points)))
            param_range = 10**param_range
        else:
            param_range = np.concatenate(
                (np.linspace(*low_range_minmax, res_points),
                 np.linspace(*mid_range_minmax, res_points),
                 np.linspace(*high_range_minmax, res_points)))

        return param_range

    def param_explore_gaps(self, param_range, category_num, param):

        res_points = int(len(param_range) / category_num)

        param_range = sorted(param_range)

        if param in ['Kmax', 'Ku']:
            param_range = np.log10(param_range)

        for i in range(category_num - 1):
            gap_start = param_range[res_points * (i + 1) - 1]
            gap_end = param_range[res_points * (i + 1)]

            # Fill in the gaps with an average difference
            delta_previous = np.abs(
                param_range[res_points * (i + 1) - 2] - gap_start)
            delta_after = np.abs(
                gap_end - param_range[res_points * (i + 1) + 1])
            if param == 'Kmax':
                delta_mean = (delta_after + delta_previous) / 2
                gap_arr = np.arange(gap_start, gap_end, delta_mean)
            else:
                delta_max = max(delta_after, delta_previous)
                gap_arr = np.arange(gap_start, gap_end, delta_max)

            param_range = np.concatenate((
                param_range, gap_arr[1:]))

        # Specific to solve the wide gaps from res_points=5
        if param == 'Kmax':
            wide_gap = param_range[res_points: res_points * 2]
            for i in range(len(wide_gap) - 1):
                fill_in_pt = (wide_gap[i] + wide_gap[i + 1]) / 2
                param_range = np.append(param_range, fill_in_pt)

        if param in ['Kmax', 'Ku']:
            param_range = 10**param_range

        return param_range

    def param_explore_uniform(self, param, res_points=20):

        param_lib = modelling.BindingParameters()

        interest_param_list = []
        for i in param_lib.drug_compounds:
            interest_param_list.append(param_lib.binding_parameters[i][param])

        min_value = min(interest_param_list)
        max_value = max(interest_param_list)

        if param in ['Kmax', 'Ku', 'EC50']:
            param_range = np.linspace(np.log10(min_value), np.log10(max_value),
                                      res_points)
            param_range = 10**param_range
        else:
            param_range = np.linspace(min_value, max_value, res_points)

        return param_range

    def comparison_evaluation(self, param_values, hERG_model, AP_model,
                              log_transform=True, APD_points=20):

        orig_param_values = pd.DataFrame(param_values, index=self.param_names)
        orig_param_values = orig_param_values.T

        # Log transformation
        if log_transform:
            orig_param_values['Kmax'] = 10**orig_param_values['Kmax']
            orig_param_values['Ku'] = 10**orig_param_values['Ku']
            orig_param_values['EC50'] = 10**orig_param_values['EC50']

        ComparisonController = modelling.ModelComparison(orig_param_values)
        Hill_curve_coefs, drug_conc_Hill, _ = \
            ComparisonController.compute_Hill(hERG_model)

        drug_conc_range = (np.log10(drug_conc_Hill[1]),
                           np.log10(drug_conc_Hill[-1]))
        try:
            APD_trapping, APD_conductance = ComparisonController.APD_sim(
                AP_model, Hill_curve_coefs, drug_conc=drug_conc_range,
                data_points=APD_points)

            RMSError = ComparisonController.compute_RMSE(APD_trapping,
                                                         APD_conductance)
            MAError = ComparisonController.compute_MAE(APD_trapping,
                                                       APD_conductance)
        except myokit.SimulationError:
            APD_trapping = [float("Nan")] * APD_points
            APD_conductance = [float("Nan")] * APD_points
            RMSError = float("Nan")
            MAError = float("Nan")

        return RMSError, MAError
