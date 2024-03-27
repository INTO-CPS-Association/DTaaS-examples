package endpoints;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.javafmi.wrapper.Simulation;

import config.TwinConfiguration;
import model.Clock;
import model.composition.Operation;


public class FMIEndpoint implements Endpoint {
	
	private String twinName = "";
	private double stepSize = 0.0;
	private TwinConfiguration twinConfig;
	private String fmuPath;
	
	public Simulation simulation;
	private Map<String,Object> registeredAttributes;
	private Map<String,Operation> registeredOperations;
	private Clock clock;
	
	public FMIEndpoint(String twinName, TwinConfiguration config) {
		this.twinName = twinName;
		this.twinConfig = config;
		this.fmuPath = config.conf.getString("fmi.file_path");
		this.stepSize = config.conf.getDouble("fmi.step_size");
		this.simulation = new Simulation(this.fmuPath);
		this.clock = new Clock();
		
		this.registeredAttributes = new HashMap<String,Object>();
		this.registeredOperations = new HashMap<String,Operation>();
	}
	
	public List<Object> getAttributeValues(List<String> variables) {
		Object value = null;
		List<Object> values = new ArrayList<Object>();
		for(String var : variables) {
			value = simulation.read(var).asEnumeration();
			values.add(value);
		}
		return values;
	}
	
	public Object getAttributeValue(String variable) {
		String variableAlias = mapAlias(variable);
		double value = simulation.read(variableAlias).asDouble();
		return value;
	}
	
	public boolean setAttributeValues(List<String> variables,List<Object> values) {
		for(String var : variables) {
			int index = variables.indexOf(var);
			String mappedVariable = mapAlias(var);
			simulation.write(mappedVariable).with(Double.valueOf(values.get(index).toString()));
		}
		return true;
	}
	
	public boolean setAttributeValue(String variable,Object value) {
		String mappedVariable = mapAlias(variable);
		simulation.write(mappedVariable).with(Double.valueOf(value.toString()));
		return true;
	}
	
	public void initializeSimulation(double startTime) {
		this.simulation.init(startTime);
	}
	
	private void terminateSimulation() {
		this.simulation.terminate();
	}
	
	private void doStep(double stepSize) {
		this.simulation.doStep(stepSize);
	}
	
	
	private String mapAlias(String in) {
		String out = this.twinConfig.conf.getString("fmi.aliases." + in);
		return out;
	}

	
	public void registerOperation(String name, Operation op) {
		this.registeredOperations.put(name,op);		
	}

	
	public void registerAttribute(String name, Object obj) {
		this.registeredAttributes.put(name,obj);
	}

	
	public boolean executeOperation(String opName, List<?> arguments) {
		if (opName.equals("doStep")) {
			if(arguments == null) {
				
			}else {
				this.stepSize = (double) arguments.get(0);
				if (arguments.size() > 1) {
					Map<String,Double> args = (Map<String, Double>) arguments.get(1);
					for (Map.Entry<String, Double> entry : args.entrySet()) {
					    this.setAttributeValue(entry.getKey(), entry.getValue());
					}
				}
			}
			this.doStep(this.stepSize);
		} else if(opName.equals("terminateSimulation")) {
			this.terminateSimulation();
		} else if(opName.equals("initializeSimulation")) {
			double startTime = (double) arguments.get(0);
			this.initializeSimulation(startTime);
		}
		return true;
	}

	
	public Object getAttributeValue(String attrName, String twinName) {
		// Not applicable
		return null;
	}

	
	public boolean setAttributeValue(String attrName, Object val, String twinName) {
		// Not applicable
		return false;
	}

	
	public void setClock(Clock value) {
		this.clock = value;
		
	}

	
	public Clock getClock() {
		return this.clock;
	}

	
	public Object getAttributeValue(String attrName, int entry) {
		// TODO Auto-generated method stub
		return null;
	}

	
	public Object getAttributeValue(String attrName, int entry, String twinName) {
		// TODO Auto-generated method stub
		return null;
	}
	
	public String getTwinName() {
		return twinName;
	}
	
}
