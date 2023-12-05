package dtmanager;

import java.io.File;

import com.typesafe.config.*;

public class TwinConfiguration {
	public Config conf;
	
	public TwinConfiguration(String filename) {
		File file = new File(filename);   
		conf = ConfigFactory.parseFile(file);
	}
	
}
