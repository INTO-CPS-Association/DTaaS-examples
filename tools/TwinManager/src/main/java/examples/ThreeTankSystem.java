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

public class ThreeTankSystem {
	static TwinManager twinManager;
	static String modelFolderPrefix = "/workspace/models/three-tank/";
	static String dtFolderPrefix = "/workspace/digital_twins/three-tank/";
	static String dataFolderPrefix = "/workspace/data/three-tank/";

	// public static void main(String[] args) {
	// 	TwinSchema schema = new TwinSchema("tank");
	// 	TwinConfiguration tank1Config = new TwinConfiguration(dtFolderPrefix+"tank1.conf");
	// 	TwinConfiguration tank2Config = new TwinConfiguration(dtFolderPrefix+"tank2.conf");
	// 	TwinConfiguration tank3Config = new TwinConfiguration(dtFolderPrefix+"tank3.conf");
		
	// 	ComponentConfiguration tankSystemConfig = new ComponentConfiguration(dtFolderPrefix+"multimodel.json");
	// 	String coe = dtFolderPrefix + "coe.json";
	// 	String outputPath = dataFolderPrefix + "output/";

	// 	twinManager = new TwinManager("TankManager");
	// 	twinManager.addSchema("tank", schema);
	// 	twinManager.createTwin("tank1",tank1Config);
	// 	twinManager.createTwin("tank2",tank2Config);
	// 	twinManager.createTwin("tank3",tank3Config);
		
	// 	List<String> twinsTankSystem = new ArrayList<String>();
	// 	twinsTankSystem.add("tank1");
	// 	twinsTankSystem.add("tank2");
	// 	twinsTankSystem.add("tank3");		
	// 	twinManager.createTwinSystem("ThreeTankSystem",twinsTankSystem,tankSystemConfig,coe,outputPath);
		
	// 	List<Object> arguments = new ArrayList<Object>();
	// 	arguments.add(0.0);
	// 	twinManager.executeOperationOnSystem("initializeSimulation", arguments, "TankSystem");
		
	// 	twinManager.setAttributeValue("Level", 2.0, "tank1");
	// 	twinManager.setAttributeValue("DerLevel", 0.1, "tank1");
	// 	twinManager.setAttributeValue("Leak", 0.1, "tank1");
	// 	twinManager.setAttributeValue("InPort", 1, "tank1");
	// 	twinManager.setAttributeValue("OutPort", 1, "tank1");
	// 	//twinManager.setAttributeValue("InPort", 1, "tank2");
	// 	//twinManager.setAttributeValue("InPort", 1, "tank3");
	// 	twinManager.executeOperationOnSystem("simulate", null, "ThreeTankSystem");
		
	// 	Object levelTank1 = twinManager.getAttributeValue("Level","tank1");
	// 	Object levelTank2 = twinManager.getAttributeValue("Level","tank2");
	// 	Object levelTank3 = twinManager.getAttributeValue("Level","tank3");

		
	// 	Object tank3Level = twinManager.getSystemAttributeValue("{tank}.tank3.level", "TankSystem");
	// 	tank3Level = twinManager.getSystemAttributeValue("Level", "TankSystem","tank3");
	// 	twinManager.setSystemAttributeValue("{tank}.tank1.level", 3.0, "TankSystem");
	// 	twinManager.setSystemAttributeValue("{tank}.tank2.level", 10.0, "TankSystem");
	// 	twinManager.setSystemAttributeValue("Level", 35.0, "TankSystem","tank3");
	// 	twinManager.setSystemAttributeValue("Level", 2.0, "TankSystem","tank1");
		
	// 	//twinManager.executeOperationOnSystem("doStep", null, "TankSystem");
	// 	tank3Level = twinManager.getSystemAttributeValue("Level", "TankSystem","tank3"); 
	// 	System.out.println(tank3Level.toString());


		
	// 	Thread eventThread = new Thread(() -> {
	// 		new Timer().scheduleAtFixedRate(new TimerTask() {
	// 			@Override
	// 			public void run() {
	// 				try {
						
	// 					//twinManager.executeOperationOnSystem("simulate", null, "TankSystem");
	// 					DeviationChecker.deviationChecking(twinManager, "Level", "tank2", "tank3", 0.15); // Returns the result of the deviation checking
						
	// 					twinManager.getClock().increaseTime(1); // Updating clock by 1 iteration
						
	// 				} catch (Exception e) {
	// 					e.printStackTrace();
	// 				}	
	// 			}
	// 		}, 1000, 1000);
				
	// 	});
	// 	eventThread.setDaemon(true);
	// 	eventThread.start();

	// }

}
