import ccxt
import time
import tools


api_key = 'ВАШ_API_KEY'
secret_key = 'ВАШ_SECRET_KEY'

exchange = ccxt.mexc({
    'apiKey': api_key,
    'secret': secret_key,
    'enableRateLimit': True,
})

def open_position(message):
    if api_key == 'ВАШ_API_KEY':
        raise Exception("traiding bot doesn't setup yet")
    exchange.fapiPrivate_post_leverage({
        "symbol": tools.Tools.getSymbol(message),
        "leverage": leverage
    })
    order = tools.Tools.createOrder(message)
    return order



def set_stop_loss(symbol, amount, stop_price, side):
    params = {"stopPrice": stop_price}
    order = exchange.create_order(
        symbol=symbol,
        type='STOP_MARKET',
        side=side,
        amount=amount,
        params=params
    )
    return order

symbol = 'BTC/USDT'
leverage = 20
amount = 0.001
side = 'buy'  

