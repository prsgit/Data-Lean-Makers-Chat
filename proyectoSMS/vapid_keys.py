from pywebpush import Vapid
from cryptography.hazmat.primitives import serialization

# Generar claves VAPID usando la clase Vapid
vapid = Vapid()
vapid.generate_keys()

# Convertir las claves a formato legible (PEM)
public_key = vapid.public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
).decode('utf-8')

private_key = vapid.private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
).decode('utf-8')

# Mostrar las claves generadas
print("VAPID Public Key:")
print(public_key)
print("VAPID Private Key:")
print(private_key)
