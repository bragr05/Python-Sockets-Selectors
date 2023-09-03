
import socket
import selectors
import types
import sys

sel = selectors.DefaultSelector()

HOST = 'localhost'
PORT = 3000

lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((HOST, PORT))
lsock.listen()
print(f"Escuchando en {HOST} puerto {PORT}")


def accept_wrapper(sock):
  conn, addr = sock.accept() 
  print(f"Accepted connection from {addr}")
  conn.setblocking(False)
  data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
  events = selectors.EVENT_READ | selectors.EVENT_WRITE
  sel.register(conn, events, data=data)


def accept_wrapper(sock):
  conn, addr = sock.accept()  # Should be ready to read
  print(f"Accepted connection from {addr}")
  conn.setblocking(False)
  data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
  events = selectors.EVENT_READ | selectors.EVENT_WRITE
  sel.register(conn, events, data=data)


# Configurar como modo sin bloqueo
lsock.setblocking(False)

# Configurar el selector para cuando hayan datos disponibles para lectura en el socket pasado como parámetro (lsock)
sel.register(lsock, selectors.EVENT_READ, data=None)

# Bucle de eventos
try:
  while True:

    """
      Espera un E/S de los socket registrados, devuelve tuplas (key, mask) para cada uno de los sockets registrados
      Key -> Describe un evento de socket en el selector.
      Mask -> Máscara de bits que indica qué tipo de evento ha ocurrido en el socket
    """
    events = sel.select(timeout=None)

    for key, mask in events:

      """
        Si key.data es None, significa que el evento está relacionado con el socket del servidor, que generalmente se utiliza para aceptar nuevas conexiones de clientes entrantes. En este caso, el código llama a la función accept_wrapper() para manejar el evento del servidor.

        Si key.data no es None, significa que el evento está relacionado con uno de los sockets de cliente registrados previamente. En este caso, el código debe tomar las acciones necesarias para manejar los eventos de lectura o escritura en ese socket específico.
      """
      if key.data is None:
        accept_wrapper(key.fileobj)
      else:
        service_connection(key, mask)
except KeyboardInterrupt:
  print("Interrupción del teclado captada, saliendo")
finally:
  sel.close()
