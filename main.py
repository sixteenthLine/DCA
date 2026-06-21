import nest_asyncio
import asyncio
from telethon import TelegramClient
from telethon import events
import tools
import price_monitoring
import re
import aiosqlite


nest_asyncio.apply()
order_id = 0
memory = {}
API_ID = ''
API_HASH = ''
sender = -1002306843892


async def create_table():
    async with aiosqlite.connect('bot_stats.db') as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS users (
                                user_id INTEGER PRIMARY KEY,
                                sum INTEGER,
                                time INTEGER,
                                price_change FLOAT,
                                frequency INTEGER,
                                simulate INTEGER,
                                amount FLOAT,
                                sholder INTEGER,
                                total FLOAT
                            )''')
        await db.execute('''CREATE TABLE IF NOT EXISTS data (
                        message TEXT,
                        first FLOAT,
                        max FLOAT,
                        last FLOAT,
                        direction INTEGER,
                        profit FLOAT
                    )''')
        await db.commit()

client = TelegramClient('main', API_ID, API_HASH)

@client.on(events.NewMessage(incoming=True))
async def handle_new_message(event):
    if await admin_message(event):
        return
    if event.sender_id == sender:
        await check_new_signal(event)  
        return
    await user_interaction(event)
    return 

async def admin_message(event):
    if event.text.strip() == "!copy" and event.sender_id == 818906207:
        try:
            await client.send_file(event.sender_id, 'bot_stats.db', caption="Резервная копия базы данных.")
            await client.send_message(event.sender_id, "База данных успешно отправлена.")
        except Exception as e:
            await client.send_message(event.sender_id, f"Ошибка при отправке базы данных: {str(e)}")
        return True

    if event.text.strip() == "!reset" and event.sender_id == 818906207:
        for key in memory.keys():
            memory[key] = []
        await client.send_message(818906207, "Память было очищена")
        return True

    if event.text[0] == "!" and event.sender_id == 818906207:            
        async with aiosqlite.connect('bot_stats.db') as db:
            async with db.execute("SELECT * FROM users") as cursor:
                rows = await cursor.fetchall() 
                for row in rows:
                    await client.send_message(row[0], event.text[1:])
        return True
    return False

async def process_filters(params):
    try:
        params[0] = int(params[0])
    except:
        return "Похоже вы ввели первое значение неправильно. Это должно быть целое число"
    
    try:
        params[1] = int(params[1])
    except:
        return "Похоже вы ввели второе значение неправильно. Это должно быть целое число"
    try:
        params[2] = float(params[2])
    except:
        return "Похоже вы ввели третье значение неправильно. Это должно быть целое или дробное число написаное через '.'"
    

    try:
        params[3] = int(params[3])
    except:
        return "Похоже вы ввели четвертое значение неправильно. Это должно быть целое число" 
    
    try:
        params[4] = int(params[4])
    except:
        return "Похоже вы ввели четвертое значение неправильно. Это должно быть целое число" 
    try:
        params[5] = int(params[5])
    except:
        return "Похоже вы ввели пятое значение неправильно. Это должно быть целое число"
    
    try:
        params[6] = int(params[6])
    except:
        return "Похоже вы ввели шестое значение неправильно. Это должно быть целое число"
    
    return False
    
    

async def check_new_signal(event):
    if event.message.reply_to_msg_id:
        await handle_reply(event)
        return
    async with aiosqlite.connect('bot_stats.db') as db:
        async with db.execute("SELECT * FROM users") as cursor:
            rows = await cursor.fetchall()  
            msg = await constract_signal_message(remove_formatting(event.text))
            for row in rows: 
                if tools.Tools.isValidMessage(remove_formatting(event.text), row[1], row[2], row[3], row[4]):
                    msg = await client.send_message(row[0], msg)
                    if row[5]:
                        if tools.Tools.has_mexc(remove_formatting(event.text)):
                            await add_to_memmory(row[0], remove_formatting(event.text), msg.id, event.message.id)  
                        else: 
                            await client.send_message(row[0], "Внимание данного токена на на MEXC FUTURES!!!")


async def user_interaction(event):
    if len(event.text)> 2 and  event.text[:2] == "-a":
        params = event.text.split(" ")[1:]
        params.append(str(event.sender_id))
        if len(params) == 8 : #проверить что все значения int
            if await process_filters(params):
                await client.send_message(event.sender_id, await process_filters(params))
                return True
            await update_settings(params)
            await client.send_message(event.sender_id, "Ваши настройки были успешно обновлены")
        else:
             await client.send_message(event.sender_id, "Неправильный формат данных!")
        return True
    
    if event.text == "-c":
        msg = await print_user_account(event.sender_id)
        await client.send_message(event.sender_id, msg)
        return True
    
    if event.text == "-h":
        await client.send_message(event.sender_id, """
-h - Список всех команд
                                                  
-a - Поменять фильтры\установть фильтры
                                  
ВНИМАНИЕ УКАЖИТЕ ВСЕ ФИЛЬТРЫ ОДНОЙ СТРОЧКА ЧЕРЕЗ ПРОБЕЛ В ФОРМАТЕ: 
                                  
(Минимальная цена ордеров что вас интересует в тысячах)
(Максимально время ордера в минутах)
(Минимальное потенциальное изминение цены в %) 
(Минимальный Frequency на 60 секунд)
(Xотите ли вы симулировать открытие сделки? 0-нет 1-да)
(Сума на которую вы бы хотели симулировать открытие сделки)
(Плечо под которое вы бы открывали позицию)
                    
Пример правильного запроса:
-a 300 90 5 3500 1 100 20
(Всего вы должны передать боту 7 значений) 

-c Данные моего аккаунта (Фильтры/Прибыль)                                  

-q - Мониторинг открытых ордеров
ВНИМАНИЕ: Хотя закрытие ордера при симуляции происходит автоматически вы не получаете никаких уведомлений об этом. Для того чтобы узнать закрылся ли ваш ордер используйте команду -q. Состояние ордера будет указано первой строчкой.
                                  
-rm - Моментально закрыть сделку. Введите -rm и через пробел id сделки(Указан вверху сообщения используйте -q чтобы узнать)
                    
-f - FAQ
                """)
        return True

    if event.text  == "-q":
        if event.sender_id in memory:
            for message in await print_orders(event.sender_id):
                await client.send_message(event.sender_id, message)
        else:
            await client.send_message(event.sender_id, f"Пока нет открытых сделок")
        return True

    if event.text  == "-f":
        msg = """
1 - Насколько быстро и точно работает симуляция открытия бота? 

Получения сигнала до момента открытия симуляции и получения данных проходит в среднем менее секунды, а в худших сценариях около 15 секунд. В любом из случаев время задержки невероятно мало. Что делает их очень точными.

2 - Как работает симуляция stop loss и take profit?

При открытии сделки stop loss сработает на изменение цены монеты на 1% в направлении противоположном направлению открытия, и при достижении профита в 1% перенесет ST на 0.7% и при обновлении максимальноой прибыли будет двигать его вверх. TP в боте отсутствует

3 - Мне не нужны все фильтры могу ли я их не устанавливать?

Пока что нет вам придется написать все значения. Просто поставьте очень большие или очень маленькие значения.

4 - По каким монетам бот мониторит сигналы?

Только по монетам что есть на бирже MEXC

Внимание бот собирает всю историю всех ордеров с вашими id и результатами. Это делаетя чтобы иметь возможность собрать подробную статистику по лучшей торговой стратегии и фильтрам.
                """
        
                
        await client.send_message(event.sender_id, msg)
        return True
    if event.text[0:3] == "-rm":
        try : 
            id = int(event.text.split(" ")[1])
            await client.send_message(event.sender_id, await remove_order(event.sender_id, id))  
        except:
            await client.send_message(event.sender_id, "Похоже вы неправильно ввели id")
        return True

    await client.send_message(event.sender_id, "Команда не распознана. Введите -h для списка всех команд")  
    return False


async def print_user_account(id):
     async with aiosqlite.connect('bot_stats.db') as db:
            async with db.execute('''
                SELECT sum, time, price_change, frequency, simulate, amount, sholder, total FROM users WHERE user_id = ?''', (id,)) as cursor:
                result = await cursor.fetchone()
                if result:
                    msg = "Minimum target amount - " + str(result[0])
                    msg += "\nTime limit - " + str(result[1])
                    msg += "\nMinimum price change - " + str(result[2])
                    msg += "\nFrequency - " + str(result[3])
                    msg += "\nSimulate - " + str(result[4])
                    msg+= "\nSimulating orger amount - " + str(result[5])
                    msg += "\nSholder - " + str(result[6])
                    msg += "\nTotal profit - " + str(result[7]) + "$"
                else:
                    msg = "У вас нет никаких фильтров используйте -a чтобы создать их"
                return msg
            
async def constract_signal_message(event_message):\

    try:
        message = event_message.split("GMT")[0] +"GMT"+event_message.split("GMT")[1]+ "GMT"
        if "Promo" in event_message:
            message = event_message.split("Promo")[0] + "Amount:"+ event_message.split("Promo")[1].split("Amount:")[1].split("GMT")[0] + "GMT" +event_message.split("GMT")[1]+ "GMT"
        else :
            message = event_message.split("GMT")[0] + "GMT" +event_message.split("GMT")[1]+ "GMT"
        return message
    except:
        return event_message
async def get_sholder_and_amount(id):
     async with aiosqlite.connect('bot_stats.db') as db:
            async with db.execute('''
                SELECT amount, sholder FROM users WHERE user_id = ?''', (id,)) as cursor:
                result = await cursor.fetchone()
                return result

async def update_settings(params):
    async with aiosqlite.connect('bot_stats.db') as db:
            async with db.execute('''
                SELECT sum FROM users WHERE user_id = ?''', (int(params[7]),)) as cursor:
                result = await cursor.fetchone()

            if not result:
                await db.execute('''
                    INSERT INTO users (user_id, sum, time, price_change, frequency, simulate, amount, sholder, total)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', 
                        (int(params[7]), int(params[0]),int(params[1]),float(params[2]),int(params[3]),float(params[4]), int(params[5]), int(params[6]), 0))
                await db.commit()
            else:
                await db.execute(f'''
                    UPDATE users
                    SET sum = ?, time = ?, price_change = ?, frequency = ?,  simulate = ?, amount = ?, sholder = ?
                    WHERE user_id = ?;''', 
                        (int(params[0]),int(params[1]),float(params[2]),int(params[3]),float(params[4]), int(params[5]), int(params[6]), int(params[7])))
                await db.commit()

