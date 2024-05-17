package model.composition;

import java.util.List;

public class Operation {
	String name;
	List<String> parameters;
	
	public Operation() {
	}
	
	public void setName(String name) {
		this.name = name;
	}
	
	public String getName() {
		return this.name;
	}
	
	public boolean executeOperation(List<?> arguments) {
		// to be updated: callback
		return true;
	}

}
