import math
import unittest
from typing import List

import numpy as np
import pandas
from matplotlib import pyplot as plt
from numpy import ndarray
from scipy.optimize import least_squares

from incubator.config.config import resource_file_path
from incubator.data_processing.data_processing import load_data, derive_data
from incubator.models.plant_models.model_functions import run_experiment_four_parameter_model, construct_residual
from incubator.monitoring.kalman_filter_4p import KalmanFilter4P
from incubator.physical_twin.low_level_driver_server import CTRL_EXEC_INTERVAL
from incubator.tests.cli_mode_test import CLIModeTest
from incubator.visualization.data_plotting import plotly_incubator_data, show_plotly


def run_kf(measurements_heater: ndarray, measurements_Troom: ndarray, measurements_T: ndarray,
           factory, reset_trigger):
    """
    Runs a kalman filter

    Parameters:
        factory - Constructs a Kalman filter, given a measurement and previous predictions
        reset_trigger - Encode the condition that went through will cause this function to reset the KF.
    """
    assert len(measurements_heater) == len(measurements_Troom) == len(measurements_T)
    prediction = [np.array([[measurements_T[0]], [measurements_T[0]]])]
    kf = factory(measurements_heater[0], measurements_Troom[0], measurements_T[0], prediction)
    resets = [1.]
    for i in range(len(measurements_heater)-1):
        x = kf.kalman_step(measurements_heater[i], measurements_Troom[i], measurements_T[i])
        prediction.append(x)
        if reset_trigger(measurements_T[i], x[1, 0]):
            kf = factory(measurements_heater[i], measurements_Troom[i], measurements_T[i], prediction)
            resets.append(1.)
        else:
            resets.append(0.)
    prediction = np.array(prediction).squeeze(2)
    assert len(prediction) == len(measurements_heater) == len(resets)
    return prediction, resets


