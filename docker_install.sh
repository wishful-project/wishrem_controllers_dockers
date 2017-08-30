sudo apt-get update
sudo apt-get install apt-transport-https ca-certificates -y
sudo apt-key adv –keyserver hkp://p80.pool.sks-keyservers.net:80 –recv-keys 58118E89F3A912897C070ADBF76221572C52609D
sudo bash -c 'echo "deb https://apt.dockerproject.org/repo ubuntu-xenial main" >> /etc/apt/sources.list.d/docker.list'
sudo apt-get update
sudo apt-get purge lxc-docker
apt-cache policy docker-engine
sudo apt-get update
sudo apt-get install linux-image-extra-$(uname -r) linux-image-extra-virtual -y
sudo apt-get update
sudo apt-get install docker-ce -y
sudo service docker start
sudo docker run hello-world
sudo apt install docker-compose -y
sudo usermod -aG docker ${USER}
groups $USER
