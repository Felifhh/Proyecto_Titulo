from django.core.management.base import BaseCommand
from django.utils import timezone
from Proyecto.models import Proyecto, VotoProyecto
from Auditoria.models import Auditoria


class Command(BaseCommand):
    help = "Cierra automáticamente las votaciones expiradas"

    def handle(self, *args, **kwargs):
        try:
            ahora = timezone.now()

            expirados = Proyecto.objects.filter(
                estado="En Votación",
                fecha_fin_votacion__lt=ahora
            )

            cerrados = 0

            for proyecto in expirados:
                votos_a_favor = VotoProyecto.objects.filter(
                    id_proyecto=proyecto,
                    voto=True
                ).count()

                votos_en_contra = VotoProyecto.objects.filter(
                    id_proyecto=proyecto,
                    voto=False
                ).count()

                # Resultado final
                proyecto.estado_votacion = (
                    "Aprobado por Votación"
                    if votos_a_favor > votos_en_contra
                    else "Rechazado por Votación"
                )

                proyecto.estado = "Finalizado"
                proyecto.save()

                # Auditoría
                Auditoria.objects.create(
                    id_vecino=None,
                    accion=f"Cierre automático del proyecto '{proyecto.titulo}'",
                    resultado="Finalizado"
                )

                cerrados += 1

            # ✔ Solo imprime si cerró proyectos
            if cerrados > 0:
                self.stdout.write(self.style.SUCCESS(
                    f"✔ Cierre automático ejecutado. Proyectos cerrados: {cerrados}"
                ))

        except Exception as e:
            # ✔ Manejo de errores limpio
            self.stderr.write(self.style.ERROR(
                f"❌ Error en cierre automático: {str(e)}"
            ))
