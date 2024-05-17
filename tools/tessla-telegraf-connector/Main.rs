mod monitor;

extern crate tessla_stdlib;
use crate::monitor::*;
use std::time::SystemTime;
use tessla_stdlib::*;

use std::net::{IpAddr, Ipv4Addr, SocketAddr, UdpSocket};

@VALID_MEASUREMENTS_ARRAY

@VALID_TAGS_ARRAY

type TesslaOutputBool = fn(tessla_stdlib::TesslaValue<bool>, i64) -> Result<(), i64>;
type TesslaOutputInt = fn(tessla_stdlib::TesslaValue<i64>, i64) -> Result<(), i64>;
type TesslaOutputFloat = fn(tessla_stdlib::TesslaValue<f64>, i64) -> Result<(), i64>;

@TESSLA_MONITOR_TYPE_DEFINITION

const OWN_PORT_SEND: u16 = 1655;
const TELEGRAF_PORT: u16 = 1654;
const OWN_PORT_RECEIVE: u16 = 1653;
const TELEGRAF_IP: [u8; 4] = [127, 0, 0, 1];

const BUF_SIZE: usize = 1024;

fn send_data(
    socket: UdpSocket,
    measurement_name: String,
    tags: Option<Vec<(String, String)>>,
    fields: Vec<(String, String)>,
    timestamp: Option<i64>,
) {
    let address = SocketAddr::new(
        IpAddr::V4(Ipv4Addr::new(
            TELEGRAF_IP[0],
            TELEGRAF_IP[1],
            TELEGRAF_IP[2],
            TELEGRAF_IP[3],
        )),
        TELEGRAF_PORT,
    );
    let mut string_to_send = measurement_name;
    // insert possible tags
    match tags {
        Some(tagsSome) => {
            let mut i = 1;
            for (tag_name, tag_val) in tagsSome {
                string_to_send.push(',');
                string_to_send.push_str(&tag_name);
                string_to_send.push('=');
                string_to_send.push_str(&tag_val);
            }
        }
        None => {}
    }
    string_to_send.push(' ');
    let mut firstVal = true;
    // insert fields
    for (field_name, field_val) in fields {
        if (!firstVal){
            string_to_send.push(',');
            firstVal = false;
        }
        string_to_send.push_str(&field_name);
        string_to_send.push('=');
        string_to_send.push_str(&field_val);
    }

    match timestamp {
        Some(time) => {
            string_to_send.push(' ');
            string_to_send.push_str(&time.to_string());
        }
        None => {}
    }

    let buf = string_to_send.as_bytes();
    println!("send to telegraf: \"{}\"", string_to_send);
    socket.send_to(buf, &address);
}

fn receive_data(
    socket: UdpSocket,
    on_receive: fn(&String, &String, &String, i64, &mut TesslaMonitorType),
    tessla_monitor: &mut TesslaMonitorType,
) {
    let mut tessla_time: i64 = 0;
    let mut buf = [0; BUF_SIZE - 1];
    println!("Start listening...");
    loop {
        // clear buf
        for i in 0..(BUF_SIZE - 1) {
            buf[i] = 0;
        }
        // receive stuff
        let (number_of_bytes, scr_addr) =
            socket.recv_from(&mut buf).expect("Error on receiving data");
        //output data
        let outp_string = match std::str::from_utf8(&buf) {
            Ok(v) => v,
            Err(e) => "Cannot interprete Buf as String.",
        };
        let (id, time, key_value_pairs) =
            interprete_influx_string(outp_string.clone().to_string());
        if (id == "nil"){
            continue;
        }
        tessla_time = update_time(time, tessla_time);
        match (key_value_pairs) {
            None => {
                println!("Cannot consume input String: {}", outp_string);
            }
            Some(key_vals) => {
                for (key, value) in key_vals {
                    println!("{}:{}= {}", id, key, value);
                    on_receive(&id, &key, &value, tessla_time, tessla_monitor);
                }
            }
        }
    }
}

