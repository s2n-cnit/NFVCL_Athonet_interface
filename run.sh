#!/bin/bash
screen -S nfvcl_interface -dm bash -c 'uvicorn main:app --host 0.0.0.0 --port 5002 --reload >> nfvcl_interface.log 2>&1'
