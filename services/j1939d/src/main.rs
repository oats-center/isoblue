mod j1939;

use anyhow::Context;
use canparse::pgn::{ParseMessage, PgnLibrary};
use j1939::J1939Socket;
use serde_json::json;

use clap::{crate_authors, crate_description, crate_name, crate_version, App, Arg};

fn main() -> anyhow::Result<()> {
    let matches = App::new(crate_name!())
        .version(crate_version!())
        .author(crate_authors!())
        .about(crate_description!())
        .arg(
            Arg::with_name("can_interface")
                .index(1)
                .env("CAN_INTERFACE")
                .takes_value(true)
                .help("SocketCAN interface to monitor"),
        )
        .arg(
            Arg::with_name("dbc_file")
                .index(2)
                .env("DBC_FILE")
                .takes_value(true)
                .help("DBC file to decode with"),
        )
        .arg(
            Arg::with_name("nats_server")
                .index(3)
                .env("NATS_SERVER")
                .takes_value(true)
                .help("NATS connection string"),
        )
        .arg(
            Arg::with_name("nats_sub_prefix")
                .long("sub_prefix")
                .env("NATS_SUB_PREFIX")
                .takes_value(true)
                .default_value("j1939")
                .help("NATS subject prefix"),
        )
        .get_matches();

    let can_interface = matches
        .value_of("can_interface")
        .with_context(|| "SocketCAN interface not provided")?;

    let nats_server = matches
        .value_of("nats_server")
        .with_context(|| "NATS connection string not provided")?;

    let nats_sub_prefix = matches
        .value_of("nats_sub_prefix")
        .with_context(|| "NATS subject prefix not provided?")?;

    let dbc_file = matches.value_of("dbc_file").with_context(|| {
        "No dbc file was
    provided?"
    })?;

    println!("Connecting to NATS");
    let nc = nats::connect(nats_server)
        .with_context(|| format!("Could not connect to NATS at {}", nats_server))?;
    println!("Connected to NATS");

    println!("Connecting to CAN");
    let mut s = J1939Socket::open(can_interface)
        .with_context(|| format!("Could not connect to can interface {}", can_interface))?;
    s.set_promisc(true)?;
    s.set_broadcast(true)?;
    s.set_timestamp(true)?;
    println!("Connected to CAN");

    println!("Loading DBC file");
    let lib = PgnLibrary::from_dbc_file(dbc_file)?;
    println!("Loaded DBC file");

    loop {
        let msg = s.recv()?;

        if let Some(pgn_def) = lib.get_pgn(msg.pgn) {
            for (s, spn) in pgn_def.get_spns().iter() {
                let value = spn.parse_message(msg.data);

                let sub = format!("{}.{}", nats_sub_prefix, s);
                nc.publish(
                    &sub,
                    serde_json::to_vec(&json!({
                        "pgn": msg.pgn,
                        "name": s,
                        "time": msg.timestamp.map(|t| t.timestamp_nanos() as f64 / 1_000_000_000.0),
                        "value": value,
                        "units": spn.units,
                        "min_value": spn.min_value,
                        "max_value": spn.max_value
                    }))
                    .with_context(|| {
                        "Failed to
                seralize frame"
                    })?,
                )
                .with_context(|| "Failed to send parsed j1939 frame to NATS")?;
            }
        }
    }
}
