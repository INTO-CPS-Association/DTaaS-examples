package dtmanager;

import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Function;

import org.eclipse.basyx.aas.manager.ConnectedAssetAdministrationShellManager;
import org.eclipse.basyx.aas.metamodel.api.IAssetAdministrationShell;
import org.eclipse.basyx.aas.metamodel.api.parts.asset.AssetKind;
import org.eclipse.basyx.aas.metamodel.connected.ConnectedAssetAdministrationShell;
import org.eclipse.basyx.aas.metamodel.map.AssetAdministrationShell;
import org.eclipse.basyx.aas.metamodel.map.descriptor.CustomId;
import org.eclipse.basyx.aas.metamodel.map.descriptor.SubmodelDescriptor;
import org.eclipse.basyx.aas.metamodel.map.parts.Asset;
import org.eclipse.basyx.aas.registration.proxy.AASRegistryProxy;
import org.eclipse.basyx.submodel.metamodel.api.ISubmodel;
import org.eclipse.basyx.submodel.metamodel.api.qualifier.qualifiable.IConstraint;
import org.eclipse.basyx.submodel.metamodel.api.submodelelement.dataelement.IProperty;
import org.eclipse.basyx.submodel.metamodel.api.submodelelement.operation.IOperation;
import org.eclipse.basyx.submodel.metamodel.connected.submodelelement.dataelement.ConnectedProperty;
import org.eclipse.basyx.submodel.metamodel.connected.submodelelement.operation.ConnectedOperation;
import org.eclipse.basyx.submodel.metamodel.map.Submodel;
import org.eclipse.basyx.submodel.metamodel.map.qualifier.qualifiable.Qualifier;
import org.eclipse.basyx.submodel.metamodel.map.submodelelement.dataelement.property.Property;
import org.eclipse.basyx.submodel.metamodel.map.submodelelement.operation.Operation;
import org.eclipse.basyx.vab.manager.VABConnectionManager;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttMessage;
import org.eclipse.paho.client.mqttv3.MqttPersistenceException;

public class DTManager {
	String name;
	public TwinSchema schema;
    public Map<String, DigitalTwin> availableTwins;
    Clock internalClock;
    
    // New input for DT Systems
    public Map<String, DigitalTwinSystem> availableTwinSystems;
    
    // New input for several schemas
    public List<TwinSchema> schemas;
    public Map<String,TwinSchema> twinToSchemaMapping;

    
	public DTManager(String name, TwinSchema schema) {
		this.name = name;
		this.schema = schema;
		this.availableTwins = new HashMap<String, DigitalTwin>();
		this.internalClock = new Clock();
		// New for DT Systems
		this.availableTwinSystems = new HashMap<String, DigitalTwinSystem>();
	}
	
	public DTManager(String name, List<TwinSchema> schemas) {
		this.name = name;
		this.schemas = schemas;
		this.schema = schemas.get(0);
		this.availableTwins = new HashMap<String, DigitalTwin>();
		this.internalClock = new Clock();
		// New for DT Systems
		this.availableTwinSystems = new HashMap<String, DigitalTwinSystem>();
		this.twinToSchemaMapping = new HashMap<String, TwinSchema>();
	}
	
