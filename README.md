# MiJuntaDigital - Sistema Territorial de Gestión Comunitaria

[![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-Backend-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Supabase-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://supabase.com/)
[![Docker](https://img.shields.io/badge/Docker-Desktop-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![n8n](https://img.shields.io/badge/n8n-Automation-FF6584?style=for-the-badge&logo=n8n&logoColor=white)](https://n8n.io/)
[![Google Gemini](https://img.shields.io/badge/IA-Google_Gemini-8E75B2?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)

**Proyecto de Título — Ingeniería en Informática (Duoc UC)**  
**Jefe de Proyecto, Desarrollador FullStack y Administrador de BD:** Felipe Fuentes  
**Docente Guía:** Arturo Vargas  

---

## Contexto y Problemática

Las Juntas de Vecinos cumplen un rol fundamental en la organización territorial en Chile al administrar espacios comunitarios, proyectos, actividades y trámites locales. Sin embargo, la gran mayoría opera bajo flujos manuales y gestiones presenciales que generan:

* Errores y demoras en la emisión de documentos e inscripción de residentes.
* Falta de trazabilidad y transparencia en proyectos y presupuesto comunitario.
* Choque de horarios en la reserva de espacios comunes.
* Baja participación de residentes jóvenes debido a la falta de canales digitales.

En un contexto donde más del 94% de los hogares en Chile cuenta con acceso a internet, **MiJuntaDigital** nace para centralizar, automatizar y modernizar la gestión vecinal mediante una plataforma tecnológica accesible, transparente e inteligente.

---

## Solución Propuesta

**MiJuntaDigital** es una solución web integral que digitaliza los procesos clave de una Junta de Vecinos:

* **Validación de Residentes:** Registro ágil de vecinos con verificación de identidad y roles (Vecino / Directiva).
* **Certificados de Residencia Automáticos:** Emisión digital con código QR, folio único, firma digital e integración de pasarela de pago (Webpay).
* **Gestión de Espacios Comunitarios:** Calendario de reservas en tiempo real para evitar duplicidad de horarios.
* **Proyectos y Votaciones:** Módulo transparente para la revisión, aprobación y votación de proyectos barriales.
* **Atención Inteligente (IA):** Chatbot integrado alimentado por Google Gemini y procesamiento OCR (Google Cloud Vision) para validación de documentos respaldantes.
* **Automatización y Reportes:** Flujos automatizados con n8n para generación de informes PDF periódicos y envío de correos.

---

## Arquitectura del Sistema

El proyecto opera bajo un esquema desacoplado y moderno enfocado en la nube y la automatización:

```text
[ Usuario / Vecino / Directiva ]
               │
       (Navegador Web)
               │
     ┌─────────┴─────────┐
     │   Frontend Web    │ (HTML5 / CSS3 / JavaScript)
     └─────────┬─────────┘
               │
     ┌─────────┴─────────┐
     │  Backend Django   │ (Python / API REST)
     └─────────┬─────────┘
               │
 ┌─────────────┼──────────────┬──────────────────┬─────────────────┐
 │             │              │                  │                 │
▼             ▼              ▼                  ▼                 ▼
[Supabase/PostgreSQL]  [Webpay]  [n8n Workflow]  [Google Gemini]  [Cloud Vision OCR]
 (BD y Storage)        (Pagos)    (Correos/PDF)   (Chatbot IA)      (Lectura Doc)
```
## Stack Tecnológico

| Capa | Tecnología / Herramienta |
| :--- | :--- |
| **Frontend** | HTML5, CSS3, JavaScript |
| **Backend** | Python, Django Framework |
| **Base de Datos & Storage** | PostgreSQL, Supabase |
| **DevOps & Entorno** | Docker Desktop, Git, GitHub |
| **Automatización & IA** | n8n (Orquestación), Google Gemini API, Google Cloud Vision (OCR) |
| **Pasarela de Pagos** | Webpay (Transbank) |

---

## Metodología de Desarrollo (SCRUM)

El desarrollo se estructuró en 8 Sprints iterativos e incrementales:

* **Sprint 0:** Levantamiento de requerimientos, diagramas de arquitectura, casos de uso, mockups y diseño de modelo de datos.
* **Sprint 1 (Módulo de Usuarios):** Registro, inicio de sesión, roles (Vecino/Directiva), perfiles y validación de solicitudes.
* **Sprint 2 (Certificados y Pagos):** Flujo de aprobación, integración con Webpay, generación de QR/folio único y automatizaciones con n8n.
* **Sprint 3 (Espacios Comunitarios):** CRUD de espacios comunitarios, módulo de reservas e inscripción a actividades.
* **Sprint 4 (Proyectos y Noticias):** Publicación de proyectos vecinales, votaciones en línea y portal de noticias.
* **Sprint 5 (Solicitudes y Auditoría):** Tablero de gestión de solicitudes ciudadanas para la directiva y sistema de bitácora/auditoría.
* **Sprint 6 (Inteligencia Artificial):** Chatbot conversacional con Gemini API, módulo OCR para lectura de documentos y reportes semanales con n8n.
* **Sprint 7 (Cierre & Despliegue):** Pruebas de integración, dockerización del sistema, manuales de usuario y documentación final.

---

## Desafíos Técnicos y Soluciones

### 1. Migración de Base de Datos
* **Desafío:** MariaDB presentó inconsistencias en migraciones complejas, conflictos de claves foráneas y límites en entornos cloud.
* **Solución:** Se realizó una migración hacia **PostgreSQL en Supabase**, logrando mayor estabilidad, mejor integración nativa con Django y un entorno cloud escalable.

### 2. Contenerización con Docker
* **Desafío:** Configuración inicial de red y persistencia de datos entre contenedores en entornos locales y de despliegue.
* **Solución:** Se construyeron imágenes livianas y un archivo `docker-compose` estructurado para garantizar la replicabilidad del entorno de desarrollo.

### 3. Seguridad y Gestión de Credenciales
* **Desafío:** Exposición de claves API de servicios de IA y pasarelas externas.
* **Solución:** Implementación de consultas de credenciales cifradas mediante almacenamiento seguro en Supabase y orquestación con n8n, evitando el hardcodeo de tokens en el repositorio.

### 4. Orquestación de Flujos Asíncronos con n8n
* **Desafío:** Coordinación de eventos del backend para disparar la creación de reportes ejecutivos en PDF y envío de notificaciones automáticas.
* **Solución:** Diseño de flujos basados en Webhooks integrados a Django que procesan datos, generan vistas HTML y consolidan archivos PDF adjuntos vía correo electrónico.

---

## Instalación y Ejecución Local

### Opción 1: Mediante Docker Desktop (Recomendado)

bash
# 1. Clonar el repositorio
git clone [https://github.com/Felifhh/Proyecto_Titulo.git](https://github.com/Felifhh/Proyecto_Titulo.git)
cd Proyecto_Titulo

# 2. Levantar los contenedores
docker-compose up --build
Opción 2: Ejecución Manual con Entorno Virtual
Clonar e ingresar al repositorio:

Bash
git clone [https://github.com/Felifhh/Proyecto_Titulo.git](https://github.com/Felifhh/Proyecto_Titulo.git)
cd Proyecto_Titulo
Crear y activar el entorno virtual:

Bash
# En Windows:
python -m venv venv
venv\Scripts\activate

# En Linux / macOS:
source venv/bin/activate
Instalar dependencias:

Bash
pip install -r requirements.txt
Configurar variables de entorno en archivo .env (credenciales de Supabase, Gemini y Webpay).

Ejecutar migraciones e iniciar el servidor:

Bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
Autor
Felipe Fuentes

Ingeniero en Informática — Duoc UC

Perfil de GitHub: https://github.com/Felifhh
