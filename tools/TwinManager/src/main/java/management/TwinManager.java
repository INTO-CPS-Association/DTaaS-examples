package management;


import java.util.HashMap;
import java.util.List;
import java.util.Map;


import config.ComponentConfiguration;
import config.TwinConfiguration;
import model.Clock;
import model.Twin;
import model.TwinSchema;
import model.composition.Attribute;
import model.composition.Operation;
import model.TwinSystem;

public class TwinManager {
	String name;
	public TwinSchema schema; // default schema
    public Map<String, Twin> availableTwins;
    Clock clock;
    
    // Twin Systems
    public Map<String, TwinSystem> availableTwinSystems;
    
    // Multiple schemas
    @Deprecated
    public List<TwinSchema> schemas;
    public Map<String,TwinSchema> twinSchemaMapping;
    
    public void addSchema(String twinClass, TwinSchema schema) {
    	twinSchemaMapping.put(twinClass, schema);
    	this.schema = schema;
    }
    
    public Map<String,TwinSchema> getSchemas(){
    	return this.twinSchemaMapping;
    }

    public TwinManager(String name) {
		this.name = name;
		this.schema = new TwinSchema();
		this.availableTwins = new HashMap<String, Twin>();
		this.clock = new Clock();
		this.availableTwinSystems = new HashMap<String, TwinSystem>();
		this.twinSchemaMapping = new HashMap<String, TwinSchema>();
	}
    
	public TwinManager(String name, TwinSchema schema) {
		this.name = name;
		this.schema = schema;
		this.availableTwins = new HashMap<String, Twin>();
		this.clock = new Clock();
		this.availableTwinSystems = new HashMap<String, TwinSystem>();
		this.twinSchemaMapping = new HashMap<String, TwinSchema>();
		this.twinSchemaMapping.put("default", schema);
	}
	
	@Deprecated
	public TwinManager(String name, List<TwinSchema> schemas) {
		this.name = name;
		this.schemas = schemas;
		this.schema = schemas.get(0);
		this.availableTwins = new HashMap<String, Twin>();
		this.clock = new Clock();
		this.availableTwinSystems = new HashMap<String, TwinSystem>();
		this.twinSchemaMapping = new HashMap<String, TwinSchema>();
	}
	
	public void createTwin(String name,TwinConfiguration config) {
		Twin twin = new Twin(name,config);
		twin.registerAttributes(schema.getAttributes());
		twin.registerOperations(schema.getOperations());
		this.availableTwins.put(name, twin);
	}
	
	@Deprecated
	public void createTwin(String name,TwinConfiguration config, TwinSchema schema) {
		Twin twin = new Twin(name,config);
		twin.registerAttributes(schema.getAttributes());
		twin.registerOperations(schema.getOperations());
		this.availableTwins.put(name, twin);
		this.twinSchemaMapping.put(name, schema);
	}
	
	public void createTwin(String name,TwinConfiguration config, String schemaClassName) {
		Twin twin = new Twin(name,config);
		TwinSchema schema = this.twinSchemaMapping.get(schemaClassName);
		twin.registerAttributes(schema.getAttributes());
		twin.registerOperations(schema.getOperations());
		this.availableTwins.put(name, twin);
	}
	
	public void createTwinSystem(String systemName,List<String> twins, ComponentConfiguration config, String coeFilename,String outputPath) {
		Map<String,Twin> twinsForSystem = new HashMap<String,Twin>();
		for(String twin : twins){
			Twin currentTwin = this.availableTwins.get(twin);
			twinsForSystem.put(twin,currentTwin);
		}
		TwinSystem dtSystem = new TwinSystem(systemName,twinsForSystem,config, coeFilename, outputPath);
		this.availableTwinSystems.put(systemName, dtSystem);
	}

	void deleteTwin(String name){
		this.availableTwins.remove(name);
	}
	
	public void copyTwin(String nameFrom, String nameTo, Clock time) {
		if(time != null && time.getNow() > getTimeFrom(nameFrom).getNow()) {
			this.waitUntil(time);
		}
		
		Twin to = this.availableTwins.get(nameTo);
		Twin from = this.availableTwins.get(nameFrom);
		for(Attribute att : this.schema.getAttributes()){
			copyAttributeValue(to, att.getName(), from, att.getName());
		}
		from.setTime(time);
	}
	
	void copyAttributeValue(Twin from, String fromAttribute, Twin to, String toAttribute){
		Object value = from.getAttributeValue(fromAttribute);
		to.setAttributeValue(toAttribute, value);
	}
	
	void copyAttributeValues(Twin from, Twin to){
		for (Map.Entry<String,Object>  att : from.getAttributes().entrySet()) {
			to.setAttributeValue(att.getKey(), att.getValue());
		}
	}
	
	void synchronizeTwin(Twin from, Twin to) {
		copyAttributeValues(from,to);
	}
	
