from oomodelling import Model


class TwoParameterIncubatorPlant(Model):
    def __init__(self, initial_heat_voltage, initial_heat_current,
                 initial_room_temperature, initial_box_temperature,
                 C_air, G_box):
        super().__init__()

        self.in_heater_on = self.input(lambda: False)
        self.in_heater_voltage = self.input(lambda: initial_heat_voltage)
        self.in_heater_current = self.input(lambda: initial_heat_current)
        self.in_room_temperature = self.input(lambda: initial_room_temperature)

        self.power_in = self.var(lambda: self.in_heater_voltage() * self.in_heater_current() if self.in_heater_on() else 0.0)

        self.G_box = self.input(lambda: G_box)
        self.C_air = self.input(lambda: C_air)

        self.T = self.state(initial_box_temperature)

        self.power_out_box = self.var(lambda: self.G_box() * (self.T() - self.in_room_temperature()))

        self.total_power_box = self.var(lambda: self.power_in() - self.power_out_box())

        self.der('T', lambda: (1.0/self.C_air())*(self.total_power_box()))

        self.save()
