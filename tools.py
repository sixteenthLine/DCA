import time

class Tools:
    @staticmethod
    def getAmout(message):
        msg = message.split(" ")[0]
        if "M" in msg:
            return 1000
        return int(msg[1:-1].split(".")[0])
    
    @staticmethod
    def getDirection(message):
        return "selling" in message
        
    @staticmethod   
    def getPercentages(message):
        try :
            percentages = float(message.split("%")[0].split(" ")[-1])
            return percentages

        except :
            return -1
    

    @staticmethod
    def idGoodTime(message):
        minutes = 0
        time_line = message.split("\n")[4].split(" ")
        print(time_line)
        if len(time_line) > 4:
            minutes += int(time_line[1]) * 60 + int(time_line[3])
        elif "h" in time_line:
            minutes += int(time_line[1]) * 60
        else:
            minutes += int(time_line[1])
        return minutes
    
    @staticmethod 
    def has_mexc(message):  
        return "Futures: MEXC" in message

    @staticmethod
    def isValidMessage(message, sum, time, price_change, frequency):
        try :
            return Tools.getPercentages(message) >= price_change and Tools.idGoodTime(message) < time and Tools.getAmout(message) > sum and Tools.validFrequency(message) >= frequency
        except:
            return False
        
    @staticmethod
    def validFrequency(message):
        frequency_line = message.split("Frequency: $")[1].split("\n")[0]
        if frequency_line.split(" ")[2] == "60":
            if "K" in frequency_line.split(" ")[0]:
                return float(frequency_line.split(" ")[0].split("K")[0]) * 1000
            else :
                return float(frequency_line.split(" ")[0])
        else:
            if "K" in frequency_line.split(" ")[0]:
                return float(frequency_line.split(" ")[0].split("K")[0]) * 1000 / (float(frequency_line.split(" ")[2])/60)
            else :
                return float(frequency_line.split(" ")[0]) / (float(frequency_line.split(" ")[0])/60)
        


    @staticmethod
    def getSymbol(message):
        return message.split(" ")[2]

    @staticmethod
    def createOrder(message):
        return {"symbol": Tools.getSymbol(message),
                "type": "market",
                "side": Tools.getDirection(message),
                "amount": 40
                }
    