package model;

public class Parameter {

	String name;
	String value;

	public Parameter(){}
	
	public Parameter(String name, String value) {
		this.name = name;
		this.value = value;
	}
	
	public String getName() {
		return this.name;
	}
	
	public String getValue() {
		return this.value;
	}
}
