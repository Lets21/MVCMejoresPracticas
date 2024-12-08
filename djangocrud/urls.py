"""djangocrud URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from tasks import views

urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('tasks/', views.tasks, name='tasks'),

    path('tasks_completed/', views.tasks_completed, name='tasks_completed'),
    path('logout/', views.signout, name='logout'),
    path('signin/', views.signin, name='signin'),
    path('create_task/', views.create_task, name='create_task'),
    path('tasks/<int:task_id>', views.task_detail, name='task_detail'),
    path('taks/<int:task_id>/complete', views.complete_task, name='complete_task'),
    path('tasks/<int:task_id>/delete', views.delete_task, name='delete_task'),
    path('admin-panel/', views.vista_admin, name='vista_admin'),
    path('editar-paciente/<int:id>/', views.editar_paciente, name='editar_paciente'),
    path('eliminar-paciente/<int:id>/', views.eliminar_paciente, name='eliminar_paciente'),
    path('editar-doctor/<int:id>/', views.editar_doctor, name='editar_doctor'),
    path('eliminar-doctor/<int:id>/', views.eliminar_doctor, name='eliminar_doctor'),
    path('crear-paciente/', views.crear_paciente, name='crear_paciente'),
    path('crear-doctor/', views.crear_doctor, name='crear_doctor'),
    path('registro-paciente/', views.registro_paciente, name='registro_paciente'),
    path('registro-doctor/', views.registro_doctor, name='registro_doctor'),
    path('vista-doctor/', views.vista_doctor, name='vista_doctor'),
    path('vista-paciente/', views.vista_paciente, name='vista_paciente'),
    path('tratamientos/', views.lista_tratamientos, name='lista_tratamientos'),
    path('tratamientos/crear/', views.crear_tratamiento, name='crear_tratamiento'),
    path('tratamientos/editar/<int:id>/', views.editar_tratamiento, name='editar_tratamiento'),
    path('tratamientos/eliminar/<int:id>/', views.eliminar_tratamiento, name='eliminar_tratamiento'),
    path('asignar-tratamiento/<int:paciente_id>/', views.asignar_tratamiento_automatico, name='asignar_tratamiento'),
    path('actualizar-estado-tratamiento/<int:asignacion_id>/', 
            views.actualizar_estado_tratamiento, 
            name='actualizar_estado_tratamiento'),
    
    path('medicamentos/', views.lista_medicamentos, name='lista_medicamentos'),
    path('medicamentos/crear/', views.crear_medicamento, name='crear_medicamento'),
    path('medicamentos/editar/<int:medicamento_id>/', views.editar_medicamento, name='editar_medicamento'),
    path('medicamentos/eliminar/<int:id>/', views.eliminar_medicamento, name='eliminar_medicamento'),
    
    path('programar-cita/<int:doctor_id>/', views.programar_cita, name='programar_cita'),
    
    path('actualizar-estado-cita/<int:cita_id>/', views.actualizar_estado_cita, name='actualizar_estado_cita'),
    
    path('crear-tratamiento-paciente/<int:asignacion_id>/', 
        views.crear_tratamiento_paciente, 
        name='crear_tratamiento_paciente'),
    
]
