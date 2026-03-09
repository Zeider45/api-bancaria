#!/bin/bash

echo "🚀 Iniciando SIB API Bridge en modo desarrollo..."

# Limpiar contenedores anteriores (opcional)
docker-compose down -v

# Construir y levantar todos los servicios
docker-compose up --build -d

# Esperar a que PostgreSQL esté listo
echo "⏳ Esperando a que los servicios estén listos..."
sleep 15

# Ejecutar migraciones
echo "🔄 Ejecutando migraciones..."
docker-compose exec backend python manage.py migrate

# Crear superusuario (opcional)
echo "👤 Creando superusuario admin..."
docker-compose exec backend python manage.py createsuperuser \
    --noinput \
    --username admin \
    --email admin@example.com 2>/dev/null || true

# Establecer contraseña para admin
docker-compose exec backend python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
try:
    user = User.objects.get(username='admin');
    user.set_password('admin123');
    user.save();
    print('✅ Contraseña de admin establecida a: admin123');
except:
    print('⚠️ No se pudo establecer contraseña');
"

echo "✅ Proyecto iniciado correctamente!"
echo "📊 Backend API: http://localhost:8000"
echo "📊 Admin Django: http://localhost:8000/admin"
echo "🎨 Frontend: http://localhost:3000"
echo ""
echo "🔑 Credenciales por defecto:"
echo "   Usuario: admin"
echo "   Password: admin123"
echo ""
echo "📝 Para ver logs: docker-compose logs -f"
echo "🛑 Para detener: docker-compose down"