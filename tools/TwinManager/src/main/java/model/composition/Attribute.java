package model.composition;

public class Attribute {
	String name;
	String type;
	Object value;
	
	public Attribute() {
		value = new Object();
	}
	
	public String getName() {
		return this.name;
	}
	
	public void setName(String name) {
		this.name = name;
	}
	
	public void setAttributeValue(Object value) {
		this.value = value;
	}
	
	public Object getAttributeValue() {
		return this.value;
	}
}
