# coding=utf-8
from typing import Any

modulname = "Funktionen"
# Definition des Modulnamen
# Modulbeschreibung
# Grundlegende Funtionen für den Smartplanter
# Display Ansteuerung
# Datenbankverbindung und verarbeitung
# Steuerung der Relays
# Abfragen von Sensordaten
# Zugriff auf die Settings Variablen
# GPIO Steuerung

# Importblock  der Module
import base64
import datetime
import socket
import sqlite3
import time

import RPi.GPIO as GPIO
import Adafruit_DHT
import os
import lib.driver_lcd as driver_lcd

# Import von Funktionen und Variablen aus anderen Modulen
from pathlib import Path
from colorama import Fore
from lib import settings, version, pins
from lib.pins import v_temp_sensor_typ, v_temp_sensor_pin, v_LED1_Pin, v_LED2_Pin, v_PUMP1_Pin, v_PUMP2_Pin
from lib.settings import komponententest
from datetime import datetime

# Display Buffer
Zeile = ["Smart Planter", "Temperatur", "Feuchtigkeit", "Webserver :"]
mylcd = driver_lcd.lcd()

# GPIO Pin Status für Lícht und Pumpen
lights = {
    v_LED1_Pin: {'name': 'LED Links', 'state': GPIO.LOW},
    v_LED2_Pin: {'name': 'LED Rechts', 'state': GPIO.LOW}
}
pumps = {
    v_PUMP1_Pin: {'name': 'Pumpe Links', 'state': GPIO.LOW},
    v_PUMP2_Pin: {'name': 'Pumpe Rechts', 'state': GPIO.LOW}
}


# GPIO Setup
def gpiosetup():
    modulname = "GPIO"
    console(modulname, "Konfiguriere GPIO-Pins")
    GPIO.setmode(GPIO.BCM)  # Set's GPIO pins to BCM GPIO numbering
    comptest = pins.v_comptest
    LED1_Pin = pins.v_LED1_Pin
    LED2_Pin = pins.v_LED2_Pin
    PUMP1_Pin = pins.v_PUMP1_Pin
    PUMP2_Pin = pins.v_PUMP2_Pin
    GPIO.setwarnings(False)
    GPIO.setup(LED1_Pin, GPIO.OUT)  # Set our input pin to be an input
    GPIO.setup(LED2_Pin, GPIO.OUT)  # Set our input pin to be an input
    GPIO.setup(PUMP1_Pin, GPIO.OUT)  # Set our input pin to be an input
    GPIO.setup(PUMP2_Pin, GPIO.OUT)  # Set our input pin to be an input
    GPIO.output(LED1_Pin, 1)
    GPIO.output(LED2_Pin, 1)
    GPIO.output(PUMP1_Pin, 1)
    GPIO.output(PUMP2_Pin, 1)
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)
    # Set each pin as an output and make it low:
    for lpin in lights:
        GPIO.setup(lpin, GPIO.OUT)
        GPIO.output(lpin, GPIO.LOW)
    for ppin in pumps:
        GPIO.setup(ppin, GPIO.OUT)
        GPIO.output(ppin, GPIO.LOW)


def getallimages(imgdirpath, imgvalid_extensions=('jpg', 'jpeg', 'png')):
    piclist = {}
    imgvalid_files = [os.path.join(imgdirpath, filename) for filename in os.listdir(imgdirpath)]
    imgvalid_files = [f for f in imgvalid_files if '.' in f and \
                      f.rsplit('.', 1)[-1] in imgvalid_extensions and os.path.isfile(f)]
    nr = 0
    for pic in imgvalid_files:
        picture = "/"+imgvalid_files[nr]
        piclist_pic = tuple(picture)
        piclist[nr] = {}
        piclist[nr]['pic'] = picture
        nr = nr + 1
    if not imgvalid_files:
        imgvalid_files=["static/gallery/nopic.png"]
    picarray= {'piclist': piclist}
    print(picarray)
    return picarray

# Stelle alle Verfügbaren Timelapse Bilder bereit
def get_latest_image(dirpath, valid_extensions=('jpg', 'jpeg', 'png')):
    """
    Get the latest image file in the given directory
    """

    # get filepaths of all files and dirs in the given dir
    valid_files = [os.path.join(dirpath, filename) for filename in os.listdir(dirpath)]
    # filter out directories, no-extension, and wrong extension files
    valid_files = [f for f in valid_files if '.' in f and \
                   f.rsplit('.', 1)[-1] in valid_extensions and os.path.isfile(f)]

    if not valid_files:
        valid_files=["static/gallery/nopic.png"]
    return max(valid_files, key=os.path.getmtime)


