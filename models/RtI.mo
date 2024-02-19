model RtI
  Modelica.Blocks.Math.RealToInteger realToInteger annotation(
    Placement(transformation(origin = {20, 0}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Gain gain(k = 100)  annotation(
    Placement(transformation(origin = {-40, 0}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Interfaces.RealInput u annotation(
    Placement(transformation(origin = {-120, 0}, extent = {{-20, -20}, {20, 20}}), iconTransformation(origin = {-120, 0}, extent = {{-20, -20}, {20, 20}})));
  Modelica.Blocks.Interfaces.IntegerOutput y annotation(
    Placement(transformation(origin = {110, 0}, extent = {{-10, -10}, {10, 10}}), iconTransformation(origin = {110, 0}, extent = {{-10, -10}, {10, 10}})));
equation
  connect(gain.y, realToInteger.u) annotation(
    Line(points = {{-28, 0}, {8, 0}}, color = {0, 0, 127}));
  connect(u, gain.u) annotation(
    Line(points = {{-120, 0}, {-52, 0}}, color = {0, 0, 127}));
  connect(realToInteger.y, y) annotation(
    Line(points = {{32, 0}, {110, 0}}, color = {255, 127, 0}));

annotation(
    uses(Modelica(version = "4.0.0")),
  Icon(graphics = {Rectangle(extent = {{-100, 100}, {100, -100}})}));
end RtI;