package dtmanager;

import java.util.HashMap;
import java.util.List;

import org.eclipse.basyx.submodel.metamodel.connected.submodelelement.dataelement.ConnectedProperty;
import org.eclipse.basyx.submodel.metamodel.connected.submodelelement.operation.ConnectedOperation;
import org.eclipse.basyx.submodel.metamodel.map.submodelelement.dataelement.property.Property;
import org.eclipse.basyx.submodel.metamodel.map.submodelelement.operation.Operation;

public interface Endpoint {
	public TwinConfiguration config = null;
	
	public int clock = 0;

	public void registerOperation(String name, Operation op);

	public void registerAttribute(String name, Object obj);

	public List<Object> getAttributeValues(List<String> variables);
	
	public Object getAttributeValue(String variable);
	
	public void setAttributeValues(List<String> variables,List<Object> values);
	
	public void setAttributeValue(String variable,Object value);
	
	public void executeOperation(String opName, List<?> arguments);

	/***** Specific for MaestroEndpoint *****/
	public Object getAttributeValue(String attrName, String twinName);
	
	public Object getAttributeValue(String attrName, int entry);
	
	public Object getAttributeValue(String attrName, int entry, String twinName);
	/***** End Specific for MaestroEndpoint *****/

	public void setAttributeValue(String attrName, Object val, String twinName);

	public void setClock(int value);

	public int getClock();
	
}