# Teste alle Komponenten durch
def komponententester():
    modulname = "Komponententester"
    comptest = komponententest

    if comptest == True:
        console(modulname, "Komponententest wird gestartet!")

        LED1_Pin = pins.v_LED1_Pin
        LED2_Pin = pins.v_LED2_Pin
        PUMP1_Pin = pins.v_PUMP1_Pin
        PUMP2_Pin = pins.v_PUMP2_Pin
        GPIO.output(LED1_Pin, 0)
        GPIO.output(LED2_Pin, 0)
        GPIO.output(PUMP1_Pin, 0)
        GPIO.output(PUMP2_Pin, 0)
        GPIO.setwarnings(False)
        console(modulname, "Relays werden getestet!")
        console(modulname, "Relay Test - Alle Relays an")
        GPIO.output(LED1_Pin, 1)
        console(modulname, "LED 1 - " + Fore.GREEN + "AN")
        time.sleep(1)
        GPIO.output(LED2_Pin, 1)
        console(modulname, "LED 2 - " + Fore.GREEN + "AN")
        time.sleep(1)
        GPIO.output(PUMP1_Pin, 1)
        console(modulname, "Pumpe 1 - " + Fore.GREEN + "AN")
        time.sleep(1)
        GPIO.output(PUMP2_Pin, 1)
        console(modulname, "Pumpe 2 - " + Fore.GREEN + "AN")
        time.sleep(1)
        GPIO.output(LED1_Pin, 0)
        console(modulname, "LED 1 - " + Fore.RED + "AUS")
        time.sleep(1)
        GPIO.output(LED2_Pin, 0)
        console(modulname, "LED 2 - " + Fore.RED + "AUS")
        time.sleep(1)
        GPIO.output(PUMP1_Pin, 0)
        console(modulname, "Pumpe 1 - " + Fore.RED + "AUS")
        time.sleep(1)
        GPIO.output(PUMP2_Pin, 0)
        console(modulname, "Pumpe 2 - " + Fore.RED + "AUS")
        time.sleep(1)
        console(modulname, "Relay Test OK!")
        time.sleep(1)
        pass


# Datenbanken
# Erstelle die Datenbank für die Sensordaten
def createsensordb():
    modulname = "Datenbank"
    db_file = "db/sensor.db"
    conn = sqlite3.connect(db_file)
    conn.execute('''CREATE TABLE daten
         (TYP           TEXT    NOT NULL,
         VALUE          TEXT     NOT NULL,
         DATE        TEXT,
         TIME        TEXT);''')
    conn.close()
    console(modulname, "Tabelle wurde erstellt")


# Sensordaten speichern in der Datenbank
def storeinsensordb(sensortyp, value, sensortyp2, value2):
    modulname = "Datenbank"
    db_file = "db/sensor.db"
    current_time = time.localtime()
    conn = sqlite3.connect(db_file)
    datum = time.strftime('%y-%m-%d', current_time)
    print (datum)
    zeit = str(time.strftime('%H:%M:%S', current_time))
    sql1 = '''INSERT INTO daten (TYP,VALUE,DATE,TIME)\
    VALUES ('{0}','{1}','{2}','{3}')'''
    sql2 = '''INSERT INTO daten (TYP,VALUE,DATE,TIME)\
    VALUES ('{0}','{1}','{2}','{3}')'''
    sql = sql1.format(str(sensortyp), value, datum, zeit)
    sql2 = sql1.format(str(sensortyp2), value2, datum, zeit)
    conn.execute(sql)
    conn.commit()
    conn.execute(sql2)
    conn.commit()
    console(modulname, "Datensatz gespeichert")
    conn.close()


# Senordaten auslesen aus der Datenbank
def getdbdata():
    sensor_data_list = {}
    datensatz_limit = 100
    now = datetime.now()  # current date and time
    year = now.strftime("%Y")

    month = now.strftime("%m")

    day = now.strftime("%d")

    zeit = now.strftime("%H:%M:%S")

    date_time = now.strftime("%Y-%m-%d")
    print(date_time)
    Datensatz = {}
    modulname = "Datenbank"
    conn = sqlite3.connect('db/sensor.db')
    console(modulname, "Datenbank wurde geöffnet")

    sql_string = 'SELECT * from daten  ORDER BY DATE DESC LIMIT {datensatz_limit}'.format(
        datum=date_time, datensatz_limit=datensatz_limit)
    print(sql_string)
    cursor = conn.execute(sql_string)
    records = cursor.fetchall()
    nr = 0
    for row in records:
        typ = row[0]
        value = row[1]
        datum = row[2]
        zeit = row[3]
        strdate = row[2]+ "" + row[3]
        print(strdate)
        dt_tuple = tuple([int(x) for x in strdate[:10].split('-')]) + tuple([int(x) for x in strdate[11:].split(':')])
        sensor_data_list[nr] = {}
        sensor_data_list[nr]['Type'] = typ
        sensor_data_list[nr]['VALUE'] = value
        sensor_data_list[nr]['DATE'] = dt_tuple
        sensor_data_list[nr]['TIME'] = row[3]
        nr = nr + 1
    console(modulname, "Datenbank Operation erfolgreich")
    conn.close()
    sensor_data_list

    sensorarray = {'sensor_daten': sensor_data_list}
    print(sensorarray)
    print(sensor_data_list)
    return sensorarray


