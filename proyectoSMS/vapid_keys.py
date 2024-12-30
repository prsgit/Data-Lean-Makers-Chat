from py_vapid import Vapid
from cryptography.hazmat.primitives import serialization
from base64 import urlsafe_b64encode

# Generar claves VAPID
vapid = Vapid()
vapid.generate_keys()

# Convertir la clave pública a formato base64url
public_key = urlsafe_b64encode(
    vapid.public_key.public_bytes(
        encoding=serialization.Encoding.X962,  # Formato correcto para la clave pública
        format=serialization.PublicFormat.UncompressedPoint
    )
).decode('utf-8').rstrip("=")

# Convertir la clave privada a formato base64url en DER
private_key = urlsafe_b64encode(
    vapid.private_key.private_bytes(
        encoding=serialization.Encoding.DER,  # Cambiado a DER para pywebpush
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
).decode('utf-8').rstrip("=")

# Mostrar las claves generadas
print("VAPID Public Key:")
print(public_key)
print("VAPID Private Key:")
print(private_key)
