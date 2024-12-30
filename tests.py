import unittest
import tools

class TestStringMethods(unittest.TestCase):
    def setUp(self):
        self.val_msg = """$9.95M buying JLP 🟩
    
MCAP: $1.62B
Liquidity: $21.87M
ETA: 20 minutes
Potential price change: 52.75%

Holders: 60,302
Vol 24h: $102.03M

CA: 27G8MtK7VtTcCHkpASjSDdkWWYfoqT6ggEuKidVJidD4
#uKidVJidD4

User: CmxF3yQgwEXNkgXgCapB6HXmGMGsUyNQsZdAkyKg6CWR
#dAkyKg6CWR

Amount: 9,948,804.35 USDC
Frequency: $497.45K every 60 seconds

MEXC

Period: 27 Dec 2024 09:35:50 GMT - 27 Dec 2024 09:55:50 GMT
🗒 C: 0, A: 0, I: 0, T: 0
👍 ETA less than 1 hour
👍 Amount per cycle more than $3K
👍 Potential price change: 52.8%
DCA Tracker - Feedback
"""

        self.invalid_msg = """"$143.39K buying PENGU 🟩
            
        MCAP: $3.29B
        Liquidity: $94.64M
        ETA: 51 minutes
        Potential price change: 0.30%

        Holders: 513,234
        Vol 24h: $255.85M

        CA: 2zMMhcVQEXDtdE6vsFS7S7D5oUodfJHE8vd1gnBouauv
        #d1gnBouauv

        User: J1f47McZ8Ay1EZuDpvMX7CMdHag1z2mHiXNH1XQuiFip
        #NH1XQuiFip

        Futures: MEXC Bitget Gate

        Promo: Bonus 30-500 USD for trading volume >1000$, 5-50 USD for the first trade for new users.

        Amount: 730.67 SOL
        Frequency: $2.87K every 60 seconds

        Period: 24 Dec 2024 18:49:53 GMT - 24 Dec 2024 19:40:53 GMT
        🗒 C: 0, A: 1, I: 0, T: 1
        👍 ETA less than 1 hour
        👍 Potential price change: 7.1%
        🤔 Amount per cycle between $1K and $3K
        🚩 Canceled 1 without completing, which is 100%
        🚩 Opened 1 in the last 20 minutes"""

    def test_isCanceledPossible(self):
        self.assertTrue(tools.Tools.isCanceledPossible(self.val_msg))
        self.assertFalse(tools.Tools.isCanceledPossible(self.invalid_msg))

    def test_isValidMessage(self):
        self.assertTrue(tools.Tools.isValidMessage(self.val_msg))
        self.assertFalse(tools.Tools.isValidMessage(self.invalid_msg))

    def test_isGoodTime(self):
        self.assertTrue(tools.Tools.idGoodTime(self.val_msg))
        self.assertTrue(tools.Tools.idGoodTime(self.invalid_msg))

if __name__ == '__main__':
    unittest.main()