async def add_to_total(id, profit):
    async with aiosqlite.connect('bot_stats.db') as db:
            async with db.execute('''
                SELECT total FROM users WHERE user_id = ?''', (id,)) as cursor:
                result = await cursor.fetchone()
                res = result[0] + profit
                await db.execute(f'''
                    UPDATE users
                    SET total = ?
                    WHERE user_id = ?;''', 
                        (res,id))
                await db.commit()

async def handle_reply(event):
    for key in memory.keys():
        for socket in memory[key]:
            if socket.signal_id == event.message.reply_to_msg_id:
                await client.send_message(key, "Ордер был закрыт", reply_to=socket.my_id)
                socket.disconnect()


async def print_orders(id):
    orders = [f"На данный момент открыто {len(memory[id])} сделок"]
    for socket in memory[id]:   
        message = ""
        message += f"{socket.symbol}  ID: {socket.order_id}\n"
        if socket.check_status():
            message += "Похоже симуляция не может быть запущена по данному токену"
            orders.append(message)
            memory[id].remove(socket)
            continue
        if not socket.first :  
            message += "Подождите пару секунд ордер на этот токен не успел открыться"
            orders.append(message)
            continue
        if socket.profit:
            message += "Сделка закрыта\n"
            message += f"Прибыль - {socket.profit:.2f}$\n"
            memory[id].remove(socket)
            await add_to_total(id, round(socket.profit, 2))
            async with aiosqlite.connect('bot_stats.db') as db:
                await db.execute('INSERT INTO data (message, first, max, last, direction, profit) VALUES (?, ?, ?, ?, ?, ?)', (socket.call, socket.first, socket.max, socket.last, socket.direction, socket.profit))
                await db.commit()
        else:
            if socket.direction:
                message += "Selling\n"
            else :
                message += "Buying\n"
            message += f"Текущая цена - {socket.last}\n"
            message += f"Teкущая прибыль - {socket.get_current_profit():.2f}$\n"
            message += f"Цена Открытия - {socket.first}\n"
            message += f"Stop loss - {socket.stop_loss:.7f}\n"

        orders.append(message)
    return orders
        

async def add_to_memmory(id, message, my_id, signal_id):
    global order_id
    order_id +=1
    amount, sholder = await get_sholder_and_amount(id)
    ws = price_monitoring.start_connection(message, amount, sholder, order_id, my_id, signal_id)
    if id not in memory:
        memory[id] = []
    memory[id].append(ws)


async def remove_order(user_id, id):
    if user_id not in memory:
        return "У вас нет открытых ордеров"
    else:
        for socket in memory[user_id]:
            if socket.order_id == id:
                socket.disconnect()
                return "Сделка была успешно закрыта"
    return "Ордера с таким ID не найдено"

def remove_formatting(text):
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  
    text = re.sub(r'__(.*?)__', r'\1', text)      
    text = re.sub(r'\*(.*?)\*', r'\1', text)     
    text = re.sub(r'_(.*?)_', r'\1', text)        
    text = re.sub(r'~~(.*?)~~', r'\1', text)     
    text = re.sub(r'`(.*?)`', r'\1', text)       
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)  

    text = re.sub(r'<.*?>', '', text)  

    return text

    
async def main():
    await create_table()
    await client.start()  
    print("Бот запущен и ждет новые сообщения...")
    await client.run_until_disconnected()  

asyncio.run(main())
