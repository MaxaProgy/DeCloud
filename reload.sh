sudo docker-compose down
sudo docker rmi $(sudo docker images -a -q)
sudo rm -r data
sudo git reset --hard HEAD
sudo git clean -f
git pull https://AlexZyryanov72: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@github.com/AlexZyryanov72/DeCloud.git
sudo docker-compose up -d

