# The Avena Architecture
This a a quick (Very WIP) summary of the Avena Architecture and the design decisions we made
 
 ## Design Requirements


## Hardware
### Hardware Requirements
When choosing the base single board computer for the Avena, we considered the following requirements:
- An x86 Platform for ease of use with pre-compiled libraries
- 12v input power for use in vehicles
- 2 CAN Bus inputs
- M2 connector for additional storage via SSD
- MPI connector for cell modem
- Integrated WiFi and Bluetooth for
- 
At the time of our selection, there were no reasonably priced single board computers that fulfilled all of these requirements. We chose a SBC that fulfilled many of the requirements and then designed an additional board to fulfill the missing requirements

### LattePanda

### Custom Hat

### Enclosure
## Software
Fig 1 shows a pictorial representation of the Avena software stack:
![Avena Arch](./AvenaArch.png)

### Apache Kafka
### PostgreSQL