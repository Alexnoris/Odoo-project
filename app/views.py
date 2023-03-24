import json
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
        # imagen = request.FILES['imagen']

        url = 'http://host.docker.internal:8069'
        db = 'anime_store'
        username = 'admin'
        password = '1234'

        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        uid = common.authenticate(db, username, password, {})
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

        if(id == ""):
            models.execute_kw(db, uid, password, 'product.product', 'create', [{
                'name': nombre,
                'description': descripcion,
                'list_price': float(precio),
            }])

            # id_insert = models.execute_kw(db, uid, password, 'product', 'name_get', [[id]])
            # models.execute_kw(db, uid, password, 'ir.attachment', 'create', [{
            #     'res_model': nombre,
            #     'name': descripcion,
            #     'res_id': float(precio),
            # }])

        else:
             models.execute_kw(db, uid, password,'product.product', 'write',[[int(id)], {
                 'name': nombre, 
                 'description': descripcion, 
                 'list_price': float(precio)
            }])

        return redirect('index')

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
    
    productos = models.execute_kw(db, uid, password, 'product.product', 'search_read', [[['id', '=', int(id)]]], {'fields': ['id','display_name', 'description', 'list_price']})

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

        return redirect('index')

    else:
        context = {}

        html_template = loader.get_template('home/index.html')
        return HttpResponse(html_template.render(context, request))