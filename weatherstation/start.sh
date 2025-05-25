#!/bin/bash
sudo python3 /home/pi/Weather-Station/weatherstation/led_controller.py &
sleep 1
sudo python3 /home/pi/Weather-Station/weatherstation/weatherapp.py &
sleep 1
sudo python3 /home/pi/Weather-Station/weatherstation/log.py &
wait
