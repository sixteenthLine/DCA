import unittest
import tools

class TestStringMethods(unittest.TestCase):
    def setUp(self):
        self.val_msg = """$102.60K selling UFD 🟥
    
MCAP: $146.56M
Liquidity: $6.80M
ETA: 1 hs, 5 mins
Potential price change: 2.95%

Holders: 33,621
Vol 24h: $17.46M

CA: eL5fUxj2J4CiQsmW85k5FG9DvuQjjUoBHoQBi2Kpump
#oQBi2Kpump

User: C36KZ692jSeFAui9kaRcA6ounG6NfUkWjhMCMQmsBK9H
#MCMQmsBK9H

Futures: MEXC

Amount: 700,000.00 UFD
Frequency: $2.85K every 300 seconds

Period: 11 Jan 2025 21:02:44 GMT - 12 Jan 2025 00:07:44 GMT
🗒 Total: 7 [✅: 0, ❌: 5, 🔄: 2]
👍 Futures available
🤔 ETA between 1 and 5 hours
🤔 Amount per cycle between $1K and $3K
🚩 Canceled 5 without completing, which is 71%
"""

        self.invalid_msg = """$87.38K buying UFD 🟩
    
MCAP: $137.68M
Liquidity: $6.80M
ETA: 1 h, 41 mins
Potential price change: 2.52%

Holders: 33,610
Vol 24h: $17.52M

CA: eL5fUxj2J4CiQsmW85k5FG9DvuQjjUoBHoQBi2Kpump
#oQBi2Kpump

User: 2rWGczJQKKDaF67MyRHFZGjyzYR4AAYXe9yXog9sFbCt
#yXog9sFbCt

Futures: MEXC

Output mint: Fartcoin  - 0.64% - MEXC

Amount: 109,633.71 Fartcoin 
Frequency: $873.81 every 60 seconds

Period: 11 Jan 2025 20:22:16 GMT - 11 Jan 2025 22:03:16 GMT
🗒 Total: 1 [✅: 0, ❌: 0, 🔄: 1]
👍 Futures available
🤔 ETA between 1 and 5 hours
🚩 Amount per cycle less than $1K"""

    def test_isValidMessage(self):
        self.assertTrue(tools.Tools.isValidMessage(self.val_msg, 70, 210, 0.1, 350))
        # self.assertFalse(tools.Tools.isValidMessage(self.invalid_msg, 0, 200, 0, 500))

    def test_isGoodTime(self):
        self.assertTrue(tools.Tools.idGoodTime(self.val_msg))
        self.assertTrue(tools.Tools.idGoodTime(self.invalid_msg))

if __name__ == '__main__':
    unittest.main()