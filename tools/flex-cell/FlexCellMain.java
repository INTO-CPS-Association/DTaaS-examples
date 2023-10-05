import java.util.ArrayList;
import java.util.List;
import java.util.Timer;
import java.util.TimerTask;

import dtmanager.ComponentConfiguration;
import dtmanager.DTManager;
import dtmanager.TwinConfiguration;
import dtmanager.TwinSchema;

public class FlexCellMain {
	static DTManager dtManager;
	static String modelFolderPrefix = "/workspace/examples/models/flex-cell/";
	static String dtFolderPrefix = "/workspace/examples/digital twins/flex-cell/";
	static String dataFolderPrefix = "/workspace/examples/data/flex-cell/";

	public static void main(String[] args) {
		TwinSchema kukaSchema = new TwinSchema(modelFolderPrefix+"kuka.aasx","Kuka_LBR_iiwa7_AAS");
		TwinSchema ur5eSchema = new TwinSchema(modelFolderPrefix+"ur5e.aasx","UR5e_AAS");
		
		TwinConfiguration kukaModelConfig = new TwinConfiguration(dtFolderPrefix+"kuka_experimental.conf");
		TwinConfiguration ur5eModelConfig = new TwinConfiguration(dtFolderPrefix+"ur5e_experimental.conf");
		TwinConfiguration kukaActualConfig = new TwinConfiguration(dtFolderPrefix+"kuka_actual.conf");
		TwinConfiguration ur5eActualConfig = new TwinConfiguration(dtFolderPrefix+"ur5e_actual.conf");
		ComponentConfiguration flexcellSystemConfig = new ComponentConfiguration(dtFolderPrefix+"multimodel.json");
		String coe = dtFolderPrefix + "coe.json";
		String outputPath = dataFolderPrefix + "output/";
		
		List<TwinSchema> schemas = new ArrayList<TwinSchema>();
		schemas.add(ur5eSchema);
		schemas.add(kukaSchema);
		dtManager = new DTManager("FlexcellManager",schemas);
		dtManager.createDigitalTwin("kuka_experimental",kukaModelConfig,kukaSchema);
		dtManager.createDigitalTwin("ur5e_experimental",ur5eModelConfig,ur5eSchema);
		dtManager.createDigitalTwin("kuka_actual",kukaActualConfig,kukaSchema);
		dtManager.createDigitalTwin("ur5e_actual",ur5eActualConfig,ur5eSchema);
		
		/***** TEST *****/
		/*System.out.println(dtManager.getAttributeValue("Current_Joint_Position_5", "ur5e_actual"));
		dtManager.setAttributeValue("Current_Joint_Position_5", 2.0, "ur5e_actual");
		System.out.println(dtManager.getAttributeValue("Current_Joint_Position_5", "ur5e_actual"));*/
		/***** END TEST *****/
		
		List<String> dtsFlexcellSystem = new ArrayList<String>();
		dtsFlexcellSystem.add("kuka_experimental");
		dtsFlexcellSystem.add("ur5e_experimental");
		dtManager.createDigitalTwinSystem("FlexcellSystem",dtsFlexcellSystem,flexcellSystemConfig,coe,outputPath);
		
		List<Object> arguments = new ArrayList<Object>();
		arguments.add(0.0);
		dtManager.executeOperationOnSystem("initializeSimulation", arguments, "FlexcellSystem");
		
		dtManager.executeOperationOnSystem("simulate", null, "FlexcellSystem");
		/*List<String> attributeNames = new ArrayList<String>();
		List<Object> attributeValues = new ArrayList<Object>();
		attributeNames.add("target_X_ur5e");
		attributeNames.add("target_Y_ur5e");
		attributeNames.add("target_Z_ur5e");
		attributeNames.add("target_X_kuka");
		attributeNames.add("target_Y_kuka");
		attributeNames.add("target_Z_kuka");
		
		attributeValues.add(0);
		attributeValues.add(22);
		attributeValues.add(4);
		attributeValues.add(4);
		attributeValues.add(5);
		attributeValues.add(3);
		
		dtManager.setSystemAttributeValues(attributeNames, attributeValues, "FlexcellSystem");*/
		
		/*dtManager.setSystemAttributeValue("target_X", 0, "FlexcellSystem","ur5e_experimental");
		dtManager.setSystemAttributeValue("target_Y", 22, "FlexcellSystem","ur5e_experimental");
		dtManager.setSystemAttributeValue("target_Z", 4, "FlexcellSystem","ur5e_experimental");
		
		dtManager.setSystemAttributeValue("target_X", 4, "FlexcellSystem","kuka_experimental");
		dtManager.setSystemAttributeValue("target_Y", 5, "FlexcellSystem","kuka_experimental");
		dtManager.setSystemAttributeValue("target_Z", 3, "FlexcellSystem","kuka_experimental");*/
		
		
		Object kukaActualQ5 = dtManager.getSystemAttributeValueAt("actual_q5", "FlexcellSystem","kuka_experimental",10);
		Object kukaActualX = dtManager.getSystemAttributeValueAt("actual_X", "FlexcellSystem","kuka_experimental",10);
		Object kukaActualY = dtManager.getSystemAttributeValueAt("actual_Y", "FlexcellSystem","kuka_experimental",10);
		Object kukaActualZ = dtManager.getSystemAttributeValueAt("actual_Z", "FlexcellSystem","kuka_experimental",10);
		Object ur5eActualX = dtManager.getSystemAttributeValueAt("actual_X", "FlexcellSystem","ur5e_experimental",10);
		Object ur5eActualY = dtManager.getSystemAttributeValueAt("actual_Y", "FlexcellSystem","ur5e_experimental",10);
		Object ur5eActualZ = dtManager.getSystemAttributeValueAt("actual_Z", "FlexcellSystem","ur5e_experimental",10);
		System.out.println("Kuka actual_q5 (experimental): " + kukaActualQ5.toString());
		System.out.println("Kuka flex-cell X position (experimental): " + kukaActualX.toString());
		System.out.println("Kuka flex-cell Y position (experimental): " + kukaActualY.toString());
		System.out.println("Kuka flex-cell X position (experimental): " + kukaActualZ.toString());
		System.out.println("UR5e flex-cell X position (experimental): " + ur5eActualX.toString());
		System.out.println("UR5e flex-cell Y position (experimental): " + ur5eActualY.toString());
		System.out.println("UR5e flex-cell Z position (experimental): " + ur5eActualZ.toString());
		
		/*
		kukaActualQ5 = dtManager.getSystemAttributeValueAt("actual_q5", "FlexcellSystem","kuka_experimental",10);
		kukaActualX = dtManager.getSystemAttributeValueAt("actual_X", "FlexcellSystem","kuka_experimental",10);
		kukaActualY = dtManager.getSystemAttributeValueAt("actual_Y", "FlexcellSystem","kuka_experimental",10);
		kukaActualZ = dtManager.getSystemAttributeValueAt("actual_Z", "FlexcellSystem","kuka_experimental",10);
		ur5eActualX = dtManager.getSystemAttributeValueAt("actual_X", "FlexcellSystem","ur5e_experimental",10);
		ur5eActualY = dtManager.getSystemAttributeValueAt("actual_Y", "FlexcellSystem","ur5e_experimental",10);
		ur5eActualZ = dtManager.getSystemAttributeValueAt("actual_Z", "FlexcellSystem","ur5e_experimental",10);
		System.out.println(kukaActualQ5.toString());
		System.out.println(kukaActualX.toString());
		System.out.println(kukaActualY.toString());
		System.out.println(kukaActualZ.toString());
		System.out.println(ur5eActualX.toString());
		System.out.println(ur5eActualY.toString());
		System.out.println(ur5eActualZ.toString());*/
		
		
		Object value = dtManager.getAttributeValue("actual_q_5", "ur5e_actual");
		System.out.println("UR5e actual_q_5 (actual): " + value);
		Object ur5eExperimentalQ = dtManager.getSystemAttributeValueAt("actual_q5", "FlexcellSystem","ur5e_experimental",10);
		System.out.println("UR5e actual_q_5 (experimental): " + ur5eExperimentalQ);
		value = dtManager.getAttributeValue("actual_q_0", "ur5e_actual");
		ur5eExperimentalQ = dtManager.getSystemAttributeValueAt("actual_q0", "FlexcellSystem","ur5e_experimental",10);
		System.out.println("UR5e actual_q_0 (actual): " + value);
		System.out.println("UR5e actual_q_0 (experimental): " + ur5eExperimentalQ);

		Object valueK = dtManager.getAttributeValue("actual_q_5", "kuka_actual");
		System.out.println("kuka actual_q_5 (actual): " + valueK);
		Object kukaExperimentalQ = dtManager.getSystemAttributeValueAt("actual_q5", "FlexcellSystem","kuka_experimental",10);
		System.out.println("kuka actual_q_5 (experimental): " + kukaExperimentalQ);
		valueK = dtManager.getAttributeValue("actual_q_0", "kuka_actual");
		kukaExperimentalQ = dtManager.getSystemAttributeValueAt("actual_q0", "FlexcellSystem","kuka_experimental",10);
		System.out.println("kuka actual_q_0 (actual): " + valueK);
		System.out.println("kuka actual_q_0 (experimental): " + kukaExperimentalQ);
		
		/*

		Thread eventThread = new Thread(() -> {
			new Timer().scheduleAtFixedRate(new TimerTask() {
				public void run() {
					try {
						Object value = dtManager.getAttributeValue("actual_q_5", "ur5e_actual");
						System.out.println("UR5e actual_q_5 (actual): " + value);
						Object ur5eExperimentalQ = dtManager.getSystemAttributeValueAt("actual_q5", "FlexcellSystem","ur5e_experimental",10);
						System.out.println("UR5e actual_q_5 (experimental): " + ur5eExperimentalQ);
						value = dtManager.getAttributeValue("actual_q_0", "ur5e_actual");
						ur5eExperimentalQ = dtManager.getSystemAttributeValueAt("actual_q0", "FlexcellSystem","ur5e_experimental",10);
						System.out.println("UR5e actual_q_0 (actual): " + value);
						System.out.println("UR5e actual_q_0 (experimental): " + ur5eExperimentalQ);
					} catch (Exception e) {
						e.printStackTrace();
					}
				}
			}, 1000, 1000);
		});
		eventThread.setDaemon(true);
		eventThread.start();*/
	}

}
