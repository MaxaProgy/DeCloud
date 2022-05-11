sudo docker-compose down
sudo docker rmi $(sudo docker images -a -q)
sudo rm -r data
sudo git reset --hard HEAD
sudo git clean -f
git pull https://github.com/MariaZyryanova72/DeCloud.git
sudo docker-compose up -d

