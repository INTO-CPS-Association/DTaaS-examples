package endpoints;


import java.util.HashMap;
import java.util.List;

import config.TwinConfiguration;
import model.Clock;
import model.composition.Operation;


public interface Endpoint {
	public TwinConfiguration config = null;
	
	public Clock clock = null;

	public void registerOperation(String name, Operation op);

	public void registerAttribute(String name, Object obj);

	public List<Object> getAttributeValues(List<String> variables);
	
	public Object getAttributeValue(String variable);
	
	public boolean setAttributeValues(List<String> variables,List<Object> values);
	
	public boolean setAttributeValue(String variable,Object value);
	
	public boolean executeOperation(String opName, List<?> arguments);

	/***** Specific for MaestroEndpoint *****/
	public Object getAttributeValue(String attrName, String twinName);
	
	public Object getAttributeValue(String attrName, int entry);
	
	public Object getAttributeValue(String attrName, int entry, String twinName);
	

	public boolean setAttributeValue(String attrName, Object val, String twinName);
	/***** End Specific for MaestroEndpoint *****/

	public void setClock(Clock clock);

	public Clock getClock();
	
}
