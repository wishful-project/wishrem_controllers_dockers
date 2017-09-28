Global controllers and docker files
============================

Download from GitHub
====================================

	sudo apt-get install git
	git clone https://github.com/wishful-project/wishrem_controllers_dockers
	cd wishrem_controllers_dockers/

Requirements installation
============

	sudo xargs apt-get install -y < requirements.system

When installing mysql, select to use as root with password "rem"

	cd db/
	python3 MySQLtables.py
	cd ..

Installation
============

	pip3 install -r requirements.txt --upgrade

Running examples
================

1. Uniflex broker init
	
	sudo uniflex-broker --xpub tcp://0.0.0.0:8990 --xsub tcp://0.0.0.0:8989

2. Node initialization:

	cd init_device_locations/

	python3 init_devices.py

3. REM controller:

	cd rem_controller/

Change IP address of sub and pub to be the IP address of the broker (in yaml file) 

	sudo uniflex-agent --config ./config_rem.yaml

4. Node controller:

	cd node_controller/

Change IP address of sub and pub to be the IP address of the broker (in yaml file) 

	sudo uniflex-agent --config ./config_master.yaml

5. RRM controller:

	cd rrm_controller/

Change IP address of sub and pub to be the IP address of the broker (in yaml file)

	sudo uniflex-agent --config ./config_rrm.yaml

6. REM console:

	cd rem_console/

	python3 REM_console.py


Alternative (TWIST testbed) install
================

Install docker compose (docker_install.sh on Ubuntu 16.04) and run rebuild_docker.sh.

After install you should run console application dockers manually
For node controller:
	sudo docker exec -it wishrem_nodes_controller bash
And then:
	uniflex-agent --config config_master.yaml

For REM console:
	sudo docker exec -it wishrem_rem_console bash
And then:
	uniflex-agent --config config_console.yaml

## Acknowledgement
The research leading to these results has received funding from the European
Horizon 2020 Programme under grant agreement n645274 (WiSHFUL project).
