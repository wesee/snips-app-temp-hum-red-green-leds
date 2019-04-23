#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from snipsTools import SnipsConfigParser
from hermes_python.hermes import Hermes
from hermes_python.ontology import *
import io
import requests

CONFIG_INI = "config.ini"

# If this skill is supposed to run on the satellite,
# please get this mqtt connection info from <config.ini>
# Hint: MQTT server is always running on the master device
MQTT_IP_ADDR = "localhost"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))

class TempHumRedGreenLeds(object):
    """Class used to wrap action code with mqtt connection
        
        Please change the name refering to your application
    """

    def __init__(self):
        # get the configuration if needed
        try:
            self.config = SnipsConfigParser.read_configuration_file(CONFIG_INI)
        except :
            self.config = None

        # start listening to MQTT
        self.start_blocking()
        

    # --> Sub callback function, one per intent

    def askTemperature_callback(self, hermes, intent_message):
        # terminate the session first if not continue
        hermes.publish_end_session(intent_message.session_id, "")
        
        # action code goes here...
        print('[Received] intent: {}'.format(intent_message.intent.intent_name))
        
        temp = requests.get("http://192.168.2.233:8080/rest/items/exec_command_7b587029_output/state")

        message = "The temperature is " + temp.text + " degree Celcius."

        # if need to speak the execution result by tts
        hermes.publish_start_session_notification(intent_message.site_id, message, "openHAB_APP")

    def askHumidity_callback(self, hermes, intent_message):
        # terminate the session first if not continue
        hermes.publish_end_session(intent_message.session_id, "")
        
        # action code goes here...
        print('[Received] intent: {}'.format(intent_message.intent.intent_name))
        
        hum = requests.get("http://192.168.2.233:8080/rest/items/exec_command_298d9701_output/state")

        message = "The relative humidity is " + hum.text + " percent."

        # if need to speak the execution result by tts
        hermes.publish_start_session_notification(intent_message.site_id, message, "openHAB_APP")

    def askLight_callback(self, hermes, intent_message, message):
        # terminate the session first if not continue
        hermes.publish_end_session(intent_message.session_id, "")
        
        # action code goes here...
        print('[Received] intent: {}'.format(intent_message.intent.intent_name))
        
        # if need to speak the execution result by tts
        hermes.publish_start_session_notification(intent_message.site_id, message, "openHAB_APP")


    # More callback function goes here...

    # --> Master callback function, triggered everytime an intent is recognized
    def master_intent_callback(self,hermes, intent_message):
        coming_intent = intent_message.intent.intent_name
        if coming_intent == 'wesee:red_light_on':
            self.askLight_callback(hermes, intent_message, "Turning on red light.")

        if coming_intent == 'wesee:red_light_off':
            self.askLight_callback(hermes, intent_message, "Turning off red light.")

        if coming_intent == 'wesee:green_light_on':
            self.askLight_callback(hermes, intent_message, "Turning on green light.")

        if coming_intent == 'wesee:green_light_off':
            self.askLight_callback(hermes, intent_message, "Turning off green light.")

        if coming_intent == 'wesee:ask_humidity':
            self.askHumidity_callback(hermes, intent_message)

        if coming_intent == 'wesee:ask_temperature':
            self.askTemperature_callback(hermes, intent_message)

        # more callback and if condition goes here...

    # --> Register callback function and start MQTT
    def start_blocking(self):
        with Hermes(MQTT_ADDR) as h:
            h.subscribe_intents(self.master_intent_callback).start()

if __name__ == "__main__":
    TempHumRedGreenLeds()
