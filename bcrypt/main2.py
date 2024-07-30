from passlib.apache import HtpasswdFile

# Ruta del archivo de contraseñas
htpasswd_path = "/Users/tavogus/dev/tutorial-python/bcrypt/.htpasswd"

# Crea o carga el archivo de contraseñas
ht = HtpasswdFile(htpasswd_path, new=True)

# Añade usuarios y contraseñas
ht.set_password("root", "root")

# Guarda el archivo
ht.save()

print(f"Archivo de contraseñas generado en {htpasswd_path}")