import socket
import threading
import csv
import time

# Store stock information by reading from the CSV file
stocks = {}

# Store bid information for each stock
stock_bids = {}

# Read stock data from the CSV file and populate the stocks dictionary
with open(r'C:\Users\SG\Documents\Downloads\stocks.csv', 'r') as file:
    csv_reader = csv.DictReader(file)
    for row in csv_reader:
        symbol = row['Symbol']
        price = float(row['Price'])
        stocks[symbol] = {'Price': price, 'Info': '', 'Security': ''}
        stock_bids[symbol] = {'HighestBid': price, 'Bidder': '', 'EndTime': None}

# Store publishers and subscribers
publishers = {}
subscribers = {}

# Define server logic for publisher-subscriber
def handle_publisher(conn, addr):
    publisher_id = conn.recv(1024).decode()  # Get publisher ID
    publishers[publisher_id] = conn
    print(f'Publisher {publisher_id} connected from {addr}')

    while True:
        try:
            data = conn.recv(1024).decode()
            if not data:
                break

            # Implement logic to publish stock information here
            parts = data.split(' ')
            if len(parts) == 7 and parts[0] == 'PUB':
                sym, info, security = parts[1], parts[3], parts[5]
                # Validate stock symbol, update stocks, and notify subscribers
                if sym in stocks:
                    stocks[sym]['Info'] = info
                    stocks[sym]['Security'] = security
                    notify_subscribers(sym, info)
                    conn.send(f'Successfully Published! {sym} / {info}'.encode())
                else:
                    conn.send(f'Invalid Stock Code {sym}'.encode())
            else:
                conn.send("Invalid Command".encode())
        except Exception as e:
            print(f"Error: {e}")
            break

    print(f'Publisher {publisher_id} disconnected')
    del publishers[publisher_id]
    conn.close()

def handle_subscriber(conn, addr):
    subscriber_id = conn.recv(1024).decode()  # Get subscriber ID
    print(f'Subscriber {subscriber_id} connected from {addr}')

    while True:
        try:
            data = conn.recv(1024).decode()
            if not data:
                break

            # Implement logic to subscribe or bid for stock information here
            parts = data.split(' ')
            if len(parts) > 1 and parts[0] == 'SUB':
                symbols = parts[1:]
                subscribe(subscriber_id, symbols, conn)
            elif len(parts) == 3 and parts[0] != 'SUB':
                sym, bid_amount, security = parts[0], int(parts[1]), parts[2]
                bid_result = place_bid(sym, bid_amount, security)
                conn.send(bid_result.encode())
            else:
                conn.send("Invalid Command".encode())
        except Exception as e:
            print(f"Error: {e}")
            break

    print(f'Subscriber {subscriber_id} disconnected')
    unsubscribe(subscriber_id)
    conn.close()

def notify_subscribers(symbol, info):
    # Send updates to all subscribers interested in the symbol
    for subscriber_id, symbols in subscribers.items():
        if symbol in symbols:
            conn = publishers.get(subscriber_id)
            if conn:
                conn.send(f'{symbol} ({info})'.encode())

def subscribe(subscriber_id, symbols, conn):
    success_messages = []
    error_messages = []

    for symbol in symbols:
        if symbol in stocks:
            info = stocks[symbol]['Info']
            conn.send(f'Successfully Subscribed! {symbol} / {info}'.encode())
            success_messages.append(f'Successfully Subscribed! {symbol}')
        else:
            conn.send(f'Invalid Code {symbol}'.encode())
            error_messages.append(f'Invalid Code {symbol}')

    # Output the results
    if success_messages:
        print("\n".join(success_messages))
    if error_messages:
        print("\n".join(error_messages))

    subscribers[subscriber_id] = symbols

def place_bid(symbol, bid_amount, security):
    if symbol not in stocks:
        return f'Invalid Stock Code {symbol}'
    
    stock_bid_info = stock_bids[symbol]

    if security != stocks[symbol]['Security']:
        return f'Invalid Security Code {symbol}'
    
    if bid_amount <= stock_bid_info['HighestBid']:
        return f'Invalid Bid {symbol} {stock_bid_info["HighestBid"]}'
    
    current_time = time.time()
    end_time = stock_bid_info['EndTime'] or current_time + 3600  # 1-hour initial bidding time

    if current_time > end_time:
        return f'Invalid Bid {symbol} {stock_bid_info["HighestBid"]} (Bidding has ended)'

    stock_bid_info['HighestBid'] = bid_amount
    stock_bid_info['Bidder'] = symbol
    stock_bid_info['EndTime'] = end_time

    # Track bid changes by appending to a SYM.txt file
    with open(f'{symbol}.txt', 'a') as file:
        file.write(f'Bid: {bid_amount} at {time.ctime(current_time)}\n')

    return f'Successfully Bided! {symbol} {bid_amount}'

# Set up the server socket
SERVER_HOST = 'localhost'
SERVER_PORT = 2023
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((SERVER_HOST, SERVER_PORT))
server.listen()
print("Publisher-Subscriber Server started. Listening on port 2023...")

# Accept incoming connections and spawn threads for publishers and subscribers
while True:
    conn, addr = server.accept()
    client_type = conn.recv(3).decode()  # Get client type ('PUB' or 'SUB')

    if client_type == 'PUB':
        publisher_thread = threading.Thread(target=handle_publisher, args=(conn, addr))
        publisher_thread.start()
    elif client_type == 'SUB':
        subscriber_thread = threading.Thread(target=handle_subscriber, args=(conn, addr))
        subscriber_thread.start()
 
