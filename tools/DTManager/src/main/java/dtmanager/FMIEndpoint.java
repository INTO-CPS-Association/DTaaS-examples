package dtmanager;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.eclipse.basyx.submodel.metamodel.connected.submodelelement.dataelement.ConnectedProperty;
import org.eclipse.basyx.submodel.metamodel.connected.submodelelement.operation.ConnectedOperation;
import org.eclipse.basyx.submodel.metamodel.map.submodelelement.dataelement.property.Property;
import org.eclipse.basyx.submodel.metamodel.map.submodelelement.operation.Operation;
import org.javafmi.wrapper.Simulation;



public class FMIEndpoint implements Endpoint {

	private double stepSize = 3.0;
	private TwinConfiguration twinConfig;
	private String fmuPath;
	
	public Simulation simulation;
	Map<String,Object> registeredAttributes;
	private ArrayList<Operation> registeredOperations;
	
	@SuppressWarnings("static-access")
	public FMIEndpoint(TwinConfiguration config) {
		this.twinConfig = config;
		this.fmuPath = config.conf.getString("fmi.file_path");
		this.stepSize = config.conf.getDouble("fmi.step_size");
		simulation = new Simulation(this.fmuPath);
		
		this.registeredAttributes = new HashMap<String,Object>();		
		this.registeredOperations = new ArrayList<Operation>();
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
	
	public void setAttributeValues(List<String> variables,List<Object> values) {
		for(String var : variables) {
			int index = variables.indexOf(var);
			String mappedVariable = mapAlias(var);
			simulation.write(mappedVariable).with(Double.valueOf(values.get(index).toString()));
		}
	}
	
	public void setAttributeValue(String variable,Object value) {
		String mappedVariable = mapAlias(variable);
		simulation.write(mappedVariable).with(Double.valueOf(value.toString()));
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

	@Override
	public void registerOperation(String name, Operation op) {
		this.registeredOperations.add(op);		
	}

	@Override
	public void registerAttribute(String name, Object obj) {
		this.registeredAttributes.put(name,obj);
	}

	@Override
	public void executeOperation(String opName, List<?> arguments) {
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
		
	}

	@Override
	public Object getAttributeValue(String attrName, String twinName) {
		// Not applicable
		return null;
	}

	@Override
	public void setAttributeValue(String attrName, Object val, String twinName) {
		// Not applicable
		
	}

	@Override
	public void setClock(int value) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public int getClock() {
		// TODO Auto-generated method stub
		return 0;
	}

	@Override
	public Object getAttributeValue(String attrName, int entry) {
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	public Object getAttributeValue(String attrName, int entry, String twinName) {
		// TODO Auto-generated method stub
		return null;
	}
	
}
