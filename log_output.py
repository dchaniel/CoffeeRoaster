import serial
import time
import matplotlib.pyplot as plt
from datetime import datetime

def initialize_serial_connection(port='/dev/tty.usbmodem2101', baud_rate=115200):
    """Initialize the serial connection."""
    return serial.Serial(port, baud_rate)

def setup_plot():
    """Setup the matplotlib plot for live data."""
    plt.ion()  # Turn on interactive mode
    fig, ax = plt.subplots(2, 1, figsize=(10, 8))  # Create two subplots
    lines = [ax[0].plot([], [], '-', label='Actual Temperature')[0],
             ax[0].plot([], [], '-', label='Desired Temperature')[0]]
    ax[0].legend(loc="upper left")
    ax[0].set_xlabel('Time (s)')
    ax[0].set_ylabel('Temperature')
    ax[1].set_xlabel('Time (s)')
    ax[1].set_ylabel('Heater Status')
    ax[1].set_ylim(-0.1, 1.1)  # Heater status is either 0 or 1
    return fig, ax, lines

def create_log_file():
    """Create a timestamped log file."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file_name = f"data_log_{timestamp}.csv"
    return open(log_file_name, "a")

def main(debug=False):
    ser = initialize_serial_connection()
    fig, ax, lines = setup_plot()
    log_file = create_log_file()

    times = []
    actual_temps = []
    desired_temps = []
    heater_statuses = []
    start_time = time.time()

    try:
        while True:
            elapsed_time = time.time() - start_time
            serial_line = ser.readline().decode('utf-8').strip()
            if debug:
                print(f"Serial Line: {serial_line}")
            
            try:
                actual_temp, desired_temp, heater_status = map(float, serial_line.split(','))
                times.append(elapsed_time)
                actual_temps.append(actual_temp)
                desired_temps.append(desired_temp)
                heater_statuses.append(heater_status)
                
                if debug:
                    print(f"Actual Temp: {actual_temp}, Desired Temp: {desired_temp}, Heater Status: {heater_status}")
                
                # Update temperature plot
                lines[0].set_data(times, actual_temps)
                lines[1].set_data(times, desired_temps)
                ax[0].relim()
                ax[0].autoscale_view(True,True,True)
                
                # Update heater status plot
                ax[1].clear()
                ax[1].step(times, heater_statuses, where='post')
                ax[1].set_ylim(-0.1, 1.1)  # Ensure the heater status plot y-axis remains 0 or 1
                ax[1].set_xlabel('Time (s)')
                ax[1].set_ylabel('Heater Status')
                
                fig.canvas.draw()
                fig.canvas.flush_events()

                # Log data
                log_file.write(f"{elapsed_time},{actual_temp},{desired_temp},{heater_status}\n")
                log_file.flush()
            except ValueError:
                pass
    except KeyboardInterrupt:
        print("User interrupted. Exiting...")
    finally:
        log_file.close()
        ser.close()
        plt.close(fig)

if __name__ == "__main__":
    # Set debug to True if you want to print debug information to the terminal
    main(debug=True)