package dtmanager;
import java.io.File;

import com.typesafe.config.*;

public class ComponentConfiguration {
	public Config conf;
	
	public ComponentConfiguration(String filename) {
		File file = new File(filename);   
		conf = ConfigFactory.parseFile(file);
	}
}
