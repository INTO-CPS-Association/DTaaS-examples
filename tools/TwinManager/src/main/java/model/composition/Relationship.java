package model.composition;

public class Relationship {
	String name;
	Object fromObject;
	Object toObject;
	Object value;
	String valueString;

	
	public Relationship() {
	}
	
	public String getName() {
		return this.name;
	}
	
	public void setName(String name) {
		this.name = name;
	}
	
	public Object getFromObject() {
		return this.fromObject;
	}
	
	public void setFromObject(Object fromObject) {
		this.fromObject = fromObject;
	}
	
	public Object getToObject() {
		return this.toObject;
	}
	
	public void setToObject(Object toObject) {
		this.toObject = toObject;
	}
	
	public Object getValue() {
		return this.value;
	}
	
	public void setValue(Object value) {
		this.value = value;
	}
	
	public String getValueString() {
		return this.valueString;
	}
	
	public void setValueString(String valueString) {
		this.valueString = valueString;
	}

}
