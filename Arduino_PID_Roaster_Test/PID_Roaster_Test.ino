#include <Wire.h>
#include <Adafruit_MCP9601.h>

// Include the RBDdimmer library
#include <RBDdimmer.h>

// Define variables
double target_temp = 40.0;    // Desired temperature
double current_temp;          // Current temperature
int output_power = 0;      // Heater power level (0 to 100)
double Kp = 5.0;              // Proportional constant
double Ki = 1.0;              // Integral constant
double Kd = 0.1;              // Derivative constant
int dimmerOutputPin = 4;

// Create MCP9600 instance
Adafruit_MCP9601 mcp;

// Create dimmer instance
dimmerLamp dimmer(dimmerOutputPin);

// PID variables
double previous_error = 0;
double integral = 0;

void setup() {
  Serial.begin(9600);

  // Initialize MCP9601
  if (!mcp.begin(0x67)) { // Use the correct I2C address for your MCP9601
    Serial.println("Couldn't find MCP9601!");
    while (1);
  }

  // Initialize dimmer
  dimmer.begin(NORMAL_MODE, ON);  // Use NORMAL_MODE for resistive loads, ON for initial state
}

void loop() {
  // Read thermocouple temperature
  current_temp = readTemperature();

  // Compute PID
  output_power = computePID();

  // Adjust heat power
  adjustHeatPower();
  // Print information for analysis
  //printOutput();

  // Add a delay for stability (adjust as needed)

}

float readTemperature() {
  // Read thermocouple temperature using MCP9601
  return mcp.readThermocouple();
}

double computePID() {
  // Calculate error
  double error = target_temp - current_temp;

  // Calculate integral of the error
  integral += error;

  // Calculate derivative of the error
  double derivative = error - previous_error;

  // PID calculation
  double pid_output = Kp * error + Ki * integral + Kd * derivative;

  // Map PID output to heater power level (0 to 100)
  output_power = int(constrain(map(pid_output, -255, 255, 0, 100), 0, 100));

  // Save the current error for the next iteration
  previous_error = error;

  return output_power;
}

void adjustHeatPower() {

  // Set dimmer power using RBDdimmer library function
  dimmer.setPower(100);
}

void printOutput() {
  Serial.print("Current Temperature: ");
  Serial.print(current_temp);
  Serial.print(" | Target Temperature: ");
  Serial.print(target_temp);
  Serial.print(" | Heater Power Level: ");
  Serial.println(output_power);
  Serial.print(" | Check Dimmer Power: ");
  Serial.println(dimmer.getPower());
}
