#!/bin/bash
echo "install python3..."
sudo apt-get -y install python3.8
echo "install uvicorn..."
sudo apt-get -y install uvicorn
echo "install pip..."
sudo apt-get -y install python3-pip
echo "install python requirements..."
pip3 install -r requirements
echo "install mongodb..."
sudo apt-get install mongodb
