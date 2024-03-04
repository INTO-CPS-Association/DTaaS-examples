package model.composition.skills;

import java.util.ArrayList;
import java.util.List;

import model.composition.Operation;

public class DevicePrimitive  extends Operation implements Cloneable {
	List<Object> params = new ArrayList<Object>();
	String name;

	public DevicePrimitive() {
	}
	
	public String getName() {
		return this.name;
	}
	
	public void setName(String name) {
		this.name = name;
	}
	
	public void setParams(List<Object> args) {
		this.params = args;
	}
	
	public List<Object> getParams(){
		return this.params;
	}
	
	public Object getParam(int i) {
		return this.params.get(i);
	}
	
	public void clearParams() {
		this.params.clear();
	}
	
	public void removeParam(int i) {
		this.params.remove(i);
	}
	
	@Override
	public Object clone() throws CloneNotSupportedException {
		Object obj = super.clone();
		
		List<Object> newParams = new ArrayList<Object>();
		DevicePrimitive newDP = (DevicePrimitive) obj;
		
		for (Object p : this.params) {
			newParams.add(p);
		}
		newDP.setParams(newParams);
		return newDP;
	}
}
