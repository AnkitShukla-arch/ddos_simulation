# DDoS Simulation System

## Components
- Bot → generates IPv4/IPv6 traffic (normal + malicious)
- Model → receives IPs, identifies malicious traffic

## Run Model
cd model
pip install -r requirements.txt
python model_server.py

## Run Bot
cd bot
pip install -r requirements.txt
python bot.py --config config.yaml

