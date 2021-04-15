sudo apt update
sudo apt upgrade -y
sudo apt install supervisor -y
sudo apt install python3-pip -y
sudo chown -R root /root/
mkdir bot
cd bot
pip3 install -r requirements.txt
sudo cp supervisor-bot.conf /etc/supervisor/conf.d/
sudo supervisorctl reload