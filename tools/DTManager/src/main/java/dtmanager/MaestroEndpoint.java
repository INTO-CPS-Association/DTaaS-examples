package dtmanager;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.TimeoutException;

import org.eclipse.basyx.submodel.metamodel.connected.submodelelement.dataelement.ConnectedProperty;
import org.eclipse.basyx.submodel.metamodel.connected.submodelelement.operation.ConnectedOperation;
import org.eclipse.basyx.submodel.metamodel.map.submodelelement.dataelement.property.Property;
import org.eclipse.basyx.submodel.metamodel.map.submodelelement.operation.Operation;
import org.json.JSONObject;

import com.fasterxml.jackson.databind.ObjectWriter;
import com.opencsv.CSVReader;
import com.opencsv.CSVReaderBuilder;
import com.opencsv.exceptions.CsvException;
import com.rabbitmq.client.Channel;
import com.rabbitmq.client.Connection;
import com.rabbitmq.client.ConnectionFactory;
import com.rabbitmq.client.DeliverCallback;
import com.typesafe.config.Config;
import com.typesafe.config.ConfigFactory;
import com.typesafe.config.ConfigRenderOptions;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Paths;
import java.time.ZoneOffset;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;

public class MaestroEndpoint implements Endpoint {
	private double stepSize = 0.0;
	private double finalTime = 0.0;
	private double startTime = 0.0;
	private ComponentConfiguration systemConfig;
	private Config coeConfig;
	private String outputPath;
	String coeFilename = "coe.json";
	String simulationFilename;
	// Data processing
	private CSVReader reader;
	private String[] columnNames;
	List<String> columnList;
	private List<String[]> myEntries;
	private int clock = 1;
	private String lastCommand = "simulate";
	
	//RabbitMQ
	boolean rabbitMQEnabled = false;
	boolean flagSend = false;
	String ip;
	int port;
	String username;
	String password;
	String exchange;
	String type;
	String vhost;
	String routingKey;
	ConnectionFactory factory;
	Connection conn;
	Channel channel;
	DeliverCallback deliverCallback;
	Map<String,Object> registeredAttributes;
	List<Operation> registeredOperations;
	
	public MaestroEndpoint() {
		// TODO Auto-generated constructor stub
	}
	
