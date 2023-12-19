import fmpy
import numpy as np
import matplotlib.pyplot as plt

# Mock Path Data
mock_path = [5, 3, 6, 2, 9, 3]

# Load the FMU
model = '/workspace/models/PathOxygenEstimate.fmu'


def calc_oxygen(path, debug=False, plot=False):
    input_values = np.zeros(len(path), dtype=[('time', np.float64), ('dist', np.float64)])
    input_values['time'] = range(len(path))
    input_values['dist'] = path
    # input_values['slope'] = path

    result = fmpy.simulate_fmu(
        filename=model,  # Name of the FMU file to be simulated
        start_time=1,
        stop_time=len(path),
        output_interval=1,
        input=input_values,  # Structured array containing the time points and input values
        output=['oxygen']  # List of requested output variable names, in this case, just 'y'
    )

    time_points = result['time']
    output_values = result['oxygen']
    total_oxygen = sum(output_values)

    if debug:
        print(time_points)
        print(output_values)
        print("It takes ", total_oxygen, "l of oxygen to walk this path of ", sum(path), "m.")

    if plot:
        # Plot the simulation results
        plt.plot(time_points, output_values)  # Plot the output values 'y' against the time points
        plt.xlabel('Dist')  # Label the x-axis as 'Time'
        plt.ylabel('Consumption')  # Label the y-axis as 'y'
        plt.title('FMU Simulation Results')  # Set the title of the plot
        plt.grid(True)  # Enable grid lines on the plot
        plt.show()  # Display the plot

    return total_oxygen


if __name__ == "__main__":
    calc_oxygen(mock_path, debug=True, plot=True)
