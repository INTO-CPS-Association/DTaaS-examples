package dtmanager;

import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Set;

import com.typesafe.config.Config;
import com.typesafe.config.ConfigValue;

public class DigitalTwinSystem {
	Map<String,DigitalTwin> digitalTwins;
	ComponentConfiguration config;
	String coeFilename;
	Endpoint endpoint;
	String systemName;
	String outputPath;
	
	public DigitalTwinSystem(String systemName, Map<String,DigitalTwin> twins,ComponentConfiguration config, String coeFilename, String outputPath) {
		this.digitalTwins = twins;
		this.config = config;
		this.coeFilename = coeFilename;
		this.systemName = systemName;
		this.outputPath = outputPath;
		//this.endpoint = new MaestroEndpoint("spec.mabl","results_cosim"); //with mabl
		this.endpoint = new MaestroEndpoint(this.config,this.coeFilename,this.outputPath); //with json config
		this.setConnections();
	}
	
	public Object executeOperation(String opName, List<?> arguments) {
		// Maestro Endpoint
		this.endpoint.executeOperation(opName, arguments);
		// Only valid for FMIEndpoints
		for (Map.Entry<String, DigitalTwin> entry : digitalTwins.entrySet()) {
			DigitalTwin twin = entry.getValue();
		    if(twin.endpoint instanceof FMIEndpoint) {
		    	FMIEndpoint tmpEndpoint = (FMIEndpoint) twin.endpoint;
		    	twin.executeOperation(opName, arguments);
		    }
		}
		return null;
	}
	
	public void setAttributeValue(String attrName, Object val) {
		this.endpoint.setAttributeValue(attrName, val);
	}
	
	public void setAttributeValue(String attrName, Object val, String twinName) {
		this.digitalTwins.get(twinName).attributes.put(attrName, val);
		this.endpoint.setAttributeValue(attrName, val, twinName);
	}
	
	public Object getAttributeValue(String attrName) {
		Object value = this.endpoint.getAttributeValue(attrName);
		return value;
	}
	
	public Object getAttributeValue(String attrName, String twinName) {
		Object value = this.endpoint.getAttributeValue(attrName, twinName);
		this.digitalTwins.get(twinName).attributes.put(attrName, value);
		return value;
	}
	
	public void setAttributeValues(List<String> attrNames, List<Object> values) {
		this.endpoint.setAttributeValues(attrNames, values);
	}
	
	public Object getAttributeValues(List<String> attrNames) {
		return this.endpoint.getAttributeValues(attrNames);
	}
	
	public Object getAttributeValue(String attrName, int entry) {
		return this.endpoint.getAttributeValue(attrName, entry);
	}
	
	public Object getAttributeValue(String attrName, int entry, String twinName) {
		Object value = this.endpoint.getAttributeValue(attrName, entry, twinName);
		this.digitalTwins.get(twinName).attributes.put(attrName, value);
		return value;
	}
	
	
	
	private void setConnections() {
		String input = "";
		String output = "";
		Config innerConf = this.config.conf.getConfig("connections");
		Set<Entry<String, ConfigValue>> entries = innerConf.root().entrySet();

		for (Map.Entry<String, ConfigValue> entry: entries) {
			input = entry.getKey();
		    output = entry.getValue().render();
		    //Fix io
		    //System.out.println(input);
		    //System.out.println(output);
		}
	}
	
	private String mapAlias(String in) {
		String out = "";
		try {
			out = this.config.conf.getString("aliases." + in);
		}catch(Exception e) {
			out = in;
		}
		return out;
	}
	
	public boolean validate() {
		return true;
	}
	
	public void synchronize() {
		
	}
	
	public void setClock(int value) {
		this.endpoint.setClock(value);
	}
	
	public int getClock() {
		return this.endpoint.getClock();
	}

}
