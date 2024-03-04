package model;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.Map;
import java.util.Set;

import javax.xml.parsers.ParserConfigurationException;

import org.eclipse.basyx.aas.factory.aasx.AASXToMetamodelConverter;
import org.eclipse.basyx.aas.metamodel.api.IAssetAdministrationShell;
import org.apache.poi.openxml4j.exceptions.InvalidFormatException;
import org.eclipse.basyx.aas.bundle.AASBundle;
import org.eclipse.basyx.submodel.metamodel.api.ISubmodel;
import org.eclipse.basyx.submodel.metamodel.api.submodelelement.ISubmodelElement;
import org.xml.sax.SAXException;

import model.composition.Attribute;
import model.composition.Operation;

public class TwinSchema {
	// TO DO: INITIALIZATION FROM JSON and XML
	private String className;
	private List<Attribute> attributes;
	private List<Operation> operations;
	
	public TwinSchema() {
	}
	
	public TwinSchema(String className) {
		this.className = className;
	}	
	
	public List<Attribute> getAttributes(){
		return this.attributes;
	}
	
	public List<Operation> getOperations(){
		return this.operations;
	}
	
	public static TwinSchema initializeFromAASX(String filePath, String aasIdShort) {
		TwinSchema schema = new TwinSchema();
		schema.attributes = new ArrayList<Attribute>();
		schema.operations = new ArrayList<Operation>();
		
		
		AASXToMetamodelConverter packageManager = new AASXToMetamodelConverter(filePath);
		Set<AASBundle> bundles = null;
		try {
			bundles = packageManager.retrieveAASBundles();
		} catch (InvalidFormatException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (ParserConfigurationException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (SAXException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		/*AASBundle bundle = findBundle(bundles, aasIdShort);
		IAssetAdministrationShell objectAAS = bundle.getAAS();
		Map<String, ISubmodel> submodels = objectAAS.getSubmodels();
		ISubmodel operationalDataSubmodel = submodels.get("OperationalData");*/
		ISubmodel operationalDataSubmodel = findSubmodel(bundles,"OperationalData");
		
		ISubmodelElement seOperations = operationalDataSubmodel.getSubmodelElement("Operations");
		Collection<ISubmodelElement> seOperationsCollection = (Collection<ISubmodelElement>) seOperations.getValue();
		for (ISubmodelElement op : seOperationsCollection) {
			Operation twinOperation = new Operation();
			twinOperation.setName(op.getIdShort());
			schema.operations.add(twinOperation);
		}
		
		ISubmodelElement seVariables = operationalDataSubmodel.getSubmodelElement("Variables");
		Collection<ISubmodelElement> seVariablesCollection = (Collection<ISubmodelElement>) seVariables.getValue();
		for (ISubmodelElement attr : seVariablesCollection) {
			Attribute twinAttribute = new Attribute();
			twinAttribute.setName(attr.getIdShort());
			schema.attributes.add(twinAttribute);
		}
		return schema;
	}
	

	private static ISubmodel findSubmodel(Set<AASBundle> bundles, String idShort) {
		for (AASBundle aasBundle : bundles) {
			for (ISubmodel sm : aasBundle.getSubmodels()) {
				if(sm.getIdShort().equals(idShort)) {
					return sm;
				}
			}
		}
		return null;
	}
	
	private static AASBundle findBundle(Set<AASBundle> bundles, String aasIdShort) {
		for (AASBundle aasBundle : bundles) {
			if (aasBundle.getAAS().getIdShort().equals(aasIdShort)) {
				return aasBundle;
			}
		}
		return null;
	}
	
	private static ISubmodel getBundleSubmodel(Set<ISubmodel> submodels, String submodelIdShort) {
		for (ISubmodel submodel : submodels) {
			if (submodel.getIdShort().equals(submodelIdShort))
				return submodel;
		}
		return null;
	}

}
