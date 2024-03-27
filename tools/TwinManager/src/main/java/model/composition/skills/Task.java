package model.composition.skills;

import java.util.ArrayList;
import java.util.List;

import model.composition.Operation;

public class Task extends Operation implements Cloneable {
	List<Skill> skills = new ArrayList<Skill>();
	String name;
    

	public Task() {

	}
	
	public String getName() {
		return this.name;
	}
	
	public void setName(String name) {
		this.name = name;
	}

	public List<Skill> getSkills() {
		return this.skills;
	}
	
	public void addSkill(Skill sk) {
		Skill newSk = null;
		try {
			newSk = (Skill) sk.clone();
			this.skills.add(newSk);
		} catch (CloneNotSupportedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
			System.out.println("Error adding skill");
		}
	}
	
	public void removeSkill(int i) {
		this.skills.remove(i);
	}
	
	public void removeSkills() {
		this.skills.clear();
	}
	
	public void executeTask() {
		System.out.println("Executing task");
		for (Skill skill : this.skills) {
			skill.executeSkill();
		}
	}
	
	public void executeTask(int timeOutMillis) {
		System.out.println("Executing task");
		for (Skill skill : this.skills) {
			skill.executeSkill(timeOutMillis);
		}
	}

	@Override
	public Object clone() throws CloneNotSupportedException {
		return super.clone();
	}

}
