sudo docker-compose down
sudo docker rmi $(sudo docker images -a -q)
sudo rm -r data
sudo git reset --hard HEAD
sudo git clean -f
sudo git pull https://AlexZyryanov72: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@github.com/AlexZyryanov72/DeCloud.git
sudo docker-compose up -d

