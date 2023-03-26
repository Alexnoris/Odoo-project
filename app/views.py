import json, base64, io
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from django import template
import xmlrpc.client


def index(request):

    context = {}

    url = 'http://host.docker.internal:8069'
    db = 'anime_store'
    username = 'admin'
    password = '1234'

    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
    
    uid = common.authenticate(db, username, password, {})

    models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
    products = models.execute_kw(db, uid, password, 'product.product', 'search_read', [], {'fields': []})
    
    if uid:
        print('Se conectó correctamente')
    else:
        print('No se pudo conectar')
    
    try:
        html_template = loader.get_template('home/index.html')

        context['products'] = products

        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))
    
def guardarProducto(request):

    if request.method == 'POST':
        id = request.POST['id']
        nombre = request.POST['nombre']
        descripcion = request.POST['descripcion']
        precio = request.POST['precio']
        stock = request.POST['stock']

        url = 'http://host.docker.internal:8069'
        db = 'anime_store'
        username = 'admin'
        password = '1234'

        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

        if(id == ""):
            imagen = request.FILES['imagen']
            # Modelo productos
            inserted_id = models.execute_kw(db, uid, password, 'product.product', 'create', [{
                'name': nombre,
                'description': descripcion,
                'list_price': float(precio),
                'qty_available': float(stock),
            }])            

            datos = base64.b64encode(imagen.read()).decode('utf-8')

            # Modelo imagen
            models.execute_kw(db, uid, password, 'ir.attachment', 'create', [{
                'name': 'image_128',
                'res_model': 'product.template',
                'res_id': int(inserted_id),
                'res_field': 'image_128',
                'type' : 'binary',
                'mimetype' : 'image/png',
                'store_fname' : imagen.name,
                'url': datos,                      
                'public': True,                      
                'datas': datos
            }])

            # Crea un movimiento de inventario
            # move_id = models.execute_kw(db, uid, password, 'stock.move', 'create', [{
            #     'name': nombre,
            #     'product_id': inserted_id,
            #     'product_uom_qty': float(stock),
            #     'product_uom': 1,
            #     'location_id': 8,
            #     'reference': 'WH/OUT/00001',
            #     'location_dest_id': 8,
            #     'state': 'confirmed',
            # }])

            # move = models.execute_kw(db, uid, password, 'stock.move', 'search_read', [[['id', '=', move_id]]], {'fields': ['picking_id']})

            # line_id = models.execute_kw(db, uid, password, 'stock.move.line', 'create', [{
            #     'move_id': move_id,
            #     'product_id': inserted_id,
            #     'product_uom_qty': float(stock),
            #     'product_uom_id': 1,
            #     'location_id': 8,
            #     'location_dest_id': 8,
            #     'lot_id': 8,  # ID del lote a asociar con esta línea de movimiento
            # }])

            # models.execute_kw(db, uid, password, 'stock.move.line', 'write', [[line_id], {'qty_done': float(stock)}])

        else:
            # Modelo productos
            inserted_id = models.execute_kw(db, uid, password,'product.product', 'write',[[int(id)], {
                'name': nombre, 
                'description': descripcion, 
                'list_price': float(precio)
            }])
            # Modelo para el stock
            # models.execute_kw(db, uid, password, 'stock.move', 'write', [[['product_id', '=', inserted_id]]], {
            #     'quantity': stock,
            #     'available_quantity': stock,
            #     'inventory_quantity': stock,
            # })
            # fields = models.execute_kw(db, uid, password, 'stock.quant', 'fields_get', [], {})
            # print(fields)

        return redirect('adminp')

    else:
        context = {}
        html_template = loader.get_template('home/index.html')
        return HttpResponse(html_template.render(context, request))
    
def editarProducto(request, id):
  if request.method == 'GET':

    context = {}

    url = 'http://host.docker.internal:8069'
    db = 'anime_store'
    username = 'admin'
    password = '1234'

    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
    uid = common.authenticate(db, username, password, {})
    models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
    
    productos = models.execute_kw(db, uid, password, 'product.product', 'search_read', [[['id', '=', int(id)]]], {'fields': ['id','display_name', 'description', 'list_price', 'qty_available']})
    
    productos_json = json.dumps(productos[0])
    
    return HttpResponse(productos_json, content_type='application/json')

  else:
    context = {}
    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))

def eliminarProducto(request, id):
    if request.method == 'GET':

        url = 'http://host.docker.internal:8069'
        db = 'anime_store'
        username = 'admin'
        password = '1234'

        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        
        models.execute_kw(db, uid, password, 'product.product', 'unlink', [[id]])

        return redirect('adminp')

    else:
        context = {}

        html_template = loader.get_template('home/index.html')
        return HttpResponse(html_template.render(context, request))

def indexCliente(request):

    context = {}

    url = 'http://host.docker.internal:8069'
    db = 'anime_store'
    username = 'admin'
    password = '1234'

    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
    
    uid = common.authenticate(db, username, password, {})

    models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
    products = models.execute_kw(db, uid, password, 'product.product', 'search_read', [], {'fields': []})

    if uid:
        print('Se conectó correctamente')
    else:
        print('No se pudo conectar')
    
    try:
        html_template = loader.get_template('home/index-cliente.html')

        context['products'] = products

        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))

def detalleProducto(request, id):

    context = {}

    url = 'http://host.docker.internal:8069/'
    db = 'anime_store'
    username = 'admin'
    password = '1234'

    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
    uid = common.authenticate(db, username, password, {})
    models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

    productos = models.execute_kw(db, uid, password, 'product.product', 'search_read', [[['id', '=', int(id)]]], {'fields': ['id','display_name', 'description', 'list_price', 'qty_available']})

    try:
        html_template = loader.get_template('home/detalle-producto.html')

        context['product'] = productos[0]

        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))