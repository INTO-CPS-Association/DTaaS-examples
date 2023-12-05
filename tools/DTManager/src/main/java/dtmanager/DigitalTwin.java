package dtmanager;

import java.sql.Timestamp;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.eclipse.basyx.aas.metamodel.api.IAssetAdministrationShell;
import org.eclipse.basyx.submodel.metamodel.api.ISubmodel;
import org.eclipse.basyx.submodel.metamodel.api.submodelelement.dataelement.IProperty;
import org.eclipse.basyx.submodel.metamodel.connected.submodelelement.dataelement.ConnectedProperty;
import org.eclipse.basyx.submodel.metamodel.map.submodelelement.dataelement.property.Property;
import org.eclipse.basyx.submodel.metamodel.map.submodelelement.operation.Operation;
import org.eclipse.milo.opcua.stack.core.types.builtin.DataValue;


public class DigitalTwin implements DigitalTwinInterface {
	
	public Endpoint endpoint;
	@Deprecated
	int eventCounter = 0;
	//public List<Property> attributes = null;
	public List<Operation> operations = null;
	private Clock clock;
	private String name;
	private TwinConfiguration config;
	public Map<String,Object> attributes;
	
	public DigitalTwin(String name, TwinConfiguration config) {
		this.name = name;
		this.config = config;
		this.attributes = new HashMap<String,Object>();
		if (config.conf.hasPath("rabbitmq")) {
			this.endpoint = new RabbitMQEndpoint(config);
		} else if (config.conf.hasPath("mqtt")) {
			this.endpoint = new MQTTEndpoint(config);
		} else if (config.conf.hasPath("fmi")){
			this.endpoint = new FMIEndpoint(config);
			List<Double> args = new ArrayList<Double>();
			args.add(0.0);
			this.endpoint.executeOperation("initializeSimulation",args);
		} else if(config.conf.hasPath("henshin")) {}
	}
	
	public DigitalTwin getEmptyClone() {
		DigitalTwin result = new DigitalTwin(this.name, this.config);
		return result;
	}


	public void registerOperations(List<Operation> operations) {
		this.operations = operations;
		for (Operation op : operations) {
			this.endpoint.registerOperation(this.name,op);
		}
	}
	
	public void registerAttributes(List<Property> attributes) {
		for (Property prop : attributes) {
			this.attributes.put(prop.getIdShort(), new Object());
			this.endpoint.registerAttribute(prop.getIdShort(),this.attributes.get(prop.getIdShort())); 
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
		return this.attributes.get(attrName);		
	}
	
	public void setAttributeValue(String attrName, Object val) {
		this.attributes.put(attrName,val);
		if (this.endpoint instanceof RabbitMQEndpoint) {
			this.endpoint.setAttributeValue(attrName, val);	
		} else if (this.endpoint instanceof MQTTEndpoint) {
			this.endpoint.setAttributeValue(attrName, val);
		}		
		else if (this.endpoint instanceof FMIEndpoint) {
			this.endpoint.setAttributeValue(attrName, Double.valueOf(val.toString()));
		}
		
	}
	
	@Deprecated
	public void setAttributeValueAt(String attrName, Object val, Timestamp at) {
	}

	public Object executeOperation(String opName, List<?> arguments) {
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
		return null;
	}
	
	@Deprecated
	public Object executeOperationAt(String opName, List<?> arguments, Timestamp at) {
		return null;
	}
	
	@Deprecated
	public Object executeOperationDelta(String opName, List<?> arguments, int numberOfEvents) {
		return null;
	}

	@Deprecated
	public void increaseEventCounter() {
		this.eventCounter = this.eventCounter + 1;
	}
	
	@Override
	public Clock getTime() {
		return this.clock;
	}

	@Override
	public void setTime(Clock clock) {
		this.clock = clock;
	}

	@Override
	public Object getAttributeValueAt(String attrName, Timestamp at) {
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	public List<Object> getAttributeValueAt(List<String> attrNames, Timestamp at) {
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	public DataValue getAttributeValueDelta(String attrName, int numberOfEvents) {
		// TODO Auto-generated method stub
		return null;
	}
	
}