class TestFaultDiagnosisWithKalmanFilter(CLIModeTest):
    """
    Illustrates how fault diagnosis can be done using 2 Kalman filters,
    each tuned to a model of a different system operating mode.
    """

    def test_fault_diagnosis_by_resetting_kalman_filters(self):
        """
        Shows an example of fault diagnosis that is implemented by resetting
        the kalman filters when the discrepancy is detected.

        The idea is to use the frequency of resets on a common filters in order to assess which mode the system is in.
        """
        data_sample_size = CTRL_EXEC_INTERVAL

        # Load the data
        time_unit = 'ns'
        data, _ = load_data("./incubator/datasets/20210122_lid_opening_kalman/lid_opening_experiment_jan_2021.csv",
                            desired_timeframe=(-math.inf, math.inf),
                            time_unit=time_unit,
                            normalize_time=False,
                            convert_to_seconds=True)
        events = pandas.read_csv(resource_file_path("./incubator/datasets/20210122_lid_opening_kalman/events.csv"))
        events["timestamp_ns"] = pandas.to_datetime(events["time"], unit=time_unit)

        # Rename column to make data independent of specific tN's
        data.rename(columns={"t1": "T_room"}, inplace=True)

        # Inputs to _plant
        measurements_heater = np.array([1.0 if b else 0.0 for b in data["heater_on"]])

        measurements_Troom = data["T_room"].to_numpy()

        # System state
        measurements_T = data["average_temperature"].to_numpy()

        std_dev = 0.0001
        Theater_covariance_init = T_covariance_init = 0.0002

        C_air = 177.62927865
        G_box = 0.77307655
        C_heater = 239.61236331
        G_heater = 2.31872819
        V_heater = 12.16
        I_heater = 10.45

        reset_trigger_threshold = 3.0

        def create_closed_lid_kf(current_measurement_heater, current_measurement_Troom, current_measurement_T,
                                 prediction):
            initial_heat_temperature = current_measurement_T if not prediction else prediction[-1][0, 0]
            return KalmanFilter4P(data_sample_size, std_dev, Theater_covariance_init,
                                  T_covariance_init,
                                  C_air,
                                  G_box,
                                  C_heater,
                                  G_heater, V_heater, I_heater,
                                  initial_room_temperature=current_measurement_Troom,
                                  initial_box_temperature=current_measurement_T,
                                  initial_heat_temperature=initial_heat_temperature)

        closed_lid_kalman_prediction, resets_closed_lid = run_kf(measurements_heater, measurements_Troom, measurements_T,
                                              create_closed_lid_kf,
                                              lambda measured_T, predicted_T:
                                                abs(measured_T - predicted_T) > reset_trigger_threshold
                                              )

        std_dev = 0.0001
        Theater_covariance_init = T_covariance_init = 0.0002

        def create_open_lid_kf(current_measurement_heater, current_measurement_Troom, current_measurement_T,
                               prediction):
            initial_heat_temperature = current_measurement_T if not prediction else prediction[-1][0, 0]
            return KalmanFilter4P(data_sample_size, std_dev, Theater_covariance_init,
                                  T_covariance_init,
                                  C_air,
                                  G_box*20.0, # Mimics effect of open lid.
                                  C_heater,
                                  G_heater, V_heater, I_heater,
                                  initial_room_temperature=current_measurement_Troom,
                                  initial_box_temperature=current_measurement_T,
                                  initial_heat_temperature=initial_heat_temperature)

        open_lid_kalman_prediction, resets_open_lid = run_kf(measurements_heater, measurements_Troom, measurements_T,
                                            create_open_lid_kf,
                                            lambda measured_T, predicted_T:
                                                abs(measured_T - predicted_T) > reset_trigger_threshold
                                            )

        # Compute lid open diagnosis with some simple thumb rules:
        # This is the real equivalent of the Boolean operation
        #   lid_open = (not resets_open_lid) and resets_closed_lid
        # Except that some smoothing is applied to eliminate noise

        def smooth(signal):
            n_samples_window = 6
            return np.convolve(signal, np.ones(n_samples_window), 'valid') / n_samples_window

        resets_open_lid_array = smooth(np.array(resets_open_lid))

        lid_open_diagnoses = [True if v < 0.15 else False for v in resets_open_lid_array]

        fig = plotly_incubator_data(data, show_actuators=True, compare_to={
            "Kalman_ClosedLid": {
                "timestamp_ns": data["timestamp_ns"],
                "T": closed_lid_kalman_prediction[:, 1],
                "in_lid_open": lid_open_diagnoses
            },
            "Kalman_OpenLid": {
                "timestamp_ns": data["timestamp_ns"],
                "T": open_lid_kalman_prediction[:, 1],
            },
        }, heater_T_data={
            "Kalman_ClosedLid": {
                "timestamp_ns": data["timestamp_ns"],
                "T_heater": closed_lid_kalman_prediction[:, 0]
            },
            "Kalman_OpenLid": {
                "timestamp_ns": data["timestamp_ns"],
                "T_heater": open_lid_kalman_prediction[:, 0]
            },
        }, events=events, overlay_heater=True, show_hr_time=True)

        if self.ide_mode():
            show_plotly(fig)

    def test_illustrate_unsuccessful_fault_diagnosis_with_kalman_filter(self):
        """
        Shows an example of fault diagnosis that is not successful because the
        Kalman filters are not converging fast enough to the correct dynamics.
        """
        data_sample_size = CTRL_EXEC_INTERVAL

        # Load the data
        time_unit = 'ns'
        data, _ = load_data("./incubator/datasets/20210122_lid_opening_kalman/lid_opening_experiment_jan_2021.csv",
                            desired_timeframe=(-math.inf, math.inf),
                            time_unit=time_unit,
                            normalize_time=False,
                            convert_to_seconds=True)
        events = pandas.read_csv(resource_file_path("./incubator/datasets/20210122_lid_opening_kalman/events.csv"))
        events["timestamp_ns"] = pandas.to_datetime(events["time"], unit=time_unit)

        # Rename column to make data independent of specific tN's
        data.rename(columns={"t1": "T_room"}, inplace=True)

        # Inputs to _plant
        measurements_heater = np.array([1.0 if b else 0.0 for b in data["heater_on"]])

        measurements_Troom = data["T_room"].to_numpy()

        # System state
        measurements_T = data["average_temperature"].to_numpy()

        std_dev = 0.0001
        Theater_covariance_init = T_covariance_init = 0.0002

        C_air = 177.62927865
        G_box = 0.77307655
        C_heater = 239.61236331
        G_heater = 2.31872819
        V_heater = 12.16
        I_heater = 10.45

        def create_closed_lid_kf(current_measurement_heater, current_measurement_Troom, current_measurement_T,
                                 prediction):
            initial_heat_temperature = current_measurement_T if not prediction else prediction[-1][0, 0]
            return KalmanFilter4P(data_sample_size, std_dev, Theater_covariance_init,
                                  T_covariance_init,
                                  C_air,
                                  G_box,
                                  C_heater,
                                  G_heater, V_heater, I_heater,
                                  initial_room_temperature=current_measurement_Troom,
                                  initial_box_temperature=current_measurement_T,
                                  initial_heat_temperature=initial_heat_temperature)

        closed_lid_kalman_prediction, _ = run_kf(measurements_heater, measurements_Troom, measurements_T,
                                              create_closed_lid_kf,
                                              lambda measured_T, predicted_T: False
                                              )

        std_dev = 0.0001
        Theater_covariance_init = T_covariance_init = 0.02

        def create_open_lid_kf(current_measurement_heater, current_measurement_Troom, current_measurement_T,
                               prediction):
            initial_heat_temperature = current_measurement_T if not prediction else prediction[-1][0, 0]
            return KalmanFilter4P(data_sample_size, std_dev, Theater_covariance_init,
                                  T_covariance_init,
                                  C_air,
                                  G_box*20.0, # Mimics effect of open lid.
                                  C_heater,
                                  G_heater, V_heater, I_heater,
                                  initial_room_temperature=current_measurement_Troom,
                                  initial_box_temperature=current_measurement_T,
                                  initial_heat_temperature=initial_heat_temperature)

        open_lid_kalman_prediction, _ = run_kf(measurements_heater, measurements_Troom, measurements_T,
                                            create_open_lid_kf,
                                            lambda measured_T, predicted_T: False
                                            )

        fig = plotly_incubator_data(data, compare_to={
            "Kalman_ClosedLid": {
                "timestamp_ns": data["timestamp_ns"],
                "T": closed_lid_kalman_prediction[:, 1]
            },
            "Kalman_OpenLid": {
                "timestamp_ns": data["timestamp_ns"],
                "T": open_lid_kalman_prediction[:, 1]
            },
        }, heater_T_data={
            "Kalman_ClosedLid": {
                "timestamp_ns": data["timestamp_ns"],
                "T_heater": closed_lid_kalman_prediction[:, 0]
            },
            "Kalman_OpenLid": {
                "timestamp_ns": data["timestamp_ns"],
                "T_heater": open_lid_kalman_prediction[:, 0]
            },
        }, events=events, overlay_heater=True, show_hr_time=True)

        if self.ide_mode():
            show_plotly(fig)

    def test_calibrate_4p_model_open_lid(self):
        """
        Calibrates the model for open lid data.
        """
        NEvals = 500 if self.ide_mode() else 1

        params = [
            177.62927865,  # C_air
            0.77307655,  # G_box
            239.61236331,  # C_heater
            2.31872819,  # G_heater
            12.16,  # V_heater
            10.45,  # I_heater
        ]

        data, _ = load_data(
            "./incubator/datasets/20210122_lid_opening_kalman/lid_opening_experiment_jan_2021.csv",
            desired_timeframe=(1611327598000000000, 1611327658000000000),  # Only open lid data
            time_unit='ns',
            normalize_time=False,
            convert_to_seconds=True)

        # Rename column to make data independent of specific tN's
        data.rename(columns={"t1": "T_room"}, inplace=True)

        h = 3.0

        def run_exp(params):
            m, sol = run_experiment_four_parameter_model(data, params, h=h)
            return m, sol, data

        residual = construct_residual([run_exp])

        result = least_squares(residual, params,
                               bounds=([176, 0, 238, 2, 12.15, 10.40], [178., 100., 240., 3., 12.17, 10.50]),
                               max_nfev=NEvals)
        if self.ide_mode():
            print(result)

    def test_run_experiment_four_parameter_model_open_lid(self):
        params_open_lid = [
            1.900e+02,  # C_air
            4.815e+00,  # G_box
            2.400e+02,  # C_heater
            1.000e+00,  # G_heater
            12.16,  # V_heater
            10.45,  # I_heater
        ]

        # params[0]=0.6*params[0]

        # CWD: Example_Digital-Twin_Incubator\software\
        data, _ = load_data("./incubator/datasets/20210122_lid_opening_kalman/lid_opening_experiment_jan_2021.csv",
                            desired_timeframe=(1611327598000000000, 1611327658000000000),  # Only open lid data
                            time_unit='ns',
                            normalize_time=False,
                            convert_to_seconds=True)
        # Rename column to make data independent of specific tN's
        data.rename(columns={"t1": "T_room"}, inplace=True)

        results, sol = run_experiment_four_parameter_model(data, params_open_lid)

        fig, (ax1, ax2, ax3) = plt.subplots(3, 1)
        ax1.plot(data["time"], data["average_temperature"], label="average_temperature")
        ax1.plot(results.signals["time"], results.signals["T"], linestyle="dashed", label="~T(4)")
        ax1.legend()

        ax2.plot(results.signals["time"], results.signals["T_heater"], label="~T_heater")
        ax2.legend()

        ax3.plot(data["time"], data["heater_on"], label="heater_on")
        ax3.legend()

        if self.ide_mode():
            plt.show()

        plt.close(fig)


if __name__ == '__main__':
    unittest.main()
