import socket
import threading

# the first copy of the app listens on this port, any later copy just pokes it and exits
PORT = 47631


def already_running():
    try:
        with socket.create_connection(("127.0.0.1", PORT), timeout=0.5) as conn:
            conn.sendall(b"show")
        return True
    except OSError:
        return False


def listen_for_show(on_show):
    server = socket.socket()
    try:
        server.bind(("127.0.0.1", PORT))
    except OSError:
        return  # port taken by something else, just skip this feature
    server.listen()

    def loop():
        while True:
            conn, _ = server.accept()
            with conn:
                if conn.recv(16) == b"show":
                    on_show()

    threading.Thread(target=loop, daemon=True).start()
