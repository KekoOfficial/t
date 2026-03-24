# cola.py
from collections import deque

cola = deque()
estado_cola = []
en_proceso = False
VIP_USERS = [123456789]  # IDs VIP

def agregar_a_cola(user_id, username, query, url, formato):
    if user_id in VIP_USERS:
        cola.appendleft((query, formato, user_id, username, url))
        estado_cola.insert(0, username + " 👑VIP")
        posicion = 1
    else:
        cola.append((query, formato, user_id, username, url))
        estado_cola.append(username)
        posicion = len(cola)
    return posicion

def quitar_de_cola():
    if cola:
        estado_cola.pop(0)
        return cola.popleft()
    return None

def ver_cola():
    return "\n".join(estado_cola) if estado_cola else "🧾 Cola vacía"