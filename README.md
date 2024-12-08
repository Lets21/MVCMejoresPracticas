# 🏥 Infinite Health - Sistema de Gestión Médica

## 📋 Descripción
Infinite Health es un sistema integral de gestión médica desarrollado con Django que facilita la administración de clínicas y hospitales. El sistema permite gestionar pacientes, doctores, tratamientos y medicamentos, con un enfoque especial en la seguridad del paciente y la eficiencia operativa.

## 🌟 Características Principales

### 👥 Gestión de Usuarios
- **Roles de Usuario:**
  - 🏥 Administradores: Control total del sistema
  - 👨‍⚕️ Doctores: Gestión de pacientes y tratamientos
  - 🧑‍🤝‍🧑 Pacientes: Acceso a historial y citas
- Sistema robusto de autenticación y autorización
- Perfiles personalizados por tipo de usuario

### 👨‍⚕️ Sistema de Tratamientos
- Creación y seguimiento de tratamientos médicos
- Asignación inteligente de medicamentos
- Sistema automático de sustitución por alergias
- Control de contraindicaciones médicas

### 💊 Gestión de Medicamentos
- Inventario completo de medicamentos
- Registro de componentes principales
- Sistema de sustitución automática
- Control de contraindicaciones y alergias

### 📅 Sistema de Citas
- Programación flexible de citas médicas
- Validación de disponibilidad
- Seguimiento del estado de las citas
- Notificaciones automáticas

## 🛠️ Tecnologías Utilizadas

- **Backend:** Django 4.1
- **Frontend:** Bootstrap 5.3
- **Base de Datos:** SQLite
- **Iconos:** Font Awesome 6.5
- **Alertas:** SweetAlert2

## ⚙️ Requisitos del Sistema

- Python 3.8+
- Django 4.1
- Otras dependencias listadas en requirements.txt

## 🚀 Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/tu-usuario/infinite-health.git
cd infinite-health
```

2. Crear y activar entorno virtual:
```bash
python -m venv venv
source venv/bin/activate # Linux/Mac
venv\Scripts\activate # Windows
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Realizar migraciones:
```bash
python manage.py makemigrations                    
python manage.py migrate
```

5. Crear datos iniciales:
```bash
python manage.py flush      

python manage.py crear_datos_iniciales
```

6. Iniciar servidor:
```bash
python manage.py runserver
```

## 👥 Usuarios por Defecto

### 🔑 Administrador
- Usuario: admin
- Contraseña: admin123

### 👨‍⚕️ Doctores
- Usuarios: dr.garcia, dra.rodriguez, dr.martinez
- Contraseña (todos): contraseña123

### 🧑‍🤝‍🧑 Pacientes
- Usuarios: juan.perez, pedro.gomez, maria.sanchez
- Contraseña (todos): contraseña123

## 🔒 Seguridad

- Autenticación robusta de usuarios
- Protección contra CSRF
- Manejo seguro de sesiones
- Validación exhaustiva de datos
- Sistema de permisos por rol

## 📱 Características de la Interfaz

- Diseño responsive con Bootstrap 5
- Interfaz intuitiva y amigable
- Iconografía clara con Font Awesome
- Alertas interactivas con SweetAlert2
- Navegación simplificada

## 🤝 Contribución

1. Fork el proyecto
2. Crea tu rama de características (`git checkout -b feature/NuevaCaracteristica`)
3. Commit tus cambios (`git commit -m 'Añadir nueva característica'`)
4. Push a la rama (`git push origin feature/NuevaCaracteristica`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE.md](LICENSE.md) para más detalles.

## 🌐 Enlaces Útiles

- [Documentación de Django](https://docs.djangoproject.com/)
- [Bootstrap Documentation](https://getbootstrap.com/docs/)
- [Font Awesome Icons](https://fontawesome.com/icons)
- [SweetAlert2 Documentation](https://sweetalert2.github.io/)

## 📧 Contacto

Para preguntas y soporte, por favor contacta a:
- Email: [tu@email.com](mailto:tu@email.com)
- GitHub: [tu-usuario](https://github.com/tu-usuario)
