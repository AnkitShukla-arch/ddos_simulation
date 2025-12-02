#!/bin/bash

cd model
uvicorn model_server:app --host 0.0.0.0 --port 8000 --reload &
cd ../bot
python bot.py --config config.yaml

