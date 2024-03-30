import time
import board
import busio
import adafruit_mcp9600
import digitalio
import asyncio

# Initialize hardware components
i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
mcp = adafruit_mcp9600.MCP9600(i2c)
psm = digitalio.DigitalInOut(board.A2)
psm.direction = digitalio.Direction.OUTPUT

# Define temperature profile
temperature_profile = [(0, 0), (100, 230), (400, 100), (450, 0)]
deadband = 0  # Temperature range in degrees Celsius around the target

# Shared state
shared_state = {
    "current_time": 0.0,
    "current_temperature": 0.0,
    "ideal_temperature": 0.0,
    "heater_status": "OFF"
}

def linear_interpolation(x, x_points, y_points):
    """Performs linear interpolation for a given x value."""
    for i in range(len(x_points) - 1):
        if x >= x_points[i] and x <= x_points[i + 1]:
            x0, y0 = x_points[i], y_points[i]
            x1, y1 = x_points[i + 1], y_points[i + 1]
            return y0 + (y1 - y0) * ((x - x0) / (x1 - x0))
    return y_points[-1]  # Return the last temperature if x is beyond the profile

async def update_temperature():
    """Updates the current temperature in the shared state every 0.1 seconds."""
    while True:
        shared_state["current_temperature"] = mcp.temperature
        await asyncio.sleep(0.1)

async def control_loop():
    """Controls the heating element and updates the shared state."""
    start_time = time.time()
    times, temperatures = zip(*temperature_profile)
    on = True
    while True:
        shared_state["current_time"] = time.time() - start_time
        shared_state["ideal_temperature"] = linear_interpolation(shared_state["current_time"], times, temperatures)

        if shared_state["current_temperature"] < shared_state["ideal_temperature"] - deadband:
            shared_state["heater_status"] = "ON"
            psm.value = True
        elif shared_state["current_temperature"] > shared_state["ideal_temperature"] + deadband:
            shared_state["heater_status"] = "OFF"
            psm.value = False
        # psm.value = on
        # on = not on
        # print("on =")
        # print(on)
        await asyncio.sleep(1)  # Control adjustments at 1Hz

def get_timestamp_filename():
    """Generates a filename based on the current date and time."""
    t = time.localtime()  # Get the current time structure
    # Format the filename as "YYYY-MM-DD_HH-MM-SS.csv"
    return "{:04d}-{:02d}-{:02d}_{:02d}-{:02d}-{:02d}.csv".format(t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)

async def log_data():
    while True:
        current_time = float(shared_state["current_time"])
        current_temperature = float(shared_state["current_temperature"])
        ideal_temperature = float(shared_state["ideal_temperature"])
        heater_status = 1 if psm.value else 0  # Convert boolean status to 1 or 0
        print("{:.2f}, {:.2f}, {}".format(current_temperature, ideal_temperature, heater_status))
        await asyncio.sleep(0.2)  # Logging at 10Hz
        
async def main():
    """Initializes and runs the update_temperature, control loop, and logging tasks."""
    temperature_task = asyncio.create_task(update_temperature())
    control_task = asyncio.create_task(control_loop())
    logging_task = asyncio.create_task(log_data())
    await asyncio.gather(temperature_task, control_task, logging_task)

asyncio.run(main())  # Uncomment this line if running in an environment that supports asyncio.run
