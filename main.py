import nest_asyncio
import asyncio
from telethon import TelegramClient
from telethon import events
import tools
import price_monitoring
import re
import aiosqlite


nest_asyncio.apply()
memory = {}
API_ID = '27805165'
API_HASH = '18cc81d866b21840ea43a04965c6665e'
sender = -1002306843892 #818906207 


async def create_table():
    async with aiosqlite.connect('bot_stats.db') as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS users (
                                user_id INTEGER PRIMARY KEY,
                                sum INTEGER,
                                time INTEGER,
                                price_change FLOAT,
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
    if event.is_private:
        await user_interaction(event)
        return 
    if event.sender_id == sender:
        await check_new_signal(event)  

async def admin_message(event):
    if event.text[0] == "!" and event.sender_id == 818906207:            
        async with aiosqlite.connect('bot_stats.db') as db:
            async with db.execute("SELECT * FROM users") as cursor:
                rows = await cursor.fetchall() 
                for row in rows:
                    await client.send_message(row[0], event.text[1:])
        return True
    return False


async def check_new_signal(event):
    async with aiosqlite.connect('bot_stats.db') as db:
        async with db.execute("SELECT * FROM users") as cursor:
            rows = await cursor.fetchall()  
            
            for row in rows: 
                if tools.Tools.isValidMessage(remove_formatting(event.text), row[1], row[2], row[3]):
                    await event.forward_to(row[0])
                    if row[4]:
                        #if Tools.has_mexc(message):
                            await add_to_memmory(row[0], remove_formatting(event.text))  
                        #else: 
                        # await client.send_message(event.sender_id, "невозможно запустить симуляцию. Кажется этого токена нет на MEXC")


async def user_interaction(event):
    
    if len(event.text)> 2 and  event.text[:2] == "-a":
        params = event.text.split(" ")[1:]
        params.append(str(event.sender_id))
        if len(params) == 7 : #проверить что все значения int
            await update_settings(params)
            await client.send_message(event.sender_id, "Ваши настройки были успешно обновлены")
        else:
             await client.send_message(event.sender_id, "Неправилььный формат данных!")
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
(Xотите ли вы симулировать открытие сделки? 0-нет 1-да)
(Сума на которую вы бы хотели симулировать открытие сделки)
(Плечо под которое вы бы открывали позицию)
                    
Пример правильного запроса:
-a 300 90 5 1 100 20
(Всего вы должны передать боту 6 значений) 

-c Данные моего аккаунта (Фильтры/Прибыль)                                  

-q - Мониторинг открытых ордеров
ВНИМАНИЕ: Хотя закрытие ордера при симуляции происходит автоматически вы не получаете никаких уведомлений об этом. Для того чтобы узнать закрылся ли ваш ордер используйте команду -q. Состояние ордера будет указано первой строчкой.
                    
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

Получения сигнала до момента открытия симуляции и получения данных проходит в среднем менее секунд, а в хужших сценариях около 15 секунд. В любом из случаев время задержки невероятно мало. Что делает их очень точными.

2 - Как работает симуляция stop loss и take profit?

При открытии сделки stop loss сработает на изменение цены монеты на 1% в направлении противоположном направлению открытия, и при достижении профита в 1% перенесет ST на 0.7% и при обновлении максимальноой прибыли будет двигать его вверх. TP в боте отсутствует

3 - Мне не нужны все фильтры могу ли я их не устанавливать?

Пока что нет вам прийдется написать все значения. Просто поставьте очень большие или очень маленькие значения.

4 - По каким монетам бот мониторит сигналы?

Только по монетам что есть на бирже MEXC

Внимание бот собирает всю историю всех ордеров с вашими id и результатами. Это делаетя чтобы иметь возможность собрать подробную статистику по лучшей торговой стратегии и фильтрам.
                """
        
                
        await client.send_message(event.sender_id, msg)
        return True
    await client.send_message(event.sender_id, "Команда не распознана. Введите -h для списка всех команд")  


async def print_user_account(id):
     async with aiosqlite.connect('bot_stats.db') as db:
            async with db.execute('''
                SELECT sum, time, price_change, simulate, amount, sholder, total FROM users WHERE user_id = ?''', (id,)) as cursor:
                result = await cursor.fetchone()
                if result:
                    msg = "Minimum target amount - " + str(result[0])
                    msg += "\nTime limit - " + str(result[1])
                    msg += "\nMinimum price change - " + str(result[2])
                    msg += "\nSimulate - " + str(result[3])
                    msg+= "\nSimulating orger amount - " + str(result[4])
                    msg += "\nSholder - " + str(result[5])
                    msg += "\nTotal profit - " + str(result[6])
                else:
                    msg = "У нас неи никаких фильтров используйте -a чтобы создать их"
                return msg
            
async def get_sholder_and_amount(id):
     async with aiosqlite.connect('bot_stats.db') as db:
            async with db.execute('''
                SELECT amount, sholder FROM users WHERE user_id = ?''', (id,)) as cursor:
                result = await cursor.fetchone()
                return result

async def update_settings(params):
    async with aiosqlite.connect('bot_stats.db') as db:
            async with db.execute('''
                SELECT sum FROM users WHERE user_id = ?''', (int(params[6]),)) as cursor:
                result = await cursor.fetchone()

            if not result:
                await db.execute('''
                    INSERT INTO users (user_id, sum, time, price_change, simulate, amount, sholder, total)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', 
                        (int(params[6]), int(params[0]),int(params[1]),float(params[2]),int(params[3]),float(params[4]), int(params[5]), 0))
                await db.commit()
            else:
                await db.execute(f'''
                    UPDATE users
                    SET sum = ?, time = ?, price_change = ?, simulate = ?, amount = ?, sholder = ?
                    WHERE user_id = ?;''', 
                        (int(params[0]),int(params[1]),float(params[2]),int(params[3]),float(params[4]), int(params[5]), int(params[6])))
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

async def print_orders(id):
    orders = [f"На данный момен открыто {len(memory[id])} сделок"]
    for socket in memory[id]:   
        message = ""
        message += f"{socket.symbol}\n"
        if not socket.valid_tocken:
            message += "Похоже симуляция не может быть запущенна по данному токену"
            orders.append(message)
            memory[id].remove(socket)
            print("Invalid token")
            continue
        if not socket.first :  
            message += "Подождиде пару секунд ордер на этот токен не успел открыться"
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
        

async def add_to_memmory(id, message):
    amount, sholder = await get_sholder_and_amount(id)
    print(str(amount) + " " + str(sholder))
    ws = price_monitoring.start_connection(message, amount, sholder)
    if id not in memory:
        memory[id] = []
    memory[id].append(ws)

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
