package model;

import model.TwinSchema;
import model.composition.Attribute;
import model.composition.Operation;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;

import config.TwinConfiguration;
import endpoints.Endpoint;
import endpoints.MQTTEndpoint;
import endpoints.RabbitMQEndpoint;
import endpoints.FMIEndpoint;


public class Twin {
	public Map<String,Object> attributes;
	public Map<String,Operation> operations;
	private TwinConfiguration config;
	private String name;
	private Endpoint endpoint;
	private Clock clock;
	private TwinSchema schema;
	
	public String getName() {
		return name;
	}
	
	public Endpoint getEndpoint() {
		return this.endpoint;
	}
	
	public void setEndpoint(Endpoint endpoint) {
		this.endpoint = endpoint;
	}

	public Twin(){
		this.attributes = new HashMap<String,Object>();
		this.operations = new HashMap<String,Operation>();
		this.clock = new Clock();
	}

	public Twin(String name, TwinSchema definition){
		this.attributes = new HashMap<String,Object>();
		this.operations = new HashMap<String,Operation>();
		this.name = name;
		this.schema = definition;
		this.clock = new Clock();
	}
	
	public Twin(String name, TwinConfiguration config) {
		this.name = name;
		this.config = config;
		this.attributes = new HashMap<String,Object>();
		this.operations = new HashMap<String,Operation>();
		this.clock = new Clock();
		
		if (config.conf.hasPath("rabbitmq")) {
			this.endpoint = new RabbitMQEndpoint(name,config);
		} else if (config.conf.hasPath("mqtt")) {
			this.endpoint = new MQTTEndpoint(name,config);
		} else if (config.conf.hasPath("fmi")){
			this.endpoint = new FMIEndpoint(name,config);
			List<Double> args = new ArrayList<Double>();
			args.add(0.0);
			this.endpoint.executeOperation("initializeSimulation",args);
		} else if(config.conf.hasPath("henshin")) {}
	}
	
	public Twin(String name, TwinSchema definition, TwinConfiguration config) {
		this.name = name;
		this.config = config;
		this.attributes = new HashMap<String,Object>();
		this.operations = new HashMap<String,Operation>();
		this.schema = definition;
		this.clock = new Clock();
		
		if (config.conf.hasPath("rabbitmq")) {
			this.endpoint = new RabbitMQEndpoint(name,config);
		} else if (config.conf.hasPath("mqtt")) {
			this.endpoint = new MQTTEndpoint(name,config);
		} else if (config.conf.hasPath("fmi")){
			this.endpoint = new FMIEndpoint(name,config);
			List<Double> args = new ArrayList<Double>();
			args.add(0.0);
			this.endpoint.executeOperation("initializeSimulation",args);
		} else if(config.conf.hasPath("henshin")) {}
	}
	
	public Map<String,Object> getAttributes(){
		return this.attributes;
	}
	
	public Object getAttribute(String attrName){
		return this.attributes.get(attrName);
	}
	
	public Map<String,Operation> getOperations(){
		return this.operations;
	}
	
	public TwinSchema getSchema() {
		return this.schema;
	}
	
	public TwinConfiguration getConfiguration() {
		return this.config;
	}

	public Twin getEmptyClone() {
		Twin result = new Twin(this.name, this.config);
		return result;
	}

	public void registerOperations(List<Operation> operations) {
		for (Operation op : operations) {
			this.attributes.put(op.getName(), new Object());
			this.endpoint.registerOperation(this.name,op);
		}
	}
	
	public void registerAttributes(List<Attribute> attributes) {
		for (Attribute attr : attributes) {
			this.attributes.put(attr.getName(), new Object());
			this.endpoint.registerAttribute(attr.getName(),this.getAttribute(attr.getName())); 
		}		
		
	}

	public Object getAttributeValue(String attrName) {
		if (this.endpoint instanceof RabbitMQEndpoint) {
			Object value = null;
			try {
				value = this.endpoint.getAttributeValue(attrName);
				this.attributes.put(attrName, value);
			} catch(Exception e) {}
		} else if(this.endpoint instanceof MQTTEndpoint) {
			Object value = null;
			try {
				value = this.endpoint.getAttributeValue(attrName);
				this.attributes.put(attrName, value);
			} catch(Exception e) {}
			
		}
		else if(this.endpoint instanceof FMIEndpoint) {
			Object value = this.endpoint.getAttributeValue(attrName);
			try {
				this.attributes.put(attrName,value);
			} catch(Exception e) {}
		}
		return this.getAttribute(attrName);		
	}
	
	public boolean setAttributeValue(String attrName, Object val) {
		this.attributes.put(attrName,val);
		if (this.endpoint instanceof RabbitMQEndpoint) {
			this.endpoint.setAttributeValue(attrName, val);	
		} else if (this.endpoint instanceof MQTTEndpoint) {
			this.endpoint.setAttributeValue(attrName, val);
		}		
		else if (this.endpoint instanceof FMIEndpoint) {
			this.endpoint.setAttributeValue(attrName, Double.valueOf(val.toString()));
		}
		return true;
	}

	public boolean executeOperation(String opName, List<?> arguments) {
		if (this.endpoint instanceof RabbitMQEndpoint) {
			if (arguments == null) {
				this.endpoint.executeOperation(opName, null);
			}else {
				this.endpoint.executeOperation(opName, arguments);
			}
		} else if (this.endpoint instanceof MQTTEndpoint) {
			if (arguments == null) {
				this.endpoint.executeOperation(opName, null);
			}else {
				this.endpoint.executeOperation(opName, arguments);
			}
		} else if(this.endpoint instanceof FMIEndpoint) {
			this.endpoint.executeOperation(opName, arguments);
		}
		return true;
	}

	public Clock getTime() {
		return this.clock;
	}

	public void setTime(Clock clock) {
		this.clock = clock;
	}





}
