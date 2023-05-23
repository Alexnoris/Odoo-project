import json, base64, io
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from django import template
import xmlrpc.client

import requests
from .models import StockQuant


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
        html_template = loader.get_template('home/index-prestashop.html')
        # html_template = loader.get_template('home/index.html')

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

        # Moficar product template tambien para insertar el onHand

        url = 'http://host.docker.internal:8069'
        db = 'anime_store'
        username = 'admin'
        password = '03b30084b45b3b8dcaffce3835b7ad31e902b49e'

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

            # create_stock_quant(inserted_id, 8, float(stock))
            stock_quant = StockQuant(product_id=inserted_id, location_id=8,quantity=stock)
            stock_quant.save()

        else:
            # Modelo productos
            inserted_id = models.execute_kw(db, uid, password,'product.product', 'write',[[int(id)], {
                'name': nombre, 
                'description': descripcion, 
                'list_price': float(precio)
            }])

        return redirect('adminp')

    else:
        context = {}
        html_template = loader.get_template('home/index.html')
        return HttpResponse(html_template.render(context, request))
    
def guardarPrestashop(request):

    if request.method == 'POST':
        id = request.POST['id']
        nombre = request.POST['nombre']
        descripcion = request.POST['descripcion']
        precio = request.POST['precio']
        stock = request.POST['stock']
        img = request.POST['imagen']

        secure_key = "2FISCKE65YG6MGT3FVV8BMXH8LQ4BUUD"
        url = f"http://host.docker.internal:8081/admin7272sw0hk5eyvkzhssy/create-product.php?secure_key={secure_key}"

        product_data = {
            'ean13': id,
            'reference': nombre,
            'name': nombre,
            'quantity': stock,
            'description': descripcion,
            'features': [
                {"name": "Color", "value": "Grey"},
                {"name": "Height", "value": "40cm"},
            ],
            'price': precio,
            'image_url': img,
            'default_category': 1,
            'categories': [1, 5]
        }

        response = requests.post(url, data=product_data)

        if response.status_code == 200:
            return redirect('adminp')
        else:
            return HttpResponse("Error al guardar el producto")


        # return redirect('adminp')

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
  

def create_stock_quant(product_id, location_id, quantity):
    url = 'http://host.docker.internal:8069'
    db = 'anime_store'
    username = 'admin'
    password = '1234'

    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
    uid = common.authenticate(db, username, password, {})
    models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

    stock_quant_data = {
        'product_id': product_id,
        'location_id': location_id,
        'quantity': quantity,
    }
    stock_quant_id = models.execute_kw(
        db, uid, password, 'stock.quant', 'create', [stock_quant_data]
    )

    return stock_quant_id

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

    url = 'http://host.docker.internal:8069'
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