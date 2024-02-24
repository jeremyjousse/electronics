import network
import socket
import secrets
from time import sleep
from machine import Pin, reset


led = Pin("LED", Pin.OUT)

htmlresponse = """HTTP/1.0 200 OK
Content-Type: text/html

<!DOCTYPE html>
<meta charset="UTF-8">
<html>
    <head>
        <title>Serveur RaspiPicoW</title>
    </head>
    <body>
        <p>Etat de la LED : {} </p>
        <p> <a href = "/?etat=on" >Led ON </a>  </p>
        <p> <a href = "/?etat=off" >Led OFF </a> </p>
        <p> <a href = "/?etat=toggle" >TOGGLE </a> </p>
    </body>
</html>
"""

def wifi_connect():
    led.off()
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    sleep_time = 0
    while wlan.isconnected() == False:
        sleep_time+=1
        print('attend la connexion : ', sleep_time)
        sleep(1)
    print('la connection est:')
    print(wlan.ifconfig())
    led.on()
    return wlan.ifconfig()[0]

try:
    ip_address = wifi_connect()
    print("connectez vous sur: ", ip_address)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((ip_address, 8080))
    s.listen(1)
    while True :
        print("Attente connexion ...")
        connexion = s.accept()
        client_address = connexion[1]
        client_socket = connexion[0]
        print("Adresse client connecté :",client_address[0])
        request = client_socket.recv(2048).decode('utf-8').split(' ')
        if request[0] == 'GET' :
            url = request[1]
            if url[0:7] == "/?etat=":
                if url[7:] == 'on':
                    led.on()
                elif url[7:] == 'off':
                    led.off()
                elif url[7:] == 'toggle':
                    led.toggle()
            client_socket.send(htmlresponse.format(led.value()))
        client_socket.close()
except KeyboardInterrupt:
    reset()