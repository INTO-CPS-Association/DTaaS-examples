model PathOxygenEstimate
  parameter Real OxygenLitersPerMeterLevel = 0.2;
  parameter Real OxygenLitersPerMeterUp = 1.5;
  parameter Real OxygenLitersPerMeterDown = 0.6;
  
  Modelica.Blocks.Interfaces.RealOutput oxygen annotation(
    Placement(visible = true, transformation(origin = {106, 0}, extent = {{-10, -10}, {10, 10}}, rotation = 0), iconTransformation(origin = {104, -2}, extent = {{-10, -10}, {10, 10}}, rotation = 0)));
  Modelica.Blocks.Interfaces.RealInput dist annotation(
    Placement(visible = true, transformation(origin = {-106, 0}, extent = {{-20, -20}, {20, 20}}, rotation = 0), iconTransformation(origin = {-98, 38}, extent = {{-20, -20}, {20, 20}}, rotation = 0)));
equation

  oxygen = dist * OxygenLitersPerMeterLevel;

annotation(
    uses(Modelica(version = "4.0.0")));
end PathOxygenEstimate;