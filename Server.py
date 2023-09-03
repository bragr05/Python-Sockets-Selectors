import socket
import selectors

# Para crear objetos
import types

sel = selectors.DefaultSelector()

HOST = 'localhost'
PORT = 3000

lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((HOST, PORT))
lsock.listen()
print(f"Escuchando en {HOST} puerto {PORT}")

# Configurar como modo sin bloqueo
lsock.setblocking(False)

# Configurar el selector para cuando hayan datos disponibles para lectura en el socket pasado como parámetro (lsock)
sel.register(lsock, selectors.EVENT_READ, data=None)


def accept_wrapper(sock):
  conn, addr = sock.accept()
  print(f"Conexión aceptada de {addr}")

  # No bloqueante para obtener los datos inmediatamente aunque no hayan en funciones como recv(), read(), send(), write()....
  conn.setblocking(False)

  # Creación de obj con props addr, inb y 'outb'
  data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")

  # Definir máscara de bits para especificar luego al selector con cuales eventos debe estar atento para dicho socket
  events = selectors.EVENT_READ | selectors.EVENT_WRITE

  # Registrar el socket en el selector
  sel.register(conn, events, data=data)


def service_connection(key, mask):
  # Obtener el socket que será atendido
  sock = key.fileobj
  # Obtener los datos
  data = key.data

  # Si mask es un evento de lectura (selectors.EVENT_READ)
  if mask & selectors.EVENT_READ:
    recv_data = sock.recv(1024)
    # Validación para evitar almacenar datos vacíos
    if recv_data:
      data.outb += recv_data
    else:
      print(f"Cerrando conexión con socket {data.addr}")
      
      # Des registrar el socket del selector y cerrar la conexión
      sel.unregister(sock)
      sock.close()
  if mask & selectors.EVENT_WRITE:

    # Enviar datos solo si hay datos en data.outb
    if data.outb:
      print(f"Enviando ' {data.outb!r}' a el socket {data.addr}")

      # Almacenar total de bytes enviados
      sent = sock.send(data.outb) 
      
      # Actualizar data.outb para que contenga los datos desde sent hasta el final
      data.outb = data.outb[sent:]
      """
       Lo anterior se hace con el fin de mantener los datos que no se lograron enviar
      """

# Bucle de eventos
try:
  while True:
    """
      Espera un E/S de los socket registrados, devuelve tuplas (key, mask) para cada uno de los sockets registrados
      Key -> Describe un evento de socket en el selector.
      Mask -> Máscara de bits que indica qué tipo de evento ha ocurrido en el socket
    """
    events = sel.select(timeout=None)

    # Key en un objeto SelectorKey que representa al socket registrado el el selector
    # Mask representa el tipo de evento activado (Escritura - lectura) que es una mascara de bits https://www.victoriglesias.net/mascaras-de-bits/
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