# Sensordaten vom DHT11 Sensor auslesen und in Datenbank speichern
def getsensordata():
    modulname = "Sensor"
    if v_temp_sensor_typ == "DHT11":
        console(modulname, "Rufe Sensoren ab")
        sensor = Adafruit_DHT.DHT11
        pin = v_temp_sensor_pin
        humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
        console(modulname, "Gelesene Senorwerte")
        console(modulname, 'Temperatur: {0:0.1f}%'.format(temperature, humidity))
        console(modulname, 'Feuchtigkeit: {1:0.1f}%'.format(temperature, humidity))
        sensor_temp = '{0:0.1f}'.format(temperature, humidity)
        sensor_humitidy = '{1:0.1f}'.format(temperature, humidity)
        storeinsensordb("Temperatur", sensor_temp, "Feuchtigkeit", sensor_humitidy)

        sensor_data = {
            sensor_temp: {'name': 'Temperatur', 'value': sensor_temp},
            sensor_humitidy: {'name': 'Luftfeuchtigkeit', 'value': sensor_humitidy}
        }
        return humidity, temperature, sensor_humitidy, sensor_temp


# Sensordaten bereitstellen uns an Modul bereitstellen
def SensorData(sender):
    if sender == "web":
        humidity, temperature, sensor_humitidy, sensor_temp = getsensordata()
    if sender == "datareader":
        humidity, temperature, sensor_humitidy, sensor_temp = getsensordata()
    sensor_data1 = {
        sensor_temp: {'name': 'Temperatur', 'value': sensor_temp + "°C"},
        sensor_humitidy: {'name': 'Luftfeuchtigkeit', 'value': sensor_humitidy + "%"}
    }
    sensorarray = {'sensor_data1': sensor_data1}
    # print(sensorarray)
    return sensorarray


# Display Ausgabe
def display_txt(text, line):
    modulname = "Display"
    i = int(line) - 1
    Zeile[i] = text
    mylcd.lcd_clear()
    mylcd.lcd_display_string(Zeile[3], 4)
    mylcd.lcd_display_string(Zeile[2], 3)
    mylcd.lcd_display_string(Zeile[1], 2)
    mylcd.lcd_display_string(Zeile[0], 1)


# Suffix erstellen und formatieren
def suffix(log2):
    Suffix = Fore.BLUE + log2
    return Suffix


# Prefix erstellen und formatieren
def prefix(log):
    Prefix = Fore.GREEN + "[" + settings.prefix + "]" + "[" + settings.version + "]" + Fore.WHITE + "-" + Fore.LIGHTGREEN_EX + "[" + suffix(
        (log) + Fore.LIGHTGREEN_EX + "]")
    return Prefix


# Funktion für die Server-Log Datei
def consolelog(modul, text):
    current_time = time.localtime()
    zeit = str(time.strftime('%H:%M:%S', current_time))
    datei = open('log/server.log', 'a')
    datei.write(
        "\r[" + settings.prefix + "][" + modul + "][" + settings.version + "][" + zeit + "]"  ":" + text)


# Funktion für Ereignisausgabe in die Systemconsole
def console(modul: object, text: object) -> object:
    current_time = datetime.time
    Ausgabe = prefix(modul) + ":" + Fore.WHITE + text
    # Ausgabe in die Console
    print(Ausgabe)
    consolelog(modul, text)
    # Schreibe ins Log


# LCD Display Funktionen
def display(text, line):
    consolelog("Display", text)


# Filecheck function
def filecheck(file):
    path_to_file = file
    path = Path(path_to_file)
    if path.is_file():
        conn = sqlite3.connect(file)
        createsensordb()
        console(modulname, "Datenbank wurde gefunden")
    else:
        console(modulname, "Datenbank wurde nicht gefunden")
        conn = sqlite3.connect(file)
        createsensordb()

        console(modulname, "Datenbank wurde neu erstellt")


# Display UI Functions
def uibootscreen():
    Version = version.v_Version
    AppTitle = version.v_Application
    Desc = "Web-Dashboard:"
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    IP = "" + s.getsockname()[0] + ":7411"
    display_txt(AppTitle, 1)
    display_txt(Version, 2)
    display_txt(Desc, 3)
    display_txt(IP, 4)
    time.sleep(3)
    statusscreen()


# Zeige Statusscreen auf dem Display an
def statusscreen():
    humidity = ""
    temperature = ""
    AppTitle = version.v_Application
    Status = "Bereit"
    display_txt(AppTitle, 1)
    display_txt("Temperatur:" + str(temperature) + "°C", 2)
    display_txt("Humidity:" + str(humidity) + "%", 3)
    display_txt("Status:Bereit!", 4)
    console(modulname, "Bereit!")


# Übergebe Status und Events an Display und zeig den Statusscreen an
def processing(device, state):
    AppTitle = version.v_Application
    Status = "Schalte"
    display_txt(AppTitle, 1)
    display_txt("Status:" + device + "-" + state, 4)
    time.sleep(3)
    statusscreen()


def get_base64_encoded_image(image_path):
    with open(image_path, "rb") as img_file:
        print(base64.b64encode(img_file.read()).decode('utf-8'))
        return base64.b64encode(img_file.read()).decode('utf-8')