	public MaestroEndpoint(ComponentConfiguration config,String coeFilename, String outputPath)
	{
		//This one is the one to be used
		this.coeFilename = coeFilename;
		File file = new File(coeFilename);   
		this.coeConfig = ConfigFactory.parseFile(file);
		this.outputPath = outputPath;
		this.systemConfig = config;
		this.simulationFilename = this.systemConfig.conf.origin().filename();
		this.stepSize = this.systemConfig.conf.getDouble("algorithm.size");
		//this.finalTime = this.systemConfig.conf.getDouble("endTime");
		//this.startTime = this.systemConfig.conf.getDouble("startTime");
		
		/***** If RabbitMQFMU is enabled *****/
		if (this.systemConfig.conf.hasPath("rabbitmq")) {
			//System.out.println("RabbitMQ enabled");
			this.rabbitMQEnabled = true;
			this.ip = this.systemConfig.conf.getString("rabbitmq.ip");
			this.port = this.systemConfig.conf.getInt("rabbitmq.port");
			this.username = this.systemConfig.conf.getString("rabbitmq.username");
			this.password = this.systemConfig.conf.getString("rabbitmq.password");
			this.exchange = this.systemConfig.conf.getString("rabbitmq.exchange");
			this.type = this.systemConfig.conf.getString("rabbitmq.type");
			this.vhost = this.systemConfig.conf.getString("rabbitmq.vhost");
			this.routingKey = this.systemConfig.conf.getString("rabbitmq.routing_key");
			
			this.deliverCallback = (consumerTag, delivery) -> {
				String message = new String(delivery.getBody(), "UTF-8");
				String keyStart = "waiting for input data for simulation";
				if (message.contains(keyStart)) {
					this.flagSend = true;
				}
	      	};
			
			this.factory = new ConnectionFactory();
			if (this.password.equals("")){
				
			}else {
				this.factory.setUsername(this.username);
				this.factory.setPassword(this.password);
			}
			//this.factory.setVirtualHost(this.vhost);
			this.factory.setHost(this.ip);
			this.factory.setPort(this.port);

			try {
				this.conn = this.factory.newConnection();
				this.channel = this.conn.createChannel();
				this.channel.exchangeDeclare(this.exchange,"direct");
				String queueName = this.channel.queueDeclare().getQueue();
				this.channel.queueBind(queueName, this.exchange, this.routingKey);
				//this.channel.basicConsume(queueName, this.deliverCallback, null);
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			} catch (TimeoutException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
			
		}
		
		
		
	}

	@Override
	public void registerOperation(String name, Operation op) {
		//Only relevant when RabbitMQFMU is in use
		//name = RabbitMQFMU variable
		this.registeredOperations.add(op);
	}

	@Override
	public void registerAttribute(String name, Object obj) {
		//Only relevant when RabbitMQFMU is in use
		//name = RabbitMQFMU variable
		this.registeredAttributes.put(name,obj);
		/*
		String queue = name + ":queue";
		try {
			channel.queueDeclare(queue, false, true, false, null);
		} catch (IOException e1) {
			e1.printStackTrace();
		}
		try {
			channel.queueBind(queue, this.routingKey, this.routingKey);
		} catch (IOException e) {
			e.printStackTrace();
		}
		
		
		this.deliverCallback = (consumerTag, delivery) -> {
			for (Map.Entry<String, Object> entry : this.registeredAttributes.entrySet()) {
				try {
					final String message = new String(delivery.getBody(), "UTF-8");
			        JSONObject jsonMessage = new JSONObject(message);
			        String alias = mapAlias(entry.getKey());
			        Object value = jsonMessage.getJSONObject("fields").get(alias);
			        entry.setValue(value);
				} catch (Exception e) {
				}
			}
      	};
      	try {
      		channel.basicConsume(queue, true, this.deliverCallback, consumerTag -> {});
		} catch (IOException e) {
			e.printStackTrace();
		}
		*/
	}

	@Override
	public List<Object> getAttributeValues(List<String> variables) {
		// from the csv output file
		List<Object> values = new ArrayList<Object>();
		for (String var : variables) {
			Object value = this.getAttributeValue(var);
			values.add(value);
		}
		return values;
	}

	@Override
	public Object getAttributeValue(String variable) {
		// from the csv output file
		String[] entry = myEntries.get(1);
		if (this.lastCommand.equals("simulate")) {
			entry = myEntries.get(this.clock + 1);
		}else if(this.lastCommand.equals("doStep")) {
			entry = myEntries.get(2);
		}
		List<String> entryList = Arrays.asList(entry);
		Object value = null;
	    for (String column : this.columnList) {
	    	if(variable.equals(column)) {
	    		int i = this.columnList.indexOf(column);
	    		value =  (Object)(entryList.get(i));
	    	}
	    }
		return value;
	}
	
	public Object getAttributeValue(String variable, String twinName) {
		// from the csv output file
		String twinRaw = mapAlias(twinName);
		String varRaw = mapAlias(variable);
		String composedRaw = twinRaw + "." + varRaw;
		String[] entry = myEntries.get(1);
		if (this.lastCommand.equals("simulate")) {
			entry = myEntries.get(this.clock + 1);
		}else if(this.lastCommand.equals("doStep")) {
			entry = myEntries.get(2);
		}
		List<String> entryList = Arrays.asList(entry);
		Object value = null;
	    for (String column : this.columnList) {
	    	if(composedRaw.equals(column)) {
	    		int i = this.columnList.indexOf(column);
	    		value =  (Object)(entryList.get(i));
	    	}
	    }
		return value;
	}
	
	public Object getAttributeValue(String variable, int position) {
		// from the csv output file
		String[] entry = myEntries.get(position);
		List<String> entryList = Arrays.asList(entry);
		Object value = null;
	    for (String column : this.columnList) {
	    	if(variable.equals(column)) {
	    		int i = this.columnList.indexOf(column);
	    		value =  (Object)(entryList.get(i));
	    	}
	    }
		return value;
	}
	
	public Object getAttributeValue(String variable, int position, String twinName) {
		// from the csv output file
		String twinRaw = mapAlias(twinName);
		String varRaw = mapAlias(variable);
		String composedRaw = twinRaw + "." + varRaw;
		String[] entry = myEntries.get(position);
		List<String> entryList = Arrays.asList(entry);
		Object value = null;
	    for (String column : this.columnList) {
	    	if(composedRaw.equals(column)) {
	    		int i = this.columnList.indexOf(column);
	    		value =  (Object)(entryList.get(i));
	    	}
	    }
		return value;
	}
	
	@Override
	public void setAttributeValues(List<String> variables, List<Object> values) {
		if(this.rabbitMQEnabled) {
			Map<String,String> body = new HashMap<String,String>();
			String ts = ZonedDateTime.now( ZoneOffset.UTC ).format( DateTimeFormatter.ISO_INSTANT);
			body.put("time", ts);
			for (int i=0; i<variables.size();i++) {				
				body.put(variables.get(i), values.get(i).toString());				
			}
			JSONObject bodyJSON = new JSONObject(body);
			String bodyMessage = bodyJSON.toString();
			this.rawSend(bodyMessage);	
		}else {
			// On the multimodel.json file
			for (String var : variables) {
				int index = variables.indexOf(var);
				this.setAttributeValue(var, values.get(index));
			}
		}
		
		
		
	}

	@Override
	public void setAttributeValue(String variable, Object value) {
		if(this.rabbitMQEnabled) {
			Map<String,String> body = new HashMap<String,String>();
			String ts = ZonedDateTime.now( ZoneOffset.UTC ).format( DateTimeFormatter.ISO_INSTANT);
			body.put("time", ts);
			body.put(variable, value.toString());
			JSONObject bodyJSON = new JSONObject(body);
			String bodyMessage = bodyJSON.toString();
			this.rawSend(bodyMessage);
		}else {
			// On the multimodel.json file
			String fileString = this.systemConfig.conf.root().render(ConfigRenderOptions.concise().setFormatted(true).setJson(true));
			JSONObject completeJsonObject = new JSONObject(fileString);
			if (variable.equals("step_size") || variable.equals("stepSize")) {
				JSONObject innerjsonObject = new JSONObject(fileString).getJSONObject("algorithm");
				innerjsonObject.put("size",value);
				completeJsonObject.put("algorithm", innerjsonObject);
				try (FileWriter file = new FileWriter(this.simulationFilename)) 
		        {
		            file.write(completeJsonObject.toString(4));
		            file.close();
		        } catch (IOException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
			}else {
				JSONObject innerjsonObject = new JSONObject(fileString).getJSONObject("parameters");
				innerjsonObject.put(variable,value);
				completeJsonObject.put("parameters", innerjsonObject);
				try (FileWriter file = new FileWriter(this.simulationFilename)) 
		        {
		            file.write(completeJsonObject.toString(4));
		            file.close();
		            
		        } catch (IOException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
			}
			this.systemConfig = new ComponentConfiguration(this.simulationFilename);
		}
		
	}
	
	public void setAttributeValue(String variable, Object value, String twinName) {
		if(this.rabbitMQEnabled) {
			Map<String,String> body = new HashMap<String,String>();
			String ts = ZonedDateTime.now( ZoneOffset.UTC ).format( DateTimeFormatter.ISO_INSTANT);
			body.put("time", ts);
			body.put(variable, value.toString());
			JSONObject bodyJSON = new JSONObject(body);
			String bodyMessage = bodyJSON.toString();
			this.rawSend(bodyMessage);
			
		}else {
			// On the multimodel.json file
			String twinRaw = mapAlias(twinName);
			String varRaw = mapAlias(variable);
			String composedRaw = twinRaw + "." + varRaw;
			String fileString = this.systemConfig.conf.root().render(ConfigRenderOptions.concise().setFormatted(true).setJson(true));
			JSONObject completeJsonObject = new JSONObject(fileString);
			if (variable.equals("step_size") || variable.equals("stepSize")) {
				JSONObject innerjsonObject = new JSONObject(fileString).getJSONObject("algorithm");
				innerjsonObject.put("size",value);
				completeJsonObject.put("algorithm", innerjsonObject);
				try (FileWriter file = new FileWriter(this.simulationFilename)) 
		        {
		            file.write(completeJsonObject.toString(4));
		            file.close();
		        } catch (IOException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
			}else {
				JSONObject innerjsonObject = new JSONObject(fileString).getJSONObject("parameters");
				innerjsonObject.put(composedRaw,value);
				completeJsonObject.put("parameters", innerjsonObject);
				try (FileWriter file = new FileWriter(this.simulationFilename)) 
		        {
		            file.write(completeJsonObject.toString(4));
		            file.close();
		            
		        } catch (IOException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
			}
			this.systemConfig = new ComponentConfiguration(this.simulationFilename);
		}
	}
	
	public void simulate() {
		//with the arguments defined in coe.json and multimodel.json
		org.intocps.maestro.Main.argumentHandler(
				new String[]{"import","sg1",this.coeFilename,this.simulationFilename, "-output",this.outputPath});
		org.intocps.maestro.Main.argumentHandler(
                new String[]{"interpret", "--verbose", Paths.get(outputPath,"spec.mabl").toString(),"-output",this.outputPath});
		try {
			this.reader = new CSVReaderBuilder(new FileReader(Paths.get(outputPath,"outputs.csv").toString())).build();
			this.myEntries = this.reader.readAll();
			this.columnNames = this.myEntries.get(0);
			this.columnList = Arrays.asList(this.columnNames);
		} catch (FileNotFoundException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (CsvException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
	
	public void simulate(double endTime) {
		//fixedEndtime
		String fileString = this.coeConfig.root().render(ConfigRenderOptions.concise().setFormatted(true).setJson(true));
		JSONObject jsonObject = new JSONObject(fileString);
		jsonObject.put("startTime",0.0);
		jsonObject.put("endTime",endTime);
		try (FileWriter file = new FileWriter(this.coeFilename)) 
        {
			//ObjectWriter writer = mapper.defaultPrettyPrintingWriter();
            file.write(jsonObject.toString(4));
            file.close();
            File fileRead = new File(this.coeFilename);   
            this.coeConfig = ConfigFactory.parseFile(fileRead);
            
        } catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		this.simulate();
	}
	
	public void simulate(double startTime,double endTime) {
		//fixed endTime and fixed startTime
		String fileString = this.coeConfig.root().render(ConfigRenderOptions.concise().setFormatted(true).setJson(true));
		JSONObject jsonObject = new JSONObject(fileString);
		jsonObject.put("startTime",startTime);
		jsonObject.put("endTime",endTime);
		try (FileWriter file = new FileWriter(this.coeFilename)) 
        {
            file.write(jsonObject.toString(4));
            file.close();
            File fileRead = new File(this.coeFilename);
            this.coeConfig = ConfigFactory.parseFile(fileRead);
            
        } catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		this.simulate();
	}
	
	private void doStep() {
		this.simulate(0.0,this.stepSize*2);
	}
	


	@Override
	public void executeOperation(String opName, List<?> arguments) {
		if (opName.equals("simulate")) {
			this.lastCommand = "simulate";
			if(arguments == null) {
				
			}else {
				this.stepSize = (double) arguments.get(0);
				if (arguments.size() > 1) {
					Map<String,Double> args = (Map<String, Double>) arguments.get(1);
					for (Map.Entry<String, Double> entry : args.entrySet()) {
					    this.setAttributeValue(entry.getKey(), entry.getValue());
					}
				}
			}
			this.simulate();
		}else if(opName.equals("doStep")) {
			this.lastCommand = "doStep";
			if(arguments == null) {
				
			}else {
				this.stepSize = (double) arguments.get(0);
				if (arguments.size() > 1) {
					Map<String,Double> args = (Map<String, Double>) arguments.get(1);
					for (Map.Entry<String, Double> entry : args.entrySet()) {
					    this.setAttributeValue(entry.getKey(), entry.getValue());
					}
				}
			}
			this.doStep();
		}
		
	}
	
	public void setClock(int value) {
		this.clock = value;
	}
	
	public int getClock() {
		return this.clock;
	}
	
	private String mapAlias(String in) {
		String out = "";
		try {
			out = this.systemConfig.conf.getString("aliases." + in);
		}catch(Exception e) {
			out = in;
		}
		
		return out;
	}
	
	/***** RabbitMQFMU support *****/
	public void rawSend(String message) {
		if (this.flagSend == true) {
			try {
				this.channel.basicPublish(this.exchange, this.routingKey, null, message.getBytes());
			} catch (IOException e) {
				e.printStackTrace();
			}
		}
		
	}

}
