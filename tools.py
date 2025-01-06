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
    def isCanceledPossible(message):
        if "which is" in message :
            if int(message.split(" which is ")[1].split("%")[0]) == 110:
                return False
        return True

    @staticmethod
    def idGoodTime(message):
        minutes = 0
        if "hour" in message.split("%")[0]:
            hours = int(message.split(" hour")[0].split(" ")[-1])
            minutes += hours * 60
        if "minut" in message.split("%")[0]:
            minutes += int(message.split("%")[0].split(" minut")[0].split(" ")[-1])
        print(minutes)
        return minutes
    
    @staticmethod 
    def has_mexc(message):  
        return "Futures: MEXC" in message

    @staticmethod
    def isValidMessage(message, sum, time, price_change):
        try :
            return Tools.getPercentages(message) >= price_change and Tools.idGoodTime(message) < time and Tools.isCanceledPossible(message) and Tools.getAmout(message) > sum
        except:
            return False

    
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
    