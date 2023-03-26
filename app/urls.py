from django.urls import path
from . import views

urlpatterns = [
    path('', views.indexCliente, name='index'),
    path('adminproductos', views.index, name='adminp'),
    path('guardar-producto/', views.guardarProducto, name='guardar_producto'),
    path('editar-producto/<int:id>/', views.editarProducto, name='editar_producto'),
    path('borrar-producto/<int:id>/', views.eliminarProducto, name='borrar_producto'),
    path('product/<int:id>', views.detalleProducto, name='detalle_producto')
]