import os
from OpenSSL import crypto

# Create key and certificate
key = crypto.PKey()
key.generate_key(crypto.TYPE_RSA, 2048)

cert = crypto.X509()
cert.get_subject().CN = "localhost"
cert.set_serial_number(1000)
cert.gmtime_adj_notBefore(0)
cert.gmtime_adj_notAfter(365*24*60*60)  # Valid for a year
cert.set_issuer(cert.get_subject())
cert.set_pubkey(key)
cert.sign(key, 'sha256')

# Write certificate and key to files
with open('server.key', 'wb') as keyfile:
    keyfile.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))

with open('server.cert', 'wb') as certfile:
    certfile.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))

print("Certificate and key files created!")
