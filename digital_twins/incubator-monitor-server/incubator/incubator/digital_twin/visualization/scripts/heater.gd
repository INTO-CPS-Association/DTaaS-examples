extends Node3D

var material

func _ready():
	material = $Color.get("surface_material_override/0")

#func round_value(val):
#	return round(val * 100) / 100

func _on_heater_info(temp_val, is_on):
	$tempLabel.text = str(temp_val) + "°C"
	
	if is_on:
		material.albedo_color = Color.RED
	else:
		material.albedo_color = Color.GREEN
