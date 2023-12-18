package dtmanager;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.TimeoutException;
import java.util.function.Function;
import java.util.stream.Collectors;

import org.eclipse.basyx.aas.manager.ConnectedAssetAdministrationShellManager;
import org.eclipse.basyx.aas.metamodel.connected.ConnectedAssetAdministrationShell;
import org.eclipse.basyx.aas.metamodel.map.descriptor.ModelUrn;
import org.eclipse.basyx.submodel.metamodel.api.ISubmodel;
import org.eclipse.basyx.submodel.metamodel.api.submodelelement.dataelement.IProperty;
import org.eclipse.basyx.submodel.metamodel.api.submodelelement.operation.IOperation;
import org.eclipse.basyx.submodel.metamodel.connected.submodelelement.dataelement.ConnectedProperty;
import org.eclipse.basyx.submodel.metamodel.connected.submodelelement.operation.ConnectedOperation;
import org.eclipse.basyx.submodel.metamodel.map.submodelelement.dataelement.property.Property;
import org.eclipse.basyx.submodel.metamodel.map.submodelelement.operation.Operation;
import org.eclipse.basyx.vab.manager.VABConnectionManager;
import org.eclipse.basyx.vab.protocol.http.connector.HTTPConnectorFactory;
import org.eclipse.basyx.vab.registry.proxy.VABRegistryProxy;
import org.json.JSONObject;

import com.rabbitmq.client.Channel;
import com.rabbitmq.client.Connection;
import com.rabbitmq.client.ConnectionFactory;
import com.rabbitmq.client.DeliverCallback;
import com.typesafe.config.Config;

public class RabbitMQEndpoint implements Endpoint {
	String ip;
	int port;
	String username;
	String password;
	String exchange;
	String type;
	String vhost;
	ConnectionFactory factory;
	Connection conn;
	Channel channel;
	DeliverCallback deliverCallback;
	TwinConfiguration twinConfig;
	Map<String,Object> registeredAttributes;
	List<Operation> registeredOperations;

	
	
	public RabbitMQEndpoint(TwinConfiguration config) {
		this.twinConfig = config;
		this.ip = config.conf.getString("rabbitmq.ip");
		this.port = config.conf.getInt("rabbitmq.port");
		this.username = config.conf.getString("rabbitmq.username");
		this.password = config.conf.getString("rabbitmq.password");
		this.exchange = config.conf.getString("rabbitmq.exchange");
		this.type = config.conf.getString("rabbitmq.type");
		this.vhost = config.conf.getString("rabbitmq.vhost");
		
		this.registeredAttributes = new HashMap<String,Object>();
		this.registeredOperations = new ArrayList<Operation>();
		
		this.deliverCallback = (consumerTag, delivery) -> {
			for (Map.Entry<String, Object> entry : this.registeredAttributes.entrySet()) {
				final String message = new String(delivery.getBody(), "UTF-8");
		        JSONObject jsonMessage = new JSONObject(message);
		        String alias = mapAlias(entry.getKey());
		        Object value = jsonMessage.getJSONObject("fields").get(alias);
		        entry.setValue(value);
			}
      	};
		
		factory = new ConnectionFactory();
		factory.setUsername(username);
		factory.setPassword(password);
		//factory.setVirtualHost(virtualHost);
		factory.setHost(ip);
		factory.setPort(port);

		try {
			conn = factory.newConnection();
		} catch (IOException | TimeoutException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		
		try {
			channel = conn.createChannel();
		} catch (IOException e3) {
			// TODO Auto-generated catch block
			e3.printStackTrace();
		}
		
		
	}
	
	public void rawSend(String message, String routingKey) {

		try {
			channel.basicPublish(exchange, routingKey, null, message.getBytes());
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
	
	public void registerOperation(String twinName,Operation op){
		this.registeredOperations.add(op);
		String opName = op.getIdShort();
		String queue = twinName + ":" +opName + ":queue";
		try {
			channel.queueDeclare(queue, false, true, false, null);
		} catch (IOException e1) {
			e1.printStackTrace();
		}
	}
	
	public void registerAttribute(String name, Object obj) {
		this.registeredAttributes.put(name,obj);
	
		String queue = name + ":queue";
		try {
			channel.queueDeclare(queue, false, true, false, null);
		} catch (IOException e1) {
			e1.printStackTrace();
		}
		try {
			String routingKey = mapRoutingKey(name);
			channel.queueBind(queue, exchange, routingKey);
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

	}
	
	private String mapRoutingKey(String in) {
		String out = this.twinConfig.conf.getString("rabbitmq.routing_keys." + in);
		return out;
	}
	
	private String mapAlias(String in) {
		String out = this.twinConfig.conf.getString("rabbitmq.aliases." + in);
		return out;
	}
	
	private List<String> mapOperationRoutingKey(String in) {
		List<String> out = this.twinConfig.conf.getStringList("rabbitmq.routing_keys.operations" + in);
		return out;
	}

	@Override
	public List<Object> getAttributeValues(List<String> variables) {
		List<Object> values = new ArrayList<Object>();
		for(String var : variables) {
			Object value = this.getAttributeValue(var);
			values.add(value);
		}
		return values;
	}

	@Override
	public Object getAttributeValue(String variable) {
		return this.registeredAttributes.get(variable);
	}

	@Override
	public void setAttributeValues(List<String> variables, List<Object> values) {
		for(String var : variables) {
			int index = variables.indexOf(var);
			this.setAttributeValue(var, values.get(index));
		}
	}

	@Override
	public void setAttributeValue(String variable, Object value) {
		this.registeredAttributes.put(variable, value);
		String routingKey = mapRoutingKey(variable);
		String message = String.valueOf(value);
		try {
			channel.basicPublish(exchange, routingKey, null, message.getBytes());
		} catch (IOException e) {
			e.printStackTrace();
		}
		
	}

	@Override
	public void executeOperation(String opName, List<?> arguments) {
		// TODO Auto-generated method stub
		List<String> routingKey = mapOperationRoutingKey(opName);
		String message = "";
		for (String rKey : routingKey) {
			int index = routingKey.indexOf(rKey);
			message = (String) arguments.get(index);
			try {
				channel.basicPublish(exchange, rKey, null, message.getBytes());
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
		}
	}

	@Override
	public Object getAttributeValue(String attrName, String twinName) {
		// Not applicable
		return null;
	}

	@Override
	public void setAttributeValue(String attrName, Object val, String twinName) {
		// Not applicable
		
	}

	@Override
	public void setClock(int value) {
		// TODO Auto-generated method stub
		
	}

	@Override
	public int getClock() {
		// TODO Auto-generated method stub
		return 0;
	}

	@Override
	public Object getAttributeValue(String attrName, int entry) {
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	public Object getAttributeValue(String attrName, int entry, String twinName) {
		// TODO Auto-generated method stub
		return null;
	}
	
}
