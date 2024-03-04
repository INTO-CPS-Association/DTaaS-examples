package model.composition;

public class Behavior {
	String name;
	String type;
	String fileLocation;
	Object model; // FMU
	
	public Behavior() {
	}
	
	public String getName() {
		return this.name;
	}
	
	public void setName(String name) {
		this.name = name;
	}
	
	public String getType() {
		return this.type;
	}
	
	public void setType(String type) {
		this.type = type;
	}
	
	public String getFileLocation() {
		return this.fileLocation;
	}
	
	public void setFileLocation(String fileLocation) {
		this.fileLocation = fileLocation;
	}
	
	public Object getModel() {
		return this.model;
	}
	
	public void setModel(Object model) {
		this.model = model;
	}

}
