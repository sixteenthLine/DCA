import websocket
import json
import threading
import tools
import time
from telethon.tl.types import MessageEntityBold
from telethon.tl.custom import Button

websocket_url = "wss://wbs.mexc.com/ws"

class WebSocketClient:
    def __init__(self, message, amount, sholder, order_id, my_id, signal_id):
        self.symbol = tools.Tools.getSymbol(message).upper()
        self.ws = None
        self.thread = None
        self.running = False 
        self.call = message
        self.sholder = sholder
        self.amount = amount
        self.valid_tocken = True
        self.order_id = order_id
        self.my_id = my_id
        self.signal_id = signal_id
        self.time = time.time()
        self.data = None

        self.direction = tools.Tools.getDirection(message)
        self.last = None
        self.first = None
        self.max = None
        self.stop_loss = None
        self.profit = None

    def on_message(self, ws, message):
            data = json.loads(message)
            self.data = data
            self.check_status()
            if not self.first and "id" not in data:
                self.first = float(data['d']['deals'][0]['p'])
                print("Первые данные получены")

            if "id" not in data and self.running:
                self.last = float(data['d']['deals'][0]['p'])
                self.update_max_and_move_stoplose()
            return data
    
    def check_status(self):
        if ("msg" in self.data and self.data["msg"][0:3] == 'Not') or (not self.first and self.time - time.time()>20):
            self.valid_tocken = False
            self.disconnect()
            return True
        return False
    
    def update_max_and_move_stoplose(self):
        if not self.max: 
            self.max =  self.last
            if (self.direction):
                self.stop_loss = self.first*1.01
            else:
                self.stop_loss = self.first*0.99
            return
        
        if (self.direction):
            if self.max > self.last:
                self.max  =  self.last
                if self.get_current_profit() > (self.sholder*self.amount)/100:
                    self.stop_loss = self.first - (self.first-self.max)*0.7 #CТОП ЛОС СОСТАВЛЕТ 70% ОТ МАКСИМАЛЬНОЙ ПИБЫЛИ
            if self.stop_loss <= self.last:
                self.disconnect()

        else:
            if self.max < self.last:
                self.max  =  self.last
                if self.get_current_profit() > (self.sholder*self.amount)/100:
                    self.stop_loss = self.max - (self.max-self.first)*0.3
            
            if self.stop_loss >= self.last:
                self.disconnect()
        

    def get_current_profit(self):

        if (self.direction):
            return (self.first/self.last-1)*(self.sholder*self.amount) - self.sholder*self.amount*0.0002
        else:
             return (self.last/self.first-1)*(self.sholder*self.amount) - self.sholder*self.amount*0.0002
        


    def on_error(self, ws, error):
        print(f"Ошибка для {self.symbol}: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        print(f"Соединение закрыто для {self.symbol}")

    def on_open(self, ws):
        print(f"Соединение открыто для {self.symbol}")
        subscribe_message = {
            "method": "SUBSCRIPTION",
            "params": [
                f"spot@public.deals.v3.api@{self.symbol}USDT"
            ],
            "id": 1
        }
        print( f"spot@public.deals.v3.api@{self.symbol}")
        ws.send(json.dumps(subscribe_message))

    def connect(self):
        if self.running:
            print(f"Соединение уже активно для {self.symbol}")
            return

        self.running = True
        self.ws = websocket.WebSocketApp(
            websocket_url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        self.thread = threading.Thread(target=self.ws.run_forever, daemon=True)
        self.thread.start()
        print(f"Подключение установлено для {self.symbol}")

    def disconnect(self):
        if not self.first:
            self.running = False
            if self.ws:
                self.ws.close()
            if self.thread:
                self.thread.join()
            return

        self.profit = self.get_current_profit() - self.amount*self.sholder*0.0002

        self.running = False
        if self.ws:
            self.ws.close()
        if self.thread:
            self.thread.join()
        print(f"Подключение закрыто для {self.symbol}")

def start_connection(message, amount, sholder, order_id, my_id, signal_id):
    client = WebSocketClient(message, amount, sholder, order_id, my_id, signal_id)
    print("Новый объект веб сокета успешно создан")
    client.connect()
    print("Клиент подключен")
    return client

def stop_connection(client):
    client.disconnect()