	public void createDigitalTwin(String name,TwinConfiguration config) {
		DigitalTwin twin = new DigitalTwin(name,config);
		TwinSchema tmpSchema = null;
		try {
			tmpSchema = (TwinSchema) this.schema.clone();
		} catch (CloneNotSupportedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		twin.registerAttributes(tmpSchema.getAttributes());
		twin.registerOperations(tmpSchema.getOperations());
		this.availableTwins.put(name, twin);
	}
	
	public void createDigitalTwin(String name,TwinConfiguration config, TwinSchema schema) {
		DigitalTwin twin = new DigitalTwin(name,config);
		TwinSchema tmpSchema = null;
		try {
			tmpSchema = (TwinSchema) schema.clone();
		} catch (CloneNotSupportedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		twin.registerAttributes(tmpSchema.getAttributes());
		twin.registerOperations(tmpSchema.getOperations());
		this.availableTwins.put(name, twin);
		this.twinToSchemaMapping.put(name, schema);
	}
	
	// New input for DT Systems
	public void createDigitalTwinSystem(String systemName,List<String> twins, ComponentConfiguration config, String coeFilename,String outputPath) {
		Map<String,DigitalTwin> digitalTwins = new HashMap<String,DigitalTwin>();
		for(String twin : twins){
			DigitalTwin currentTwin = this.availableTwins.get(twin);
			digitalTwins.put(twin,currentTwin);
		}
		DigitalTwinSystem dtSystem = new DigitalTwinSystem(systemName,digitalTwins,config, coeFilename, outputPath);
		this.availableTwinSystems.put(systemName, dtSystem);
	}

	void deleteTwin(String name){
		this.availableTwins.remove(name);
	}
	
	public void copyTwin(String nameFrom, String nameTo, Clock time) {
		if(time != null && time.getNow() > getTimeFrom(nameFrom).getNow()) {
			this.waitUntil(time);
		}
		
		DigitalTwin to = this.availableTwins.get(nameTo);
		DigitalTwin from = this.availableTwins.get(nameFrom);
		for(Property att : this.schema.getAttributes()){
			copyAttributeValue(to, att.getIdShort(), from, att.getIdShort());
		}
		from.setTime(time);
	}
	
	void copyAttributeValue(DigitalTwin from, String fromAttribute, DigitalTwin to, String toAttribute){
		Object value = from.getAttributeValue(fromAttribute);
		to.setAttributeValue(toAttribute, value);
	}
	
	void cloneTwin(String nameFrom, String nameTo, Clock time){
		if(time != null && time.getNow() > getTimeFrom(nameFrom).getNow()) {
			this.waitUntil(time);
		}
		
		DigitalTwin from = this.availableTwins.get(nameFrom);
		this.availableTwins.put(nameTo, from);
		copyTwin(nameTo, nameFrom, null);
	}
	
	public void executeOperationOnTwins(String opName, List<?> arguments,List<String> twins) {
		List<String> twinsToCheck = twins;
		if(twinsToCheck == null) {
			for(String temp : this.availableTwins.keySet()) {
				twinsToCheck.add(temp);
			}
		}
		for(String twin : twinsToCheck){
			DigitalTwin currentTwin = this.availableTwins.get(twin);
			currentTwin.executeOperation(opName, arguments);
		}
	}
	
	public void executeOperation(String opName, List<?> arguments,String twinName) {
		DigitalTwin twin = this.availableTwins.get(twinName);
		twin.executeOperation(opName, arguments);
	}
	
	public void executeOperationAt(String opName, List<?> arguments, String twinName, Clock time) {
		if(time != null && time.getNow() > getTimeFrom(twinName).getNow()) {
			this.waitUntil(time);
		}
		DigitalTwin twin = this.availableTwins.get(twinName);
		twin.executeOperation(opName, arguments);
	}
	
	public Object getAttributeValue(String attName, String twinName) {
		DigitalTwin twin = this.availableTwins.get(twinName);
		Object value = twin.getAttributeValue(attName);
		return value;
	}
	
	public Object getAttributeValueAt(String attName, String twinName, Clock time) {
		if(time != null && time.getNow() > getTimeFrom(twinName).getNow()) {
			this.waitUntil(time);
		}
		DigitalTwin twin = this.availableTwins.get(twinName);
		Object value = twin.getAttributeValue(attName);
		return value;
	}
	
	public List<Object> getAttributeValues(String attName, List<String> twins) {
		List<String> twinsToCheck = twins;
		List<Object> values = null;
		if(twinsToCheck == null) {
			for(String temp : this.availableTwins.keySet()) {
				twinsToCheck.add(temp);
			}
		}
		for(String twin : twinsToCheck){
			DigitalTwin currentTwin = this.availableTwins.get(twin);
			Object value = currentTwin.getAttributeValue(attName);
			values.add(value);
		}
		return values;
	}
	
	public void setAttributeValue(String attrName, Object val, String twinName) {
		DigitalTwin twin = this.availableTwins.get(twinName);
		twin.setAttributeValue(attrName, val);
	}
	
	public void setAttributeValueAt(String attrName, Object val, String twinName, Clock time) {
		if(time != null && time.getNow() > getTimeFrom(twinName).getNow()) {
			this.waitUntil(time);
		}
		DigitalTwin twin = this.availableTwins.get(twinName);
		twin.setAttributeValue(attrName, val);
	}
	
	public void registerOperations(String twinName, List<Operation> operations) {
		DigitalTwin twin = this.availableTwins.get(twinName);
		twin.registerOperations(operations);
	}
	
	public void registerAttributes(String twinName, List<Property> attributes) {
		DigitalTwin twin = this.availableTwins.get(twinName);
		twin.registerAttributes(attributes);	
	}
	
	
	// TIMING 
	public Clock getTimeFrom(String twinName) {
		DigitalTwin twin = this.availableTwins.get(twinName);
		return twin.getTime();
	}
		
	private void waitUntil(Clock time) {
		while(this.internalClock.getNow() != time.getNow()) {
			//Waits until
		}
	}
	
	public void setClock(int value) {
		this.internalClock.setClock(value);
	}
	
	/***** New for DT Systems *****/
	public void executeOperationOnSystem(String opName, List<?> arguments,String systemName) {
		DigitalTwinSystem twinSystem = this.availableTwinSystems.get(systemName);
		twinSystem.executeOperation(opName, arguments);
	}
	
	public void setSystemAttributeValue(String attrName, Object val, String systemName) {
		DigitalTwinSystem twinSystem = this.availableTwinSystems.get(systemName);
		twinSystem.setAttributeValue(attrName, val);
	}
	
	public void setSystemAttributeValue(String attrName, Object val, String systemName, String twinName) {
		DigitalTwinSystem twinSystem = this.availableTwinSystems.get(systemName);
		twinSystem.setAttributeValue(attrName, val, twinName);
	}
	
	public void setSystemAttributeValues(List<String> attrNames, List<Object> values, String systemName) {
		DigitalTwinSystem twinSystem = this.availableTwinSystems.get(systemName);
		twinSystem.setAttributeValues(attrNames, values);
	}
	
	public void setSystemAttributeValuesAt(List<String> attrNames, List<Object> values, String systemName, Clock time) {
		DigitalTwinSystem twinSystem = this.availableTwinSystems.get(systemName);
		twinSystem.setClock(time.getNow());
		twinSystem.setAttributeValues(attrNames, values);
	}
	
	public Object getSystemAttributeValue(String attrName, String systemName) {
		DigitalTwinSystem twinSystem = this.availableTwinSystems.get(systemName);
		twinSystem.setClock(this.internalClock.getNow());
		Object value = twinSystem.getAttributeValue(attrName);
		return value;
	}
	
	public void setSystemAttributeValueAt(String attrName, Object val, String systemName, String twinName, Clock time) {
		DigitalTwinSystem twinSystem = this.availableTwinSystems.get(systemName);
		twinSystem.setClock(time.getNow());
		twinSystem.setAttributeValue(attrName, val, twinName);
	}
	
	public Object getSystemAttributeValueAt(String attrName, String systemName, Clock time) {
		DigitalTwinSystem twinSystem = this.availableTwinSystems.get(systemName);
		twinSystem.setClock(time.getNow());
		Object value = twinSystem.getAttributeValue(attrName);
		return value;
	}
	
	public Object getSystemAttributeValueAt(String attrName, String systemName, int entry) {
		DigitalTwinSystem twinSystem = this.availableTwinSystems.get(systemName);
		Object value = twinSystem.getAttributeValue(attrName,entry);
		return value;
	}
	
	public Object getSystemAttributeValueAt(String attrName, String systemName, String twinName, int entry) {
		DigitalTwinSystem twinSystem = this.availableTwinSystems.get(systemName);
		Object value = twinSystem.getAttributeValue(attrName, entry, twinName) ;
		return value;
	}
	
	public Object getSystemAttributeValue(String attrName, String systemName, String twinName) {
		DigitalTwinSystem twinSystem = this.availableTwinSystems.get(systemName);
		twinSystem.setClock(this.internalClock.getNow());
		Object value = twinSystem.getAttributeValue(attrName,twinName);
		return value;
	}
	
	/***** Get Knowledge graphs - Systems and individual DTs *****/
	//TBD
}
