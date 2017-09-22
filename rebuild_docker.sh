sudo docker-compose down
sudo docker rm -f $(sudo docker ps -a -q)
sudo docker rmi -f $(sudo docker images -q)
sudo docker network rm $(sudo docker network ls -q)
sudo docker-compose up
