# coding=utf-8
import os

modulname = "Core"
import socket
import sys
import subprocess

sys.path.insert(0, "lib/")
sys.path.insert(1, "lib/settings/")
import RPi.GPIO as GPIO
from flask import Flask
from flask import render_template
from flask_fontawesome import FontAwesome

from lib.pins import v_LED1_Pin, v_LED2_Pin, v_PUMP1_Pin, v_PUMP2_Pin
from lib.functions import console, uibootscreen, \
    SensorData, processing, statusscreen, gpiosetup, komponententester, getdbdata
import websettings
import version
lights = {
    v_LED1_Pin: {'name': 'LED Links', 'state': GPIO.LOW},
    v_LED2_Pin: {'name': 'LED Rechts', 'state': GPIO.LOW}
}
pumps = {
    v_PUMP1_Pin: {'name': 'Pumpe Links', 'state': GPIO.LOW},
    v_PUMP2_Pin: {'name': 'Pumpe Rechts', 'state': GPIO.LOW}
}

console(modulname, "System startet")
console(modulname, version.v_Application + version.v_Version)
console(modulname, version.v_Description)
console(modulname,"GPIO - Einrichtung")
gpiosetup()
komponententester()
console(modulname,"Display und Sensoren werden Initzalisiert !")
uibootscreen()
app = Flask(__name__, template_folder='dashboard')
fa = FontAwesome(app)





# GPIO Steuerung der Pflanzenlichter - Start
@app.route("/LIGHT/<changeLightPin>/<actionLight>/<returnto>")
def lightaction(changeLightPin, actionLight, returnto):
    # Convert the pin from the URL into an integer:
    changeLightPin = int(changeLightPin)
    # Get the device name for the pin being changed:
    deviceName = lights[changeLightPin]['name']
    # If the action part of the URL is "on," execute the code indented below:

    if actionLight == "on":
        # Set the pin high:
        GPIO.output(changeLightPin, GPIO.HIGH)
        # Save the status message to be passed into the template:
        message = "Schalte " + deviceName + " ein."
    if actionLight == "off":
        GPIO.output(changeLightPin, GPIO.LOW)
        message = "Schalte " + deviceName + " aus."
    for lpin in lights:
        lights[lpin]['state'] = GPIO.input(lpin)
    for ppin in pumps:
        pumps[ppin]['state'] = GPIO.input(ppin)

    Template_Pumps = {'pumps': pumps}
    Template_Lights = {'lights': lights}

    appversion: object = version.v_Version
    appname = version.v_Application
    Template_Sensor = SensorData("web")
    Template_Sensordaten = getdbdata("Temperatur")
    return render_template(returnto + '.html', title='Welcome', v_Application=appname, v_Version=appversion,
                           **Template_Pumps, **Template_Lights, **Template_Sensor,**Template_Sensordaten )

# GPIO Steuerung der Bewässerung - Start
@app.route("/Pump/<changePumpPin>/<actionPUMP>/<returnto>")
def pumpaction(changePumpPin, actionPUMP, returnto):
    # Convert the pin from the URL into an integer:

    changePumpPin = int(changePumpPin)
    # Get the device name for the pin being changed:
    deviceName = pumps[changePumpPin]['name']
    # If the action part of the URL is "on," execute the code indented below:

    if actionPUMP == "on":
        # Set the pin high:
        GPIO.output(changePumpPin, GPIO.HIGH)
        # Save the status message to be passed into the template:
        message = "Schalte " + deviceName + " ein."
    if actionPUMP == "off":
        GPIO.output(changePumpPin, GPIO.LOW)
        message = "Schalte " + deviceName + " aus."
    for lpin in lights:
        lights[lpin]['state'] = GPIO.input(lpin)
    for ppin in pumps:
        pumps[ppin]['state'] = GPIO.input(ppin)

    Template_Pumps = {'pumps': pumps}
    Template_Lights = {'lights': lights}

    appversion: object = version.v_Version
    appname = version.v_Application
    Template_Sensor = SensorData("web")
    Template_Sensordaten = getdbdata("Temperatur")
    return render_template(returnto + '.html', title='Welcome', v_Application=appname, v_Version=appversion,
                           **Template_Pumps, **Template_Lights, **Template_Sensor,**Template_Sensordaten )




@app.route('/')
@app.route('/index')
def index():
    for lpin in lights:
        lights[lpin]['state'] = GPIO.input(lpin)
    for ppin in pumps:
        pumps[ppin]['state'] = GPIO.input(ppin)

    Template_Pumps = {'pumps': pumps}
    Template_Lights = {'lights': lights}
    Template_Sensor = SensorData("web")
    Template_Sensordaten = getdbdata("Temperatur")
    appversion: object = version.v_Version
    appname = version.v_Application


    return render_template('index.html', title='Welcome', v_Application=appname, v_Version=appversion,
                           **Template_Pumps, **Template_Lights, **Template_Sensor,**Template_Sensordaten )


@app.route('/Light/')
def light():
    for lpin in lights:
        lights[lpin]['state'] = GPIO.input(lpin)
    for ppin in pumps:
        pumps[ppin]['state'] = GPIO.input(ppin)

    Template_Pumps = {'pumps': pumps}
    Template_Lights = {'lights': lights}
    Template_Sensor = SensorData("web")
    appversion: object = version.v_Version
    appname = version.v_Application
    Template_Sensordaten = getdbdata("Temperatur")
    return render_template('/light.html', title='Welcome', v_Application=appname, v_Version=appversion,
                           **Template_Pumps, **Template_Lights, **Template_Sensor,**Template_Sensordaten )


