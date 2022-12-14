#!/usr/bin/python3
import socket, threading
from wakeonlan import send_magic_packet
import yaml
import sys
import logging
import requests



# Блок функций исполняющих действия

def startpc():
    send_magic_packet(mac)

def startrozetka(vibor):
    try:
        with open(srcyaml, "r") as fh:
            configs = yaml.safe_load(fh)
        passwdeltex = configs["passwdeltex"]
        usereltex = configs["usereltex"]
        srcyaml.close()
    except:
        logging.error("Проблема с конфигом!")
    auth = 'https://eltexhome.ru/api/v1/oauth2/token'
    url = "https://eltexhome.ru/api/v1/ctl/a144a1d2-e4c8-4bfa-9fea-c2f11f247a50/devices/ddc00248-2281-46c8-8eb6-2daa35959942/props/00250000_0"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:106.0) Gecko/20100101 Firefox/106.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Authorization": "Basic d2ViLWNsaWVudDpwYXNzd29yZA==",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin"
    }
    usereltex = usereltex.replace('@','%40')
    data = str("username="+usereltex+"&password="+passwdeltex+"&grant_type=password")
    session = requests.Session()
    reqauth = session.post(auth, data=data, headers=headers)
    result = eval(reqauth.text)
    bearer = result["access_token"]
    var = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:106.0) Gecko/20100101 Firefox/106.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Authorization": "Bearer " + bearer,
        "Content-Type": "application/json",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin"
    }
    if vibor:
        vibor = "{\"value\":\"true\"}"
    elif vibor == False:
        vibor = "{\"value\":\"false\"}"
    req = session.post(url, headers=var, data=vibor)
    session.close()


def getwether():
    try:
        with open(srcyaml, "r") as fh:
            configs = yaml.safe_load(fh)
        appid = configs['appid']
        srcyaml.close()
    except:
        logging.error("Проблема с конфигом!")
    try:
        s_city_name = "Vladivostok"
        wet1 = ("Город: " + s_city_name)
        res = requests.get("http://api.openweathermap.org/data/2.5/weather",
                           params={'q': s_city_name, 'units': 'metric', 'lang': 'ru', 'APPID': appid})
        data = res.json()
        wet2 = ("Погода: " + data['weather'][0]['description'])
        wet3 = ("Темп: " + str(data['main']['temp']))
        wet4 = ("Мин: " + str(data['main']['temp_min']))
        wet5 = ("Макс: " + str(data['main']['temp_max']))

        wet = [wet1, wet2, wet3, wet4, wet5]
        return wet
    except Exception as e:
        print("Exception (weather):", e)
        pass

# Жизненый цикл подключения
class ClientThread(threading.Thread):
    def __init__(self, clientAddress, clientsocket):
        threading.Thread.__init__(self)
        self.csocket = clientsocket
        logging.info("Новое подключение: ", clientAddress)

    def run(self):
        logging.info("Подключение с клиента : ", clientAddress)
        self.csocket.send(bytes('Добро пожаловать на сервер romanhand.ru', 'UTF-8'))
        msg = ''
        while True:
            data = self.csocket.recv(4096)
            msg = data.decode()
            logging.info(msg)

            if msg == '':
                logging.info("Отключение")
                break

            elif msg == 'startpc':
                self.csocket.send(bytes('Магический пакет отправлен!', 'UTF-8'))
                startpc()

            elif msg == 'startrozetka on':
                self.csocket.send(bytes('Розетка включена!', 'UTF-8'))
                startrozetka(vibor=True)
            elif msg == 'startrozetka off':
                self.csocket.send(bytes('Розетка выключена!', 'UTF-8'))
                startrozetka(vibor=False)

            elif msg == 'getwether':
                wether = getwether()
                #print(wether)
                wether_result = str(wether[0] + "\n" + wether[1] + "\n" + wether[2] + "\n" + wether[3] + "\n" + wether[4])
                self.csocket.send(bytes(str(wether_result), 'UTF-8'))
                print(getwether())

            else:
                self.csocket.send(bytes('Команда не найдена:(', 'UTF-8'))

            logging.info("Запрос " + str(msg) + " обработан")

        logging.info("Клиент ", clientAddress, " покинул нас...")

def debugArg():
    try:
        debug = (sys.argv[1])
        if len(sys.argv) > 1:
            if debug == "-d" or debug == "--debug":
                debug = True
        else: debug = False
    except: debug = False
    return debug


if __name__ == "__main__":



    # Проверка на аргумент -d --debug для сбора доп логов
    debug = debugArg()


    # Обьявляем логи
    if debug:srclog = "rcs.log"
    else: srclog = "rcs.log"

    logging.basicConfig(filename="rcs.log")


    # Читаем конфиг
    if debug: srcyaml = 'remotecontrol.yaml'
    else: srcyaml = 'remotecontrol.yaml'


    # Назначение переменных из конфига
    try:
        with open(srcyaml, "r") as fh:
            configs = yaml.safe_load(fh)
        PORT = configs['port']
        USERNAME = configs['username']
        mac = configs['mac']
        api_yandex = configs['api_yandex']
        appid = configs['appid']
        passwdeltex = configs["passwdeltex"]
        usereltex = configs["usereltex"]
        srcyaml.close()
    except: logging.error("Проблема с конфигом!")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("", PORT))

    print("Сервер запущен, " + USERNAME + "!")

    while True:
        server.listen(1)
        clientsock, clientAddress = server.accept()
        newthread = ClientThread(clientAddress, clientsock)
        newthread.start()

