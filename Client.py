import socket
import selectors
import types

sel = selectors.DefaultSelector()
messages = [b'Mensaje 01 de cliente', b'Mensaje 02 de cliente']

def start_connections(num_conns):
  server_addr = ('localhost', 3000)
  for i in range(0, num_conns):
    connid = i + 1
    print(f'Iniciando conexión {connid} con {server_addr}')
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)

    # Se usa connect_ex y no connect ya que este generaría una BlockingIOError exception.
    sock.connect_ex(server_addr)

    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    data = types.SimpleNamespace(
      connid=connid,
      msg_total=sum(len(m) for m in messages),
      recv_total=0,
      messages=messages.copy(),
      outb=b"",
    )
    sel.register(sock, events, data=data)


def service_connection(key, mask):
  sock = key.fileobj
  data = key.data

  if mask & selectors.EVENT_READ:
    recv_data = sock.recv(1024)
    if recv_data:
      print(f"Recibido {recv_data!r} de la conexión {data.connid}")
      data.recv_total += len(recv_data)

    if not recv_data or data.recv_total == data.msg_total:
      print(f"Cerrando conexión con {data.connid}")
      sel.unregister(sock)
      sock.close()

  if mask & selectors.EVENT_WRITE:
    if not data.outb and data.messages:
      data.outb = data.messages.pop(0)
    if data.outb:
      print(f"Enviando {data.outb!r} a la conexión {data.connid}")
      sent = sock.send(data.outb)
      data.outb = data.outb[sent:]


start_connections(4)


try:
  while True:
    events = sel.select(timeout=1)
    if events:
      for key, mask in events:
        service_connection(key, mask)
    if not sel.get_map():
      break
except KeyboardInterrupt:
  print("Interrupción del teclado captada, saliendo")
finally:
  sel.close()
