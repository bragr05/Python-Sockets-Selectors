import socket
import selectors
import types

sel = selectors.DefaultSelector()

HOST = 'localhost'
PORT = 3000

lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((HOST, PORT))
lsock.listen()
print(f"Escuchando en {HOST} puerto {PORT}")
lsock.setblocking(False)

sel.register(lsock, selectors.EVENT_READ, data=None)

def accept_wrapper(sock):
  conn, addr = sock.accept()
  print(f"Conexión aceptada de IP: {addr}")
  conn.setblocking(False)
  data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
  events = selectors.EVENT_READ | selectors.EVENT_WRITE
  sel.register(conn, events, data=data)

def service_connection(key, mask):
  sock = key.fileobj
  data = key.data

  if mask & selectors.EVENT_READ:
    recv_data = sock.recv(1024)
    if recv_data:
      data.outb += recv_data
    else:
      print(f"Cerrando conexión con socket {data.addr}")
      sel.unregister(sock)
      sock.close()

  if mask & selectors.EVENT_WRITE:
    if data.outb:
      print(f"Enviando ' {data.outb!r}' a el socket {data.addr}")
      sent = sock.send(data.outb)
      data.outb = data.outb[sent:]

try:
  while True:
    events = sel.select(timeout=None)
    for key, mask in events:
      if key.data is None:
        accept_wrapper(key.fileobj)
      else:
        service_connection(key, mask)
except KeyboardInterrupt:
  print("Interrupción del teclado captada, saliendo")
finally:
  sel.close()