	void cloneTwin(String nameFrom, String nameTo, Clock time){
		if(time != null && time.getNow() > getTimeFrom(nameFrom).getNow()) {
			this.waitUntil(time);
		}
		
		Twin from = this.availableTwins.get(nameFrom);
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
			Twin currentTwin = this.availableTwins.get(twin);
			currentTwin.executeOperation(opName, arguments);
		}
	}
	
	public void executeOperation(String opName, List<?> arguments,String twinName) {
		Twin twin = this.availableTwins.get(twinName);
		twin.executeOperation(opName, arguments);
	}
	
	public void executeOperationAt(String opName, List<?> arguments, String twinName, Clock time) {
		if(time != null && time.getNow() > getTimeFrom(twinName).getNow()) {
			this.waitUntil(time);
		}
		Twin twin = this.availableTwins.get(twinName);
		twin.executeOperation(opName, arguments);
	}
	
	public Object getAttributeValue(String attName, String twinName) {
		Twin twin = this.availableTwins.get(twinName);
		Object value = twin.getAttributeValue(attName);
		return value;
	}
	
	public Object getAttributeValueAt(String attName, String twinName, Clock time) {
		if(time != null && time.getNow() > getTimeFrom(twinName).getNow()) {
			this.waitUntil(time);
		}
		Twin twin = this.availableTwins.get(twinName);
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
			Twin currentTwin = this.availableTwins.get(twin);
			Object value = currentTwin.getAttributeValue(attName);
			values.add(value);
		}
		return values;
	}
	
	public void setAttributeValue(String attrName, Object val, String twinName) {
		Twin twin = this.availableTwins.get(twinName);
		twin.setAttributeValue(attrName, val);
	}
	
	public void setAttributeValueAt(String attrName, Object val, String twinName, Clock time) {
		if(time != null && time.getNow() > getTimeFrom(twinName).getNow()) {
			this.waitUntil(time);
		}
		Twin twin = this.availableTwins.get(twinName);
		twin.setAttributeValue(attrName, val);
	}
	
	public void registerOperations(String twinName, List<Operation> operations) {
		Twin twin = this.availableTwins.get(twinName);
		twin.registerOperations(operations);
	}
	
	public void registerAttributes(String twinName, List<Attribute> attributes) {
		Twin twin = this.availableTwins.get(twinName);
		twin.registerAttributes(attributes);	
	}
	
	
	// TIMING 
	public Clock getTimeFrom(String twinName) {
		Twin twin = this.availableTwins.get(twinName);
		return twin.getTime();
	}
		
	private void waitUntil(Clock time) {
		while(this.clock.getNow() != time.getNow()) {
			//Waits until
		}
	}
	
	public void setClock(int value) {
		this.clock.setClock(value);
	}
	
	public Clock getClock() {
		return this.clock;
	}
	
	/***** New for DT Systems *****/
	public void executeOperationOnSystem(String opName, List<?> arguments,String systemName) {
		TwinSystem twinSystem = this.availableTwinSystems.get(systemName);
		twinSystem.executeOperation(opName, arguments);
	}
	
	public void setSystemAttributeValue(String attrName, Object val, String systemName) {
		TwinSystem twinSystem = this.availableTwinSystems.get(systemName);
		twinSystem.setAttributeValue(attrName, val);
	}
	
	public void setSystemAttributeValue(String attrName, Object val, String systemName, String twinName) {
		TwinSystem twinSystem = this.availableTwinSystems.get(systemName);
		twinSystem.setAttributeValue(attrName, val, twinName);
	}
	
	public void setSystemAttributeValues(List<String> attrNames, List<Object> values, String systemName) {
		TwinSystem twinSystem = this.availableTwinSystems.get(systemName);
		twinSystem.setAttributeValues(attrNames, values);
	}
	
	public void setSystemAttributeValuesAt(List<String> attrNames, List<Object> values, String systemName, Clock time) {
		TwinSystem twinSystem = this.availableTwinSystems.get(systemName);
		twinSystem.setClock(time.getNow());
		twinSystem.setAttributeValues(attrNames, values);
	}
	
	public Object getSystemAttributeValue(String attrName, String systemName) {
		TwinSystem twinSystem = this.availableTwinSystems.get(systemName);
		twinSystem.setClock(this.clock.getNow());
		Object value = twinSystem.getAttributeValue(attrName);
		return value;
	}
	
	public void setSystemAttributeValueAt(String attrName, Object val, String systemName, String twinName, Clock time) {
		TwinSystem twinSystem = this.availableTwinSystems.get(systemName);
		twinSystem.setClock(time.getNow());
		twinSystem.setAttributeValue(attrName, val, twinName);
	}
	
	public Object getSystemAttributeValueAt(String attrName, String systemName, Clock time) {
		TwinSystem twinSystem = this.availableTwinSystems.get(systemName);
		twinSystem.setClock(time.getNow());
		Object value = twinSystem.getAttributeValue(attrName);
		return value;
	}
	
	public Object getSystemAttributeValueAt(String attrName, String systemName, int entry) {
		TwinSystem twinSystem = this.availableTwinSystems.get(systemName);
		Object value = twinSystem.getAttributeValue(attrName,entry);
		return value;
	}
	
	public Object getSystemAttributeValueAt(String attrName, String systemName, String twinName, int entry) {
		TwinSystem twinSystem = this.availableTwinSystems.get(systemName);
		Object value = twinSystem.getAttributeValue(attrName, entry, twinName) ;
		return value;
	}
	
	public Object getSystemAttributeValue(String attrName, String systemName, String twinName) {
		TwinSystem twinSystem = this.availableTwinSystems.get(systemName);
		twinSystem.setClock(this.clock.getNow());
		Object value = twinSystem.getAttributeValue(attrName,twinName);
		return value;
	}

}
