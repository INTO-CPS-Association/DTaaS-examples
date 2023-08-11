package dtmanager;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.function.Function;

import javax.xml.parsers.ParserConfigurationException;

import org.apache.poi.openxml4j.exceptions.InvalidFormatException;
import org.eclipse.basyx.aas.manager.ConnectedAssetAdministrationShellManager;
import org.eclipse.basyx.aas.metamodel.api.IAssetAdministrationShell;
import org.eclipse.basyx.aas.metamodel.connected.ConnectedAssetAdministrationShell;
import org.eclipse.basyx.aas.metamodel.map.AssetAdministrationShell;
import org.eclipse.basyx.aas.metamodel.map.descriptor.ModelUrn;
import org.eclipse.basyx.aas.metamodel.map.descriptor.SubmodelDescriptor;
import org.eclipse.basyx.aas.metamodel.map.parts.Asset;
import org.eclipse.basyx.aas.registration.proxy.AASRegistryProxy;
import org.eclipse.basyx.components.aas.aasx.AASXPackageManager;
import org.eclipse.basyx.submodel.metamodel.api.ISubmodel;
import org.eclipse.basyx.submodel.metamodel.api.qualifier.qualifiable.IConstraint;
import org.eclipse.basyx.submodel.metamodel.api.submodelelement.ISubmodelElement;
import org.eclipse.basyx.submodel.metamodel.api.submodelelement.dataelement.IProperty;
import org.eclipse.basyx.submodel.metamodel.api.submodelelement.operation.IOperation;
import org.eclipse.basyx.submodel.metamodel.connected.submodelelement.dataelement.ConnectedProperty;
import org.eclipse.basyx.submodel.metamodel.connected.submodelelement.operation.ConnectedOperation;
import org.eclipse.basyx.submodel.metamodel.map.Submodel;
import org.eclipse.basyx.submodel.metamodel.map.qualifier.qualifiable.Qualifier;
import org.eclipse.basyx.submodel.metamodel.map.submodelelement.dataelement.property.Property;
import org.eclipse.basyx.submodel.metamodel.map.submodelelement.operation.Operation;
import org.eclipse.basyx.support.bundle.AASBundle;
import org.eclipse.basyx.vab.manager.VABConnectionManager;
import org.eclipse.basyx.vab.modelprovider.api.IModelProvider;
import org.xml.sax.SAXException;

public class TwinSchema implements Cloneable {

	// From the File
	private List<Property> attributes;
	private List<Operation> operations;

	// From the File
	public Set<ISubmodel> submodels;
	public ISubmodel technicalDataSubmodel;
	public ISubmodel operationalDataSubmodel;
	public IAssetAdministrationShell objectAAS;

	
	
	public TwinSchema(String schemaFileName,String aasIdShort) {
		AASXPackageManager aasxManager = new AASXPackageManager(schemaFileName);
		Set<AASBundle> bundles;
		try {
			bundles = aasxManager.retrieveAASBundles();
		} catch (InvalidFormatException e) {
			bundles = null;
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			bundles = null;
			e.printStackTrace();
		} catch (ParserConfigurationException e) {
			// TODO Auto-generated catch block
			bundles = null;
			e.printStackTrace();
		} catch (SAXException e) {
			// TODO Auto-generated catch block
			bundles = null;
			e.printStackTrace();
		}
		
		AASBundle object = findBundle(bundles, aasIdShort);
		objectAAS = object.getAAS();

		/***** Configuration *****/
		this.submodels = object.getSubmodels();
		this.technicalDataSubmodel = getBundleSubmodel(submodels, "TechnicalData");
		this.operationalDataSubmodel = getBundleSubmodel(submodels, "OperationalData");
		this.operations = this.getOperations();
		this.attributes = this.getAttributes();
	}
	
	public static AASBundle findBundle(Set<AASBundle> bundles, String aasIdShort) {
		for (AASBundle aasBundle : bundles) {
			if (aasBundle.getAAS().getIdShort().equals(aasIdShort))
				return aasBundle;
		}
		return null;
	}

	public static ISubmodel getBundleSubmodel(Set<ISubmodel> submodels, String submodelIdShort) {
		for (ISubmodel submodel : submodels) {
			if (submodel.getIdShort().equals(submodelIdShort))
				return submodel;
		}
		return null;
	}
	
	public static ISubmodel getSubmodel(Set<ISubmodel> submodels, String submodelIdShort) {
		for (ISubmodel submodel : submodels) {
			if (submodel.getIdShort().equals(submodelIdShort))
				return submodel;
		}
		return null;
	}
	
	/****** From the File  *******/
	public Map<String, IOperation> getMapOperations(){
		ISubmodelElement seOperations = this.operationalDataSubmodel.getSubmodelElement("Operations");
		Collection<ISubmodelElement> seOperationsCollection = (Collection<ISubmodelElement>) seOperations.getValue();
		Map<String, IOperation> operationsMap = new HashMap<String, IOperation>();
		for (ISubmodelElement op : seOperationsCollection) {
			operationsMap.put(op.getIdShort(), (IOperation) op);
		}
		return operationsMap;
	}
	
	public List<Operation> getOperations(){
		ISubmodelElement seOperations = this.operationalDataSubmodel.getSubmodelElement("Operations");
		Collection<ISubmodelElement> seOperationsCollection = (Collection<ISubmodelElement>) seOperations.getValue();
		List<Operation> operationsList = new ArrayList<Operation>();
		for (ISubmodelElement op : seOperationsCollection) {
			operationsList.add((Operation) op);
		}
		return operationsList;
	}
	
	public Map<String, IProperty> getMapAttributes(){
		ISubmodelElement seVariables = this.operationalDataSubmodel.getSubmodelElement("Variables");
		Collection<ISubmodelElement> seVariablesCollection = (Collection<ISubmodelElement>) seVariables.getValue();
		Map<String, IProperty> variablesMap = new HashMap<String, IProperty>();
		for (ISubmodelElement op : seVariablesCollection) {
			variablesMap.put(op.getIdShort(), (IProperty) op);
		}
		return variablesMap;
	}
	
	public List<Property> getAttributes(){
		ISubmodelElement seVariables = this.operationalDataSubmodel.getSubmodelElement("Variables");
		Collection<ISubmodelElement> seVariablesCollection = (Collection<ISubmodelElement>) seVariables.getValue();
		List<Property> variablesList = new ArrayList<Property>();
		for (ISubmodelElement op : seVariablesCollection) {
			variablesList.add((Property) op);
		}
		return variablesList;
	}
	
	public Object clone() throws CloneNotSupportedException {
		TwinSchema clone = (TwinSchema) super.clone();
		return clone;
	}
}