@app.route('/Pumps/')
def pumpen():
    for lpin in lights:
        lights[lpin]['state'] = GPIO.input(lpin)
    for ppin in pumps:
        pumps[ppin]['state'] = GPIO.input(ppin)

    Template_Pumps = {'pumps': pumps}
    Template_Lights = {'lights': lights}
    Template_Sensor = SensorData("web")
    statusscreen()
    appversion: object = version.v_Version
    appname = version.v_Application

    Template_Sensordaten = getdbdata("Temperatur")
    return render_template('/pumps.html', title='Welcome', v_Application=appname, v_Version=appversion,
                           **Template_Pumps, **Template_Lights, **Template_Sensor,**Template_Sensordaten )


@app.route('/Sensors/')
def sensors():
    for lpin in lights:
        lights[lpin]['state'] = GPIO.input(lpin)
    for ppin in pumps:
        pumps[ppin]['state'] = GPIO.input(ppin)
    console(modulname, "Rufe Sensordaten ab")
    Template_Sensor = SensorData("web")
    Template_Pumps = {'pumps': pumps}
    Template_Lights = {'lights': lights}
    appversion: object = version.v_Version
    appname = version.v_Application
    Template_Sensordaten = getdbdata("Temperatur")
    return render_template('/sensors.html', title='Welcome', v_Application=appname, v_Version=appversion,
                           **Template_Pumps, **Template_Lights, **Template_Sensor,**Template_Sensordaten )


@app.route('/Stats/')
def stats():
    for lpin in lights:
        lights[lpin]['state'] = GPIO.input(lpin)
    for ppin in pumps:
        pumps[ppin]['state'] = GPIO.input(ppin)

    Template_Pumps = {'pumps': pumps}
    Template_Lights = {'lights': lights}
    Template_Sensor = SensorData("web")
    appversion: object = version.v_Version
    appname = version.v_Application
    console(modulname, "Statistik wird geladen ...")
    console(modulname, "Statistik wird ausgewertet und bereitgestellt ...")
    Template_Sensordaten = getdbdata("Temperatur")

    return render_template('/stats.html', title='Welcome', v_Application=appname, v_Version=appversion,
                           **Template_Pumps, **Template_Lights, **Template_Sensor,**Template_Sensordaten )


@app.route('/system/restart')
def restartplanter():
    modulname="Systemdienst"
    for lpin in lights:
        lights[lpin]['state'] = GPIO.input(lpin)
    for ppin in pumps:
        pumps[ppin]['state'] = GPIO.input(ppin)

    Template_Pumps = {'pumps': pumps}
    Template_Lights = {'lights': lights}
    Template_Sensor = SensorData("web")
    appversion: object = version.v_Version
    appname = version.v_Application
    console(modulname, "Statistik wird geladen ...")
    console(modulname, "Statistik wird ausgewertet und bereitgestellt ...")
    Template_Sensordaten = getdbdata("Temperatur")


    subprocess.Popen(['./startup.sh restart'], shell=True)
    return render_template('/wait.html', title='Welcome', v_Application=appname, v_Version=appversion,
                           **Template_Pumps, **Template_Lights, **Template_Sensor,**Template_Sensordaten )
@app.route('/system/restartos')
def restartos():
    modulname="Systemdienst"
    for lpin in lights:
        lights[lpin]['state'] = GPIO.input(lpin)
    for ppin in pumps:
        pumps[ppin]['state'] = GPIO.input(ppin)

    Template_Pumps = {'pumps': pumps}
    Template_Lights = {'lights': lights}
    Template_Sensor = SensorData("web")
    appversion: object = version.v_Version
    appname = version.v_Application
    console(modulname, "Statistik wird geladen ...")
    console(modulname, "Statistik wird ausgewertet und bereitgestellt ...")
    Template_Sensordaten = getdbdata("Temperatur")


    subprocess.Popen(['reboot'], shell=True)
    return render_template('/wait.html', title='Welcome', v_Application=appname, v_Version=appversion,
                           **Template_Pumps, **Template_Lights, **Template_Sensor,**Template_Sensordaten )
@app.route('/Webcam/')
def webcam():
    for lpin in lights:
        lights[lpin]['state'] = GPIO.input(lpin)
    for ppin in pumps:
        pumps[ppin]['state'] = GPIO.input(ppin)

    Template_Pumps = {'pumps': pumps}
    Template_Lights = {'lights': lights}
    Template_Sensor= SensorData("web")
    appversion: object = version.v_Version
    appname = version.v_Application
    console(modulname, "Webcam Stream wurde gestartet")
    Template_Sensordaten = getdbdata("Temperatur")
    return render_template('/webcam.html', title='Welcome', v_Application=appname, v_Version=appversion,
                           **Template_Pumps, **Template_Lights, **Template_Sensor,**Template_Sensordaten )


if __name__ == "__main__":
    console(modulname, "Webserver startet bitte warten!")
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    console(modulname, "Web-Dashboard wurde gestartet")
    app.run(host=s.getsockname()[0], port=websettings.s_server_port)


