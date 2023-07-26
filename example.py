from uwebserver import UWebServer
import network
from time import sleep
from picozero import pico_led
import ujson
import _thread

web_server = UWebServer(port=80, static_dir='static')

@web_server.route("/api/led", "POST")
def api_led_control(data):
    state = ujson.loads(data)

    if 'led' in state:
        if state["led"] == 1:
            pico_led.on()
        elif state["led"] == 0:
            pico_led.off()

        return ujson.dumps({"message": f"LED set to {state['led']}"}), "application/json", "200 OK"
    else:
        return ujson.dumps({"message": "No LED state in data"}), "application/json", "200 OK"

if __name__ == "__main__":
    ssid = "Your wifi"
    password = "password"

    # If you want to connect to existing WiFi
    ap = network.WLAN(network.STA_IF)
    ap.active(True)
    ap.connect(ssid, password)

    # If you want to create Access Point with specified ssid and password
    # ap = network.WLAN(network.AP_IF)
    # ap.config(essid=ssid, password=password)
    # ap.active(True)

    while ap.isconnected() == False:
        print('Waiting for connection...')
        sleep(1)

    print('Connection is successful')
    print(ap.ifconfig())

    web_server.start()