fn interprete_influx_string(
    inp_str: String,
) -> (
    String,         //matching ID String
    Option<String>, //Timestring
    Option<Vec<(String, String)>>,
) {
    // println!("got from telegraf: \"{}\"", inp_str);
    // key value pair
    let mut time_string: Option<String> = None;

    // Split the received string into its parts according to the influx line protocol
    let mut input_parts = inp_str.split(' ');
    let id_string = input_parts.next().expect("Message from telegraf is empty");
    let inp_fields_str = input_parts.next().expect("Message from telegraf does not contain any spaces");
    let inp_timestamp = input_parts.next().expect("Message from telegraf does not contain a Timestamp");

    let mut inp_measurement_tags_iter = id_string.split(',');
    let inp_measurement = inp_measurement_tags_iter.next().expect("Message contains empty measurement name");
    let inp_tags = inp_measurement_tags_iter.collect::<Vec<&str>>();

    //ignore invalid mesurements
    if !VALID_MEASUREMENTS.contains(&inp_measurement) {
        //println!("Measurement {} is not one of: {:?}, ignoring message", inp_measurement, VALID_MEASUREMENTS);
        return ("nil".to_string(), time_string, None);
    }

    //check all if all required tags are in the message, return if not
    for valid_tag in VALID_TAGS {
        if !inp_tags.contains(&valid_tag) {
            //println!("Tag {} required, but message only contains: {:?}, ignoring message", valid_tag, inp_tags);
            return ("nil".to_string(), time_string, None)
        }
    }

    println!("Valid Message: {}", inp_str);

    let mut fields: Vec<(String, String)> = Vec::<(String, String)>::new();
    let pairs = inp_fields_str.split(',');
    for pair in pairs {
        let key_value: Vec<&str> = pair.split('=').collect();
        fields.push((key_value[0].to_string(), key_value[1].to_string()));
    }

    return (id_string.to_string(), time_string, Some(fields));
}

fn update_time(timeInput: Option<String>, current_tessla_time: i64) -> i64 {
    let mut new_tessla_time: i64 = 0;
    match (timeInput) {
        None => {
            match SystemTime::now().duration_since(SystemTime::UNIX_EPOCH) {
                Ok(n) => {
                    new_tessla_time = <u128 as TryInto<i64>>::try_into(n.as_millis()).unwrap() * 1000000;
                }
                Err(_) => panic!("System time is invalid!"),
            }
        }
        Some(inp_string) => {
            new_tessla_time = inp_string.parse::<i64>().unwrap();
        }
    }
    if new_tessla_time < current_tessla_time {
        panic!(
            "Order of timestamps is broken! {} < {}",
            new_tessla_time, current_tessla_time
        );
    }
    return new_tessla_time;
}

@REACT_ON_INPUT_FUNTION


@HANDLE_TESSLA_OUTPUT_FUNCTIONS


fn get_sending_socket() -> UdpSocket {
    let addrs = [
        SocketAddr::from((TELEGRAF_IP, OWN_PORT_SEND)),
        SocketAddr::from((TELEGRAF_IP, OWN_PORT_SEND + 1)),
        SocketAddr::from((TELEGRAF_IP, OWN_PORT_SEND + 2)),
        SocketAddr::from((TELEGRAF_IP, OWN_PORT_SEND + 3)),
    ];
    let sending_socket = Some(
        UdpSocket::bind(get_ip_string_remote() + &":".to_string() + &OWN_PORT_SEND.to_string())
            .expect(&(get_ip_string_remote() + &":".to_string() + &OWN_PORT_SEND.to_string())),
    );
    match sending_socket {
        Some(socket) => return socket,
        None => panic!("Cannot create Socket"),
    }
}

fn get_ip_string_remote() -> String {
    let ip_string = TELEGRAF_IP[0].to_string()
        + &".".to_owned()
        + &TELEGRAF_IP[1].to_string()
        + &".".to_owned()
        + &TELEGRAF_IP[2].to_string()
        + &".".to_owned()
        + &TELEGRAF_IP[3].to_string();
    return ip_string;
}

fn get_ip_string_own() -> String {
    return "127.0.0.1".to_string();
}

fn init_telegraf_udp_connection(tessla_monitor: &mut TesslaMonitorType) {
    let receiving_socket: Option<UdpSocket> = Some(
        UdpSocket::bind(get_ip_string_own() + &":".to_string() + &OWN_PORT_RECEIVE.to_string())
            .expect(&(get_ip_string_own() + &":".to_string() + &OWN_PORT_RECEIVE.to_string())),
    );
    match receiving_socket {
        Some(rec_socket) => receive_data(rec_socket, react_on_input, tessla_monitor),
        None => panic!("Something went wrong."),
    }
}

fn main() {

    // init telegraf connection
    @INSTANTIATE_TESSLA_MONITOR

    init_telegraf_udp_connection(&mut tessla_monitor);
}
