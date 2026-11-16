import socket
import threading

HOST = "0.0.0.0"   # listen on all network interfaces
PORT = 5050

# Connected clients: nickname -> {"sock": socket, "room": room name}
clients = {}

# Lock used whenever a thread reads or changes the "clients" dictionary
lock = threading.Lock()


def send(sock, text):
    """Send one line of text to a client."""
    try:
        sock.sendall((text + "\n").encode("utf-8"))
    except OSError:
        pass  # if the client dropped, its own thread handles the cleanup


def send_to_room(room, text, exclude=None):
    """Send a text to everyone in the room (except 'exclude')."""
    with lock:
        targets = [data["sock"] for name, data in clients.items()
                   if data["room"] == room and name != exclude]
    for sock in targets:
        send(sock, text)


def register(sock, nickname):
    """Try to register the nickname. Return the nickname on success, or None."""
    if nickname == "" or " " in nickname or len(nickname) > 15:
        send(sock, "Invalid nickname (no spaces, up to 15 characters). Try another one:")
        return None
    with lock:
        if nickname in clients:
            taken = True
        else:
            taken = False
            clients[nickname] = {"sock": sock, "room": "general"}
    if taken:
        send(sock, "That nickname is already in use. Try another one:")
        return None
    send(sock, f"Welcome, {nickname}! You are in the 'general' room. Type /help to see the commands.")
    send_to_room("general", f"* {nickname} joined the room.", exclude=nickname)
    return nickname


def handle_message(nickname, line):
    """Interpret a line sent by the client. Return False if the client wants to quit."""
    sock = clients[nickname]["sock"]
    room = clients[nickname]["room"]

    if line == "/quit":
        send(sock, "Goodbye!")
        return False

    elif line == "/help":
        send(sock, "Commands: /join <room>, /msg <nickname> <text>, /users, /rooms, /quit")

    elif line == "/users":
        with lock:
            names = sorted(clients.keys())
        send(sock, "Online: " + ", ".join(names))

    elif line == "/rooms":
        count = {}
        with lock:
            for data in clients.values():
                count[data["room"]] = count.get(data["room"], 0) + 1
        send(sock, "Rooms: " + ", ".join(f"{r} ({n})" for r, n in count.items()))

    elif line.startswith("/join "):
        new_room = line[6:].strip().lower()
        if new_room == "" or " " in new_room:
            send(sock, "Invalid room name.")
        else:
            with lock:
                clients[nickname]["room"] = new_room
            send_to_room(room, f"* {nickname} left the room.")
            send_to_room(new_room, f"* {nickname} joined the room.", exclude=nickname)
            send(sock, f"You are now in the '{new_room}' room.")

    elif line.startswith("/msg "):
        parts = line.split(" ", 2)   # ["/msg", "target", "text"]
        if len(parts) < 3:
            send(sock, "Usage: /msg <nickname> <text>")
        else:
            target, text = parts[1], parts[2]
            with lock:
                target_data = clients.get(target)
            if target_data is None:
                send(sock, "User not found.")
            else:
                send(target_data["sock"], f"[private from {nickname}] {text}")
                send(sock, f"[private to {target}] {text}")

    elif line.startswith("/"):
        send(sock, "Unknown command. Type /help.")

    else:
        send_to_room(room, f"[{room}] {nickname}: {line}")

    return True


def handle_client(sock, address):
    """Function run by a separate thread for each connected client."""
    nickname = None
    buffer = b""
    send(sock, "Enter your nickname:")
    try:
        while True:
            data = sock.recv(1024)
            if not data:           # empty recv = client closed the connection
                break
            buffer += data
            # TCP may merge or split messages, so we separate them by line breaks
            while b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)
                line = line.decode("utf-8", errors="replace").strip()
                if line == "":
                    continue
                if nickname is None:
                    nickname = register(sock, line)
                    if nickname:
                        print(f"[+] {nickname} connected from {address}")
                elif not handle_message(nickname, line):
                    return
    except OSError:
        pass  # client dropped abruptly
    finally:
        if nickname:
            with lock:
                room = clients.pop(nickname)["room"]
            send_to_room(room, f"* {nickname} disconnected.")
            print(f"[-] {nickname} disconnected")
        sock.close()


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()
    # accept() waits at most 1 second at a time, so Ctrl+C works on Windows too
    server.settimeout(1.0)
    print(f"Server listening on port {PORT}. Press Ctrl+C to stop.")
    try:
        while True:
            try:
                conn, address = server.accept()
            except socket.timeout:
                continue           # nobody connected; check Ctrl+C and wait again
            conn.settimeout(None)  # client sockets wait without a time limit
            t = threading.Thread(target=handle_client, args=(conn, address), daemon=True)
            t.start()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.close()


if __name__ == "__main__":
    main()