use chrono::DateTime;
use gpsd_proto::{get_data, handshake, ResponseData};
use sqlx::PgPool;
use std::env;
use std::{
    io::{BufReader, BufWriter},
    net::TcpStream,
};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let gpsd_conn_str = env::var("gpsd_url").expect("Env var gpsd_host is required.");
    let postgres_conn_str = env::var("tsdb_url").expect("Env var tsdb_host is required.");
    let pool = PgPool::new(&postgres_conn_str).await?;

    if let Ok(stream) = TcpStream::connect(gpsd_conn_str) {
        println!("Connected to gpsd!");

        let mut reader = BufReader::new(&stream);
        let mut writer = BufWriter::new(&stream);

        handshake(&mut reader, &mut writer).unwrap();

        // let mut old_time = DateTime::parse_from_rfc3339(&"1970-01-01T00:00:00-00:00")?;
        loop {
            match get_data(&mut reader) {
                Ok(m) => {
                    if let ResponseData::Tpv(t) = m {
                        let time = DateTime::parse_from_rfc3339(&t.time.unwrap())?;

                        // if old_time.eq(&time) {
                        //     continue;
                        //}
                        //old_time = time;

                        sqlx::query(
                            r#"
                            INSERT INTO gps (time, lat, lng)
                            VALUES ($1, $2, $3)
                            "#,
                        )
                        .bind(time)
                        .bind(t.lat.unwrap())
                        .bind(t.lon.unwrap())
                        .execute(&pool)
                        .await?;

                        println!(
                            "{:} {:3} {:8.5} {:8.5} {:6.1} m {:5.1}   {:6.3} m/s",
                            time,
                            t.mode.to_string(),
                            t.lat.unwrap_or(0.0),
                            t.lon.unwrap_or(0.0),
                            t.alt.unwrap_or(0.0),
                            t.track.unwrap_or(0.0),
                            t.speed.unwrap_or(0.0)
                        );
                    }
                }
                Err(e) => println!("{:?}", e),
            }
        }
    } else {
        panic!("Could not connect to gpsd!");
    }
}
