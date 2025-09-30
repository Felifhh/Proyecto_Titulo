# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Actividad(models.Model):
    id_actividad = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    fecha = models.DateField()
    cupos = models.IntegerField(blank=True, null=True)
    estado = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'actividad'


class Auditoria(models.Model):
    id_evento = models.AutoField(primary_key=True)
    id_vecino = models.ForeignKey('Vecino', models.DO_NOTHING, db_column='id_vecino', blank=True, null=True)
    accion = models.CharField(max_length=255)
    fecha_evento = models.DateTimeField(blank=True, null=True)
    resultado = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'auditoria'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class Certificado(models.Model):
    id_certificado = models.AutoField(primary_key=True)
    id_vecino = models.ForeignKey('Vecino', models.DO_NOTHING, db_column='id_vecino')
    tipo = models.CharField(max_length=10, blank=True, null=True)
    fecha_emision = models.DateTimeField(blank=True, null=True)
    folio = models.CharField(unique=True, max_length=50, blank=True, null=True)
    qr_code = models.CharField(max_length=255, blank=True, null=True)
    firma_digital = models.CharField(max_length=255, blank=True, null=True)
    estado = models.CharField(max_length=9, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'certificado'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Documento(models.Model):
    id_documento = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=200)
    tipo = models.CharField(max_length=10, blank=True, null=True)
    ruta_archivo = models.CharField(max_length=255, blank=True, null=True)
    version = models.IntegerField(blank=True, null=True)
    fecha_subida = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'documento'


class InscripcionActividad(models.Model):
    id_inscripcion = models.AutoField(primary_key=True)
    id_actividad = models.ForeignKey(Actividad, models.DO_NOTHING, db_column='id_actividad')
    id_vecino = models.ForeignKey('Vecino', models.DO_NOTHING, db_column='id_vecino')
    fecha_inscripcion = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'inscripcion_actividad'
        unique_together = (('id_actividad', 'id_vecino'),)


class Metricas(models.Model):
    id_metrica = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=200, blank=True, null=True)
    valor = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    fecha = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'metricas'


class Noticia(models.Model):
    id_noticia = models.AutoField(primary_key=True)
    id_autor = models.ForeignKey('Vecino', models.DO_NOTHING, db_column='id_autor')
    titulo = models.CharField(max_length=200)
    contenido = models.TextField(blank=True, null=True)
    fecha_publicacion = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'noticia'


class Proyecto(models.Model):
    id_proyecto = models.AutoField(primary_key=True)
    id_vecino = models.ForeignKey('Vecino', models.DO_NOTHING, db_column='id_vecino')
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    presupuesto = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    documento_adj = models.CharField(max_length=255, blank=True, null=True)
    fecha_postulacion = models.DateTimeField(blank=True, null=True)
    estado = models.CharField(max_length=11, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'proyecto'


class Reserva(models.Model):
    id_reserva = models.AutoField(primary_key=True)
    id_vecino = models.ForeignKey('Vecino', models.DO_NOTHING, db_column='id_vecino')
    espacio = models.CharField(max_length=100)
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    valor = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    moneda = models.CharField(max_length=3, blank=True, null=True)
    estado = models.CharField(max_length=10, blank=True, null=True)
    fecha_reserva = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'reserva'


class Rol(models.Model):
    id_rol = models.AutoField(primary_key=True)
    nombre = models.CharField(unique=True, max_length=50)

    class Meta:
        managed = False
        db_table = 'rol'


class Solicitud(models.Model):
    id_solicitud = models.AutoField(primary_key=True)
    id_vecino = models.ForeignKey('Vecino', models.DO_NOTHING, db_column='id_vecino')
    tipo = models.CharField(max_length=10, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    estado = models.CharField(max_length=10, blank=True, null=True)
    fecha_creacion = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'solicitud'


class Vecino(models.Model):
    id_vecino = models.AutoField(primary_key=True)
    run = models.CharField(unique=True, max_length=15)
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200, blank=True, null=True)
    correo = models.CharField(unique=True, max_length=100, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    fecha_registro = models.DateTimeField(blank=True, null=True)
    id_rol = models.ForeignKey(Rol, models.DO_NOTHING, db_column='id_rol')
    estado = models.CharField(max_length=9, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'vecino'
