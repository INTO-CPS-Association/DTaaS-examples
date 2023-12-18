package dtmanager;

import java.sql.Timestamp;
import java.util.List;

import org.eclipse.basyx.submodel.metamodel.map.submodelelement.dataelement.property.Property;
import org.eclipse.basyx.submodel.metamodel.map.submodelelement.operation.Operation;
import org.eclipse.milo.opcua.stack.core.types.builtin.DataValue;

public interface DigitalTwinInterface {
	Endpoint endpoint = null;
	@Deprecated
	int eventCounter = 0;
	List<Property> attributes = null;
	List<Operation> operations = null;
	
	//public DigitalTwin();
	
	public void registerOperations(List<Operation> operations);
	
	public void registerAttributes(List<Property> attributes);
	
	public Object getAttributeValue(String attrName);
	
	public DigitalTwin getEmptyClone();
	
	@Deprecated
	public Object getAttributeValueAt(String attrName, Timestamp at);
	
	@Deprecated
	public List<Object> getAttributeValueAt(List<String> attrNames, Timestamp at);	// not yet used in the SDs, but should be of course also for the other get and set methods
	
	@Deprecated
	public DataValue getAttributeValueDelta(String attrName, int numberOfEvents); // This change is to introduce discrete-event future
	// It requires a count of events instead of absolute event count to avoid sync problems
	
	public void setAttributeValue(String attrName, Object val);
	
	@Deprecated
	public void setAttributeValueAt(String attrName, Object val, Timestamp at);
	
	// specific to discrete-time events
	public Object executeOperation(String opName, List<?> arguments);
	
	@Deprecated
	public Object executeOperationAt(String opName, List<?> arguments, Timestamp at);
	
	@Deprecated
	public Object executeOperationDelta(String opName, List<?> arguments, int numberOfEvents);
	
	@Deprecated
	void increaseEventCounter();
	
	public Clock getTime();
	
	public void setTime(Clock clock);

}
