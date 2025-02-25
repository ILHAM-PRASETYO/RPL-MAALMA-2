from machine import Pin, PWM
import ujson
import network
import utime as time
import dht
import urequests as requests

DEVICE_ID = "Sensor_RPL_MAALMA_2"
WIFI_SSID = "WIN-DPENVE1NVD9 6290"
WIFI_PASSWORD = "jandD23703"
TOKEN = "BBUS-K5EEFORpRXi1m0kizhkkcCSWqyPohD"

Buzzer = PWM(Pin(12))
DHT_PIN = Pin(15)
PIR_PIN = Pin(5)
pir_motion = Pin(PIR_PIN, Pin.IN)
jumlah_motion = 0

def did_receive_callback(topic, message):
    print('\n\nData Received! \ntopic = {0}, message = {1}'.format(topic, message))

def create_json_data(temperature, humidity, motion, jumlah_motion):
    data = ujson.dumps({
        "device_id": DEVICE_ID,
        "temp": temperature,
        "humidity": humidity,
        "motion": motion,
        "motion_per_record": jumlah_motion,
        "type": "sensor"
    })
    return ujson.dumps(data)

def send_data_ubidots(temperature, humidity, motion, jumlah_motion):
    ubidots_url = "http://industrial.api.ubidots.com/api/v1.6/devices/" + DEVICE_ID
    headers = {"Content-Type": "application/json", "X-Auth-Token": TOKEN}
    try :
        ubidots_data = {
            "temp": temperature,
            "humidity": humidity,
            "motion": motion,
            "motion_per_record": jumlah_motion
        }
        ubidots_response = requests.post(ubidots_url, json=ubidots_data, headers=headers,)
        print("Ubidots Kirim Data!")
        print("Ubidots Response :", ubidots_response.text)
        print("Data Masuk Ubidots")
    except OSError as e:
        print("Network Error:", e)
    except Exception as e:
        print("error ubidots :", e)
        
Flask_url = "http://192.168.0.133:6000/data"

def send_data_mongoDB(temperature, humidity, motion, jumlah_motion):
    url = "http://industrial.api.ubidots.com/api/v1.6/devices/" + DEVICE_ID
    headers = {"Content-Type": "application/json", "X-Auth-Token": TOKEN}
    try :
        Flask_data = {
            "temp": temperature,
            "humidity": humidity,
            "motion": motion,
            "motion_per_second": jumlah_motion
        }
        Flask_response = requests.post(Flask_url, json=Flask_data, headers=headers)
        print("mongoDB Kirim Data!")
        print("Flask Response :", Flask_response.text)
    except Exception as e:
        print("mongoDB error :", e)
        
wifi_client = network.WLAN(network.STA_IF)
wifi_client.active(True)
print("Connecting device to WiFi")
wifi_client.connect(WIFI_SSID, WIFI_PASSWORD)

while not wifi_client.isconnected():
    print("Connecting")
    time.sleep( 1)
print("WiFi Connected!")
print(wifi_client.ifconfig())

def suara_buzzer():
    global jumlah_motion

    motion_value = pir_motion.value()
    if motion_value == 1 :
        jumlah_motion += 1
        if jumlah_motion == 1:
            Buzzer.freq(100)
        elif jumlah_motion > 1 :
            Buzzer.freq(100 + (jumlah_motion * 200))
        Buzzer.duty(512)
    elif motion_value == 0 :
        jumlah_motion = 0
        Buzzer.duty(0)
    time.sleep(1)

dht_sensor = dht.DHT11(DHT_PIN)
telemetry_data_old = ""

while True:
    try:
        dht_sensor.measure()
        pir_motion.value()
        suara_buzzer()
        time.sleep(0)  # Tunggu sedikit sebelum membaca
    except (OSError, Exception) as e:
        if Exception :
            print(f"Error reading DHT sensor: {e}")
        else :
            print(f"Error reading PIR sensor: {e}")
            print(f"Error reading sensor: {e}")

    telemetry_data_new = create_json_data(dht_sensor.temperature(), dht_sensor.humidity(), pir_motion.value(), jumlah_motion)
    send_data_ubidots(dht_sensor.temperature(), dht_sensor.humidity(), pir_motion.value(), jumlah_motion)
    send_data_mongoDB(dht_sensor.temperature(), dht_sensor.humidity(), pir_motion.value(), jumlah_motion)

    time.sleep(0.1)
