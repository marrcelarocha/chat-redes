import socket
import sys
import threading

PORT = 5050


def receive(sock):
    """Thread that keeps waiting for messages from the server."""
    while True:
        try:
            data = sock.recv(1024)
        except OSError:
            break
        if not data:           # server closed the connection
            break
        print(data.decode("utf-8", errors="replace"), end="")
    print("Connection closed.")


def main():
    # The server IP can be passed on the command line; default is this machine
    host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, PORT))
    except OSError as error:
        print(f"Could not connect to {host}:{PORT} ({error})")
        return

    # Receiving thread: lets the user read and type at the same time
    t = threading.Thread(target=receive, args=(sock,), daemon=True)
    t.start()

    # The main thread reads the keyboard and sends to the server
    try:
        while True:
            text = input()
            sock.sendall((text + "\n").encode("utf-8"))
            if text.strip() == "/quit":
                t.join(timeout=1)   # wait for the server's "Goodbye!"
                break
    except (EOFError, KeyboardInterrupt, OSError):
        pass
    sock.close()


if __name__ == "__main__":
    main()
