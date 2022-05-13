sudo dpkg --configure -a
sudo apt-get update
sudo apt-get upgrade -y

sudo iptables -A INPUT -p tcp --dport 9000 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 9100 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 9200 -j ACCEPT
sudo iptables-save

sudo apt-get install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get -y install python3.7 python3.7-venv python3.7-dev build-essential
python3.7 -m venv venv
source ./venv/bin/activate
venv/bin/python3.7 -m pip install --upgrade pip
venv/bin/python3.7 -m pip install -r requirements.txt
sudo venv/bin/python3.7 register_domain_name.py
deactivate