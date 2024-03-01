package examples;

import java.util.ArrayList;
import java.util.List;
import java.util.Timer;
import java.util.TimerTask;

import config.ComponentConfiguration;
import config.TwinConfiguration;
import management.TwinManager;
import model.TwinSchema;
import services.DeviationChecker;

public class FlexCell {
	static TwinManager twinManager;
	static String modelFolderPrefix = "models/";
	static String dtFolderPrefix = "config/";
	static String dataFolderPrefix = "data/";

	public static void main(String[] args) {
		TwinSchema kukaSchema = TwinSchema.initializeFromAASX(modelFolderPrefix+"kuka.aasx","Kuka_LBR_iiwa7_AAS");
		TwinSchema ur5eSchema = TwinSchema.initializeFromAASX(modelFolderPrefix+"ur5e.aasx","UR5e_AAS");
		
		TwinConfiguration kukaModelConfig = new TwinConfiguration(dtFolderPrefix+"kuka_experimental.conf");
		TwinConfiguration ur5eModelConfig = new TwinConfiguration(dtFolderPrefix+"ur5e_experimental.conf");
		TwinConfiguration kukaActualConfig = new TwinConfiguration(dtFolderPrefix+"kuka_actual.conf");
		TwinConfiguration ur5eActualConfig = new TwinConfiguration(dtFolderPrefix+"ur5e_actual.conf");
		ComponentConfiguration flexcellSystemConfig = new ComponentConfiguration(dtFolderPrefix+"multimodel.json");
		String coe = dtFolderPrefix + "coe.json";
		String outputPath = dataFolderPrefix + "output/";
		
		
		twinManager = new TwinManager("FlexcellManager");
		twinManager.addSchema("Kuka_LBR_iiwa7", kukaSchema);
		twinManager.addSchema("UR5e", ur5eSchema);
		twinManager.createTwin("kuka_experimental",kukaModelConfig,"Kuka_LBR_iiwa7");
		twinManager.createTwin("ur5e_experimental",ur5eModelConfig,"UR5e");
		twinManager.createTwin("kuka_actual",kukaActualConfig,"Kuka_LBR_iiwa7");
		twinManager.createTwin("ur5e_actual",ur5eActualConfig,"UR5e");
		
		/***** TEST *****/
		/*System.out.println(twinManager.getAttributeValue("Current_Joint_Position_5", "ur5e_actual"));
		twinManager.setAttributeValue("Current_Joint_Position_5", 2.0, "ur5e_actual");
		System.out.println(twinManager.getAttributeValue("Current_Joint_Position_5", "ur5e_actual"));*/
		/***** END TEST *****/
		
		List<String> dtsFlexcellSystem = new ArrayList<String>();
		dtsFlexcellSystem.add("kuka_experimental");
		dtsFlexcellSystem.add("ur5e_experimental");
		twinManager.createTwinSystem("FlexcellSystem",dtsFlexcellSystem,flexcellSystemConfig,coe,outputPath);
		
		// These should be set from the real robots
		/*
		twinManager.setSystemAttributeValue("prev_q0_param", twinManager.getAttributeValue("Current_Joint_Position_0","ur5e_actual"), "FlexcellSystem","ur5e_experimental");
		twinManager.setSystemAttributeValue("prev_q1_param", twinManager.getAttributeValue("Current_Joint_Position_1","ur5e_actual"), "FlexcellSystem","ur5e_experimental");
		twinManager.setSystemAttributeValue("prev_q2_param", twinManager.getAttributeValue("Current_Joint_Position_2","ur5e_actual"), "FlexcellSystem","ur5e_experimental");
		twinManager.setSystemAttributeValue("prev_q3_param", twinManager.getAttributeValue("Current_Joint_Position_3","ur5e_actual"), "FlexcellSystem","ur5e_experimental");
		twinManager.setSystemAttributeValue("prev_q4_param", twinManager.getAttributeValue("Current_Joint_Position_4","ur5e_actual"), "FlexcellSystem","ur5e_experimental");
		twinManager.setSystemAttributeValue("prev_q5_param", twinManager.getAttributeValue("Current_Joint_Position_5","ur5e_actual"), "FlexcellSystem","ur5e_experimental");
		
		twinManager.setSystemAttributeValue("prev_q0_param", twinManager.getAttributeValue("Current_Joint_Position_0","kuka_actual"), "FlexcellSystem","kuka_experimental");
		twinManager.setSystemAttributeValue("prev_q1_param", twinManager.getAttributeValue("Current_Joint_Position_1","kuka_actual"), "FlexcellSystem","kuka_experimental");
		twinManager.setSystemAttributeValue("prev_q2_param", twinManager.getAttributeValue("Current_Joint_Position_2","kuka_actual"), "FlexcellSystem","kuka_experimental");
		twinManager.setSystemAttributeValue("prev_q3_param", twinManager.getAttributeValue("Current_Joint_Position_3","kuka_actual"), "FlexcellSystem","kuka_experimental");
		twinManager.setSystemAttributeValue("prev_q4_param", twinManager.getAttributeValue("Current_Joint_Position_4","kuka_actual"), "FlexcellSystem","kuka_experimental");
		twinManager.setSystemAttributeValue("prev_q5_param", twinManager.getAttributeValue("Current_Joint_Position_5","kuka_actual"), "FlexcellSystem","kuka_experimental");
		twinManager.setSystemAttributeValue("prev_q6_param", twinManager.getAttributeValue("Current_Joint_Position_6","kuka_actual"), "FlexcellSystem","kuka_experimental");
		*/		
		
		twinManager.setSystemAttributeValue("prev_q0_param", -2.666677, "FlexcellSystem","ur5e_experimental");
		twinManager.setSystemAttributeValue("prev_q1_param", -2.06638, "FlexcellSystem","ur5e_experimental");
		twinManager.setSystemAttributeValue("prev_q2_param", 2.315173, "FlexcellSystem","ur5e_experimental");
		twinManager.setSystemAttributeValue("prev_q3_param", -2.248468, "FlexcellSystem","ur5e_experimental");
		twinManager.setSystemAttributeValue("prev_q4_param", -0.890721, "FlexcellSystem","ur5e_experimental");
		twinManager.setSystemAttributeValue("prev_q5_param", -0.942086, "FlexcellSystem","ur5e_experimental");
		
		twinManager.setSystemAttributeValue("prev_q0_param", 0.285609, "FlexcellSystem","kuka_experimental");
		twinManager.setSystemAttributeValue("prev_q1_param", 0.287188, "FlexcellSystem","kuka_experimental");
		twinManager.setSystemAttributeValue("prev_q2_param", 0.220264, "FlexcellSystem","kuka_experimental");
		twinManager.setSystemAttributeValue("prev_q3_param", -1.851805, "FlexcellSystem","kuka_experimental");
		twinManager.setSystemAttributeValue("prev_q4_param", -0.073072, "FlexcellSystem","kuka_experimental");
		twinManager.setSystemAttributeValue("prev_q5_param", 1.010198, "FlexcellSystem","kuka_experimental");
		twinManager.setSystemAttributeValue("prev_q6_param", 0.536052, "FlexcellSystem","kuka_experimental");
		
		/*twinManager.setSystemAttributeValue("actual_q0", -2.666677, "FlexcellSystem","ur5e_experimental");
		twinManager.setSystemAttributeValue("actual_q1", -2.06638, "FlexcellSystem","ur5e_experimental");
		twinManager.setSystemAttributeValue("actual_q2", 2.315173, "FlexcellSystem","ur5e_experimental");
		twinManager.setSystemAttributeValue("actual_q3", -2.248468, "FlexcellSystem","ur5e_experimental");
		twinManager.setSystemAttributeValue("actual_q4", -0.890721, "FlexcellSystem","ur5e_experimental");
		twinManager.setSystemAttributeValue("actual_q5", -0.942086, "FlexcellSystem","ur5e_experimental");
		
		twinManager.setSystemAttributeValue("actual_q0", 0.285609, "FlexcellSystem","kuka_experimental");
		twinManager.setSystemAttributeValue("actual_q1", 0.287188, "FlexcellSystem","kuka_experimental");
		twinManager.setSystemAttributeValue("actual_q2", 0.220264, "FlexcellSystem","kuka_experimental");
		twinManager.setSystemAttributeValue("actual_q3", -1.851805, "FlexcellSystem","kuka_experimental");
		twinManager.setSystemAttributeValue("actual_q4", -0.073072, "FlexcellSystem","kuka_experimental");
		twinManager.setSystemAttributeValue("actual_q5", 1.010198, "FlexcellSystem","kuka_experimental");
		twinManager.setSystemAttributeValue("actual_q6", 0.536052, "FlexcellSystem","kuka_experimental");*/
		//System.exit(0);
		
		List<Object> arguments = new ArrayList<Object>();
		arguments.add(0.0);
		twinManager.executeOperationOnSystem("initializeSimulation", arguments, "FlexcellSystem");
		
		twinManager.executeOperationOnSystem("simulate", null, "FlexcellSystem");		
		
		
		Object kukaActualQ5 = twinManager.getSystemAttributeValueAt("actual_q5", "FlexcellSystem","kuka_experimental",10);
		Object kukaActualX = twinManager.getSystemAttributeValueAt("actual_X", "FlexcellSystem","kuka_experimental",10);
		Object kukaActualY = twinManager.getSystemAttributeValueAt("actual_Y", "FlexcellSystem","kuka_experimental",10);
		Object kukaActualZ = twinManager.getSystemAttributeValueAt("actual_Z", "FlexcellSystem","kuka_experimental",10);
		Object ur5eActualX = twinManager.getSystemAttributeValueAt("actual_X", "FlexcellSystem","ur5e_experimental",10);
		Object ur5eActualY = twinManager.getSystemAttributeValueAt("actual_Y", "FlexcellSystem","ur5e_experimental",10);
		Object ur5eActualZ = twinManager.getSystemAttributeValueAt("actual_Z", "FlexcellSystem","ur5e_experimental",10);
		System.out.println("Kuka actual_q5 (experimental): " + kukaActualQ5.toString());
		System.out.println("Kuka flex-cell X position (experimental): " + kukaActualX.toString());
		System.out.println("Kuka flex-cell Y position (experimental): " + kukaActualY.toString());
		System.out.println("Kuka flex-cell X position (experimental): " + kukaActualZ.toString());
		System.out.println("UR5e flex-cell X position (experimental): " + ur5eActualX.toString());
		System.out.println("UR5e flex-cell Y position (experimental): " + ur5eActualY.toString());
		System.out.println("UR5e flex-cell Z position (experimental): " + ur5eActualZ.toString());
		
		
		
		Object value = twinManager.getAttributeValue("actual_q_5", "ur5e_actual");
		System.out.println("UR5e actual_q_5 (actual): " + value);
		Object ur5eExperimentalQ = twinManager.getSystemAttributeValueAt("actual_q5", "FlexcellSystem","ur5e_experimental",10);
		System.out.println("UR5e actual_q_5 (experimental): " + ur5eExperimentalQ);
		value = twinManager.getAttributeValue("actual_q_0", "ur5e_actual");
		ur5eExperimentalQ = twinManager.getSystemAttributeValueAt("actual_q0", "FlexcellSystem","ur5e_experimental",10);
		System.out.println("UR5e actual_q_0 (actual): " + value);
		System.out.println("UR5e actual_q_0 (experimental): " + ur5eExperimentalQ);

		Object valueK = twinManager.getAttributeValue("actual_q_5", "kuka_actual");
		System.out.println("kuka actual_q_5 (actual): " + valueK);
		Object kukaExperimentalQ = twinManager.getSystemAttributeValueAt("actual_q5", "FlexcellSystem","kuka_experimental",10);
		System.out.println("kuka actual_q_5 (experimental): " + kukaExperimentalQ);
		valueK = twinManager.getAttributeValue("actual_q_0", "kuka_actual");
		kukaExperimentalQ = twinManager.getSystemAttributeValueAt("actual_q0", "FlexcellSystem","kuka_experimental",10);
		System.out.println("kuka actual_q_0 (actual): " + valueK);
		System.out.println("kuka actual_q_0 (experimental): " + kukaExperimentalQ);
		
		
		Thread eventThread = new Thread(() -> {
			new Timer().scheduleAtFixedRate(new TimerTask() {
				public void run() {
					try {
						//twinManager.executeOperationOnSystem("simulate", null, "FlexcellSystem");
						DeviationChecker.deviationChecking(twinManager, "actual_q_5", "actual_q5", "ur5e_actual", "ur5e_experimental", 0.1); // Returns the result of the deviation checking
						
						DeviationChecker.deviationChecking(twinManager, "actual_q_5", "actual_q5", "kuka_actual", "kuka_experimental", 0.1); // Returns the result of the deviation checking
						
						twinManager.getClock().increaseTime(1); // Updating clock by 1 iteration
					} catch (Exception e) {
						e.printStackTrace();
					}
				}
			}, 1000, 1000);
		});
		//eventThread.setDaemon(true);
		//eventThread.start();
	}
}
