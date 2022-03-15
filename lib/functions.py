# coding=utf-8
import datetime
import socket
import sqlite3
import time
from pathlib import Path
import RPi.GPIO as GPIO
import Adafruit_DHT
from colorama import Fore

import driver_lcd
from lib import settings, version, pins
from lib.pins import v_temp_sensor_typ, v_temp_sensor_pin, v_LED1_Pin, v_LED2_Pin, v_PUMP1_Pin, v_PUMP2_Pin
from lib.settings import komponententest

modulname = "Funktionen"
# Display Buffer
Zeile = ["Smart Planter", "Temperatur", "Feuchtigkeit", "Webserver :"]
mylcd = driver_lcd.lcd()

lights = {
        v_LED1_Pin: {'name': 'LED Links', 'state': GPIO.LOW},
        v_LED2_Pin: {'name': 'LED Rechts', 'state': GPIO.LOW}
    }
pumps = {
        v_PUMP1_Pin: {'name': 'Pumpe Links', 'state': GPIO.LOW},
        v_PUMP2_Pin: {'name': 'Pumpe Rechts', 'state': GPIO.LOW}
    }
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
        console(modulname,"Relays werden getestet!")
        console(modulname,"Relay Test - Alle Relays an")
        GPIO.output(LED1_Pin, 1)
        console(modulname,"LED 1 - " + Fore.GREEN + "AN")
        time.sleep(1)
        GPIO.output(LED2_Pin, 1)
        console(modulname,"LED 2 - " + Fore.GREEN + "AN")
        time.sleep(1)
        GPIO.output(PUMP1_Pin, 1)
        console(modulname,"Pumpe 1 - " + Fore.GREEN + "AN")
        time.sleep(1)
        GPIO.output(PUMP2_Pin, 1)
        console(modulname,"Pumpe 2 - " + Fore.GREEN + "AN")
        time.sleep(1)
        GPIO.output(LED1_Pin, 0)
        console(modulname,"LED 1 - " + Fore.RED + "AUS")
        time.sleep(1)
        GPIO.output(LED2_Pin, 0)
        console(modulname, "LED 2 - " + Fore.RED + "AUS")
        time.sleep(1)
        GPIO.output(PUMP1_Pin, 0)
        console(modulname,"Pumpe 1 - " + Fore.RED + "AUS")
        time.sleep(1)
        GPIO.output(PUMP2_Pin, 0)
        console(modulname,"Pumpe 2 - " + Fore.RED + "AUS")
        time.sleep(1)
        console(modulname,"Relay Test OK!")
        time.sleep(1)
        pass

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


def storeinsensordb(sensortyp, value,sensortyp2,value2):
    modulname = "Datenbank"
    db_file = "db/sensor.db"

    current_time = time.localtime()
    conn = sqlite3.connect(db_file)
    datum = str(datetime.date.today())
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


def getdbdata(sensortype):
    sensor_data_list = {}
    Datensatz={}
    modulname = "Datenbank"
    conn = sqlite3.connect('db/sensor.db')
    console(modulname, "Datenbank wurde geöffnet")
    cursor = conn.execute("SELECT * from daten ")
    records = cursor.fetchall()
    nr = 0
    for row in records:
        typ=row[0]
        value=row[1]
        datum=row[2]
        from datetime import datetime
        zeit=row[3]
        strdate = row[2]+" "+row[3]
        dt_tuple = tuple([int(x) for x in strdate[:10].split('-')]) + tuple([int(x) for x in strdate[11:].split(':')])
        sensor_data_list[nr] = {}
        sensor_data_list[nr]['Type'] = typ
        sensor_data_list[nr]['VALUE'] =value
        sensor_data_list[nr]['DATE'] = dt_tuple

        nr = nr+1

    console(modulname, "Datenbank Operation erfolgreich")
    conn.close()
    sensor_data_list
    sensorarray = {'sensor_daten': sensor_data_list}
    return sensorarray



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
        storeinsensordb("Temperatur", sensor_temp,"Feuchtigkeit", sensor_humitidy)

        sensor_data = {
            sensor_temp: {'name': 'Temperatur', 'value': sensor_temp},
            sensor_humitidy: {'name': 'Luftfeuchtigkeit', 'value': sensor_humitidy}
        }
        return humidity, temperature,  sensor_humitidy, sensor_temp


def SensorData(sender):
    if sender =="web":
        humidity, temperature,  sensor_humitidy, sensor_temp = getsensordata()
    if sender =="datareader":
        humidity, temperature,  sensor_humitidy, sensor_temp = getsensordata()
    sensor_data1 = {
        sensor_temp: {'name': 'Temperatur', 'value': sensor_temp + "°C"},
        sensor_humitidy: {'name': 'Luftfeuchtigkeit', 'value': sensor_humitidy + "%"}
    }
    sensorarray = {'sensor_data1': sensor_data1}
    # print(sensorarray)
    return sensorarray


def display_txt(text, line):
    modulname = "Display"
    i = int(line) - 1
    Zeile[i] = text
    mylcd.lcd_clear()
    mylcd.lcd_display_string(Zeile[3], 4)
    mylcd.lcd_display_string(Zeile[2], 3)
    mylcd.lcd_display_string(Zeile[1], 2)
    mylcd.lcd_display_string(Zeile[0], 1)


def suffix(log2):
    Suffix = Fore.BLUE + log2
    return Suffix


# Prefix Funktion
def prefix(log):
    Prefix = Fore.GREEN + "[" + settings.prefix + "]" + "[" + settings.version + "]" + Fore.WHITE + "-" + Fore.LIGHTGREEN_EX + "[" + suffix(
        (log) + Fore.LIGHTGREEN_EX + "]")
    return Prefix


def consolelog(modul, text):
    current_time = time.localtime()
    zeit = str(time.strftime('%H:%M:%S', current_time))
    datei = open('log/server.log', 'a')
    datei.write(
        "\r[" + settings.prefix + "][" + modul + "][" + settings.version + "][" + zeit + "]"  ":" + text)


# Syslog Funktion
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


def filecheck(file):
    path_to_file = file
    path = Path(path_to_file)

    if path.is_file():
        conn = sqlite3.connect(file)
        createsensordb()
        #console(modulname, "Datenbank wurde gefunden")
    else:
        #console(modulname, "Datenbank wurde nicht gefunden")
        conn = sqlite3.connect(file)
        createsensordb()

        #console(modulname, "Datenbank wurde neu erstellt")


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

def statusscreen():
    humidity =""
    temperature = ""
    AppTitle = version.v_Application
    Status = "Bereit"
    display_txt(AppTitle, 1)
    display_txt("Temperatur:"+str(temperature)+"°C", 2)
    display_txt("Humidity:"+str(humidity)+"%", 3)
    display_txt("Status:Bereit!", 4)
    console(modulname, "Bereit!")

def processing(device, state):

    AppTitle = version.v_Application
    Status = "Schalte"
    display_txt(AppTitle, 1)
    display_txt("Status:"+device+"-"+state, 4)
    time.sleep(3)
    statusscreen()