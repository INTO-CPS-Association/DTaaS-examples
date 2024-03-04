package model.composition.skills;

import java.util.ArrayList;
import java.util.List;

import model.composition.Operation;

public class Skill extends Operation implements Cloneable {
	List<DevicePrimitive> devicePrimitives = new ArrayList<DevicePrimitive>();
	String name;

	public Skill() {
	}
	
	public String getName() {
		return this.name;
	}
	
	public void setName(String name) {
		this.name = name;
	}
	
	public List<DevicePrimitive> getDevicePrimitives() {
		return this.devicePrimitives;
	}
	
	public void setDevicePrimitives(List<DevicePrimitive> dps) {
		this.devicePrimitives = dps;
	}
	
	public void addDevicePrimitive(DevicePrimitive dp) {
		DevicePrimitive newDp = null;
		try {
			newDp = (DevicePrimitive) dp.clone();
			this.devicePrimitives.add(newDp);
		} catch (CloneNotSupportedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
			System.out.println("Error adding devprim");
		}
	}
	
	public void removeDevicePrimitive(int i) {
		this.devicePrimitives.remove(i);
	}
	
	public void removeDevicePrimitives() {
		this.devicePrimitives.clear();
	}
	
	public void executeSkill() {
		System.out.println("Executing skill");
		for (DevicePrimitive dp : this.devicePrimitives) {
			dp.executeOperation(dp.params);
		}
	}
	
	public void executeSkill(int timeOutMillis) {
		System.out.println("Executing skill");
		for (DevicePrimitive dp : this.devicePrimitives) {
			dp.executeOperation(dp.params);
			waitTime(timeOutMillis);
		}
	}
	
	private void waitTime(int milliseconds) {
		try {
			Thread.sleep(milliseconds);
		} catch (InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
	
	@Override
	public Object clone() throws CloneNotSupportedException {
		Object obj = super.clone();
		
		List<DevicePrimitive> newListDp = new ArrayList<DevicePrimitive>();
		Skill newSkill = (Skill) obj;
		
		for (DevicePrimitive dp : this.devicePrimitives) {
			newListDp.add(dp);
		}
		newSkill.setDevicePrimitives(newListDp);
		
		return newSkill;
	}
}
