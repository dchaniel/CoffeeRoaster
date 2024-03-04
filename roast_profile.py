class RoastProfile:
    def __init__(self, total_duration, drying_phase_percentage, browning_phase_percentage, development_phase_percentage):
        self.total_duration = total_duration

        # Slopes initialized as int()
        self.drying_phase_slope = int()
        self.browning_phase_slope = int()
        self.development_phase_slope = int()

        # Percentage values as integers
        self.drying_phase_percentage = int(drying_phase_percentage)
        self.browning_phase_percentage = int(browning_phase_percentage)
        self.development_phase_percentage = int(development_phase_percentage)

        # Non-parameter variables for durations
        self.drying_phase_duration = int()
        self.browning_phase_duration = int()
        self.development_phase_duration = int()

        # Initialize phase durations and slopes
        self.init_phase_durations()
        self.init_phase_slopes()

    def init_phase_durations(self):
        # Update phase durations based on percentage values
        self.drying_phase_duration = int(self.total_duration * (self.drying_phase_percentage / 100))
        self.browning_phase_duration = int(self.total_duration * (self.browning_phase_percentage / 100))
        self.development_phase_duration = int(self.total_duration * (self.development_phase_percentage / 100))

    def init_phase_slopes(self):
        # Update phase slopes using calculate_slope helper function
        self.drying_phase_slope = self.calculate_slope(self.drying_phase_duration, start_temp=100, target_temp=150)
        self.browning_phase_slope = self.calculate_slope(self.browning_phase_duration, start_temp=200, target_temp=300)
        self.development_phase_slope = self.calculate_slope(self.development_phase_duration, start_temp=300, target_temp=400)

    def calculate_slope(self, duration, start_temp, target_temp):
        # Calculate the slope of the line connecting start_temp to target_temp over duration seconds
        temp_change = target_temp - start_temp
        return temp_change / duration

# Example usage:
roast = RoastProfile(total_duration=600, drying_phase_percentage=30, browning_phase_percentage=40, development_phase_percentage=30)

# Accessing the variables:
print("Total Duration:", roast.total_duration, "seconds")
print("Drying Phase Slope:", roast.drying_phase_slope)
print("Browning Phase Slope:", roast.browning_phase_slope)
print("Development Phase Slope:", roast.development_phase_slope)
print("Drying Phase Percentage:", roast.drying_phase_percentage, "%")
print("Browning Phase Percentage:", roast.browning_phase_percentage, "%")
print("Development Phase Percentage:", roast.development_phase_percentage, "%")
print("Drying Phase Duration:", roast.drying_phase_duration, "seconds")
print("Browning Phase Duration:", roast.browning_phase_duration, "seconds")
print("Development Phase Duration:", roast.development_phase_duration, "seconds")