sudo docker-compose down
sudo docker rmi $(sudo docker images -a -q)
sudo rm -r data
sudo git reset --hard HEAD
sudo git clean -f
git pull
sudo docker-compose up -d

