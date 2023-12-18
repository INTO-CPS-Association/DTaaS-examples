import java.util.ArrayList;
import java.util.List;
import java.util.Timer;
import java.util.TimerTask;

//import org.apache.log4j.LogManager;

import dtmanager.ComponentConfiguration;
import dtmanager.DTManager;
import dtmanager.DigitalTwin;
import dtmanager.TwinConfiguration;
import dtmanager.TwinSchema;

public class TankMain {
	static DTManager dtManager;
	static String modelFolderPrefix = "/workspace/examples/models/three-tank/";
	static String dtFolderPrefix = "/workspace/examples/digital_twins/three-tank/";
	static String dataFolderPrefix = "/workspace/examples/data/three-tank/";

	public static void main(String[] args) {
		// TODO Auto-generated method stub
		//LogManager.shutdown();

		TwinSchema schema = new TwinSchema(modelFolderPrefix+"TankSystem.aasx","TankSystem_AAS");
		TwinConfiguration tank1Config = new TwinConfiguration(dtFolderPrefix+"tank1.conf");
		TwinConfiguration tank2Config = new TwinConfiguration(dtFolderPrefix+"tank2.conf");
		TwinConfiguration tank3Config = new TwinConfiguration(dtFolderPrefix+"tank3.conf");
		ComponentConfiguration tankSystemConfig = new ComponentConfiguration(dtFolderPrefix+"multimodel.json");
		String coe = dtFolderPrefix + "coe.json";
		String outputPath = dataFolderPrefix + "output/";

		dtManager = new DTManager("TankManager",schema);
		dtManager.createDigitalTwin("tank1",tank1Config);
		dtManager.createDigitalTwin("tank2",tank2Config);
		dtManager.createDigitalTwin("tank3",tank3Config);
		
		List<String> dtsTankSystem = new ArrayList<String>();
		dtsTankSystem.add("tank1");
		dtsTankSystem.add("tank2");
		dtsTankSystem.add("tank3");		
		dtManager.createDigitalTwinSystem("TankSystem",dtsTankSystem,tankSystemConfig,coe,outputPath);
		
		List<Object> arguments = new ArrayList<Object>();
		arguments.add(0.0);
		dtManager.executeOperationOnSystem("initializeSimulation", arguments, "TankSystem");
		
		dtManager.setAttributeValue("Level", 2.0, "tank1");
		dtManager.setAttributeValue("DerLevel", 0.1, "tank1");
		dtManager.setAttributeValue("Leak", 0.1, "tank1");
		dtManager.setAttributeValue("InPort", 1, "tank1");
		dtManager.setAttributeValue("OutPort", 1, "tank1");
		//dtManager.setAttributeValue("InPort", 1, "tank2");
		//dtManager.setAttributeValue("InPort", 1, "tank3");
		dtManager.executeOperationOnSystem("simulate", null, "TankSystem");
		
		Object levelTank1 = dtManager.getAttributeValue("Level","tank1");
		Object levelTank2 = dtManager.getAttributeValue("Level","tank2");
		Object levelTank3 = dtManager.getAttributeValue("Level","tank3");
		System.out.println(levelTank1);
		System.out.println(levelTank2);
		System.out.println(levelTank3);
		
		Object tank3Level = dtManager.getSystemAttributeValue("{tank}.tank3.level", "TankSystem");
		System.out.println(tank3Level.toString());
		tank3Level = dtManager.getSystemAttributeValue("Level", "TankSystem","tank3");
		System.out.println(tank3Level.toString());
		dtManager.setSystemAttributeValue("{tank}.tank1.level", 3.0, "TankSystem");
		dtManager.setSystemAttributeValue("{tank}.tank2.level", 10.0, "TankSystem");
		//dtManager.setSystemAttributeValue("{tank}.tank3.level", 45.0, "TankSystem");
		dtManager.setSystemAttributeValue("Level", 35.0, "TankSystem","tank3");
		dtManager.setSystemAttributeValue("Level", 2.0, "TankSystem","tank1");
		
		//dtManager.executeOperationOnSystem("doStep", null, "TankSystem");
		tank3Level = dtManager.getSystemAttributeValue("{tank}.tank3.level", "TankSystem");
		System.out.println(tank3Level.toString());
		tank3Level = dtManager.getSystemAttributeValue("Level", "TankSystem","tank3"); 
		System.out.println(tank3Level.toString());
		
		Object tank2Level = dtManager.getSystemAttributeValue("Level", "TankSystem","tank2");
		System.out.println(tank2Level.toString());

		
		Thread eventThread = new Thread(() -> {
			new Timer().scheduleAtFixedRate(new TimerTask() {
				@Override
				public void run() {
					try {
						dtManager.executeOperationOnSystem("simulate", null, "TankSystem");
						Object levelTank1 = dtManager.getAttributeValue("Level","tank1");
						Object levelTank2 = dtManager.getAttributeValue("Level","tank2");
						Object levelTank3 = dtManager.getAttributeValue("Level","tank3");
						System.out.println(levelTank1);
						System.out.println(levelTank2);
						System.out.println(levelTank3);
					} catch (Exception e) {
						e.printStackTrace();
					}	
				}
			}, 1000, 1000);
				
	});
		
	/*public void deviationChecking(String variable, DigitalTwin twin1, DigitalTwin twin2, float threshold) {
		if (DTManager.getAttributeValue(variable,twin1) > threshold* DTManager.getAttributeValue(variable,twin2)) {
			System.out.println("Level of tank 1 (physical) higher than expected");
		}
	}*/
	//eventThread.start();
	}

}
