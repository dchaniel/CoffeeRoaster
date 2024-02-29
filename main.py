import time
import board
import busio
import adafruit_mcp9600
import digitalio
import asyncio

# Initialize hardware components
i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
mcp = adafruit_mcp9600.MCP9600(i2c)
psm = digitalio.DigitalInOut(board.D4)
psm.direction = digitalio.Direction.OUTPUT

# Define temperature profile
temperature_profile = [(0, 25), (300, 150), (600, 200), (900, 225), (1200, 180)]
deadband = 5  # Temperature range in degrees Celsius around the target

# Shared state
shared_state = {
    "current_time": 0,
    "current_temperature": 0,
    "ideal_temperature": 0,
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
    while True:
        shared_state["current_time"] = time.time() - start_time
        shared_state["ideal_temperature"] = linear_interpolation(shared_state["current_time"], times, temperatures)
        
        if shared_state["current_temperature"] < shared_state["ideal_temperature"] - deadband:
            shared_state["heater_status"] = "ON"
            psm.value = True
        elif shared_state["current_temperature"] > shared_state["ideal_temperature"] + deadband:
            shared_state["heater_status"] = "OFF"
            psm.value = False
        await asyncio.sleep(1)  # Control adjustments at 1Hz

def get_simple_timestamp():
    """Generates a simple timestamp string."""
    t = time.localtime()  # Get the current time structure
    # Format the time as "HH:MM:SS"
    return "{:02d}:{:02d}:{:02d}".format(t.tm_hour, t.tm_min, t.tm_sec)

# Adjust the log_data function
async def log_data():
    """Logs data every 0.1 seconds."""
    while True:
        print("{},{:.2f},{:.2f},{:.2f},{}".format(
            get_simple_timestamp(),
            shared_state["current_time"],
            shared_state["current_temperature"],
            shared_state["ideal_temperature"],
            shared_state["heater_status"]
        ))
        await asyncio.sleep(0.1)  # Logging at 10Hz

async def main():
    """Initializes and runs the update_temperature, control loop, and logging tasks."""
    input("Press Enter to start the roasting process...")
    temperature_task = asyncio.create_task(update_temperature())
    control_task = asyncio.create_task(control_loop())
    logging_task = asyncio.create_task(log_data())
    await asyncio.gather(temperature_task, control_task, logging_task)

asyncio.run(main())  # Uncomment this line if running in an environment that supports asyncio.run
