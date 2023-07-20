import os
import json
import re
import cv2
from datetime import datetime
from PIL import Image, ImageTk
import numpy as np
import webbrowser
import folium
import subprocess
import tkinter as tk
import threading
import requests
from pyproj import CRS, Transformer

from obtenerTexto import obtenerTextoConImagen
from image_downloading import download_image

file_dir = os.path.dirname(__file__)
prefs_path = os.path.join(file_dir, 'preferences.json')
default_prefs = {
        'url': 'https://mt.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
        'url2': 'https://a.tile-cyclosm.openstreetmap.fr/cyclosm/{z}/{x}/{y}.png',
        'tile_size': 256,
        'tile_format': 'jpg',
        'dir': os.path.join(file_dir, 'images'),
        'headers': {
            'cache-control': 'max-age=0',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36'
        },
        'tl': '',
        'br': '',
        'zoom': ''
    }

'''
def take_input(messages):
    inputs = []
    print('Introduce r para resetear o q para salir.')
    for message in messages:
        inp = input(message)
        if inp == 'q' or inp == 'Q':
            return None
        if inp == 'r' or inp == 'R':
            return take_input(messages)
        inputs.append(inp)
    return inputs
'''

def run(cord1,cord2):
    with open(os.path.join(file_dir, 'preferences.json'), 'r', encoding='utf-8') as f:
        prefs = json.loads(f.read())

    if not os.path.isdir(prefs['dir']):
        os.mkdir(prefs['dir'])

    lat1, lon1 = re.findall(r'[+-]?\d*\.\d+|d+', cord1)
    lat2, lon2 = re.findall(r'[+-]?\d*\.\d+|d+', cord2)
    print("Has elegido las coordenadas siguientes:\nEsquina superior izquierda: ("+ lat1 + ", " + lon1 + ")\nEsquina inferior derecha: ("+lat2+", "+lon2+")")

    zoom = 21
    lat1 = float(lat1)
    lon1 = float(lon1)
    lat2 = float(lat2)
    lon2 = float(lon2)

    if prefs['tile_format'].lower() == 'png':
        channels = 4
    else:
        channels = 3

    img = download_image(lat1, lon1, lat2, lon2, zoom, prefs['url'],
        prefs['headers'], prefs['tile_size'], channels)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    name = f'img_{timestamp}.png'
    if(cv2.imwrite(name, img)):
        print("Se ha creado la imagen correctamente con el nombre de "+name)
    if(obtenerTextoConImagen(name)):

        ventana2 = tk.Tk()
        canvas = tk.Canvas(ventana2, width=1300, height=1000)
        canvas.pack()
        line = canvas.create_line(305, 0, 305, 1000, width=2, fill='black')
        ventana2.title("Visualización de la imagen")
        ventana2.geometry("1300x1000")
        imagenColor = Image.open('colores.png')
        imagenColor = reducir_imagen(imagenColor)
        fotoColor = ImageTk.PhotoImage(imagenColor)
        labelColor = tk.Label(ventana2, image=fotoColor)
        labelColor.place(x=870,y=520)
        imagenFiltro = Image.open('filtro.png')
        imagenFiltro = reducir_imagen(imagenFiltro)
        fotoFiltro = ImageTk.PhotoImage(imagenFiltro)
        labelFiltro = tk.Label(ventana2, image=fotoFiltro)
        labelFiltro.place(x=870,y=120)
        imagenOtsu = Image.open('otsu.png')
        imagenOtsu = reducir_imagen(imagenOtsu)
        fotoOtsu = ImageTk.PhotoImage(imagenOtsu)
        labelOtsu = tk.Label(ventana2, image=fotoOtsu)
        labelOtsu.place(x=410,y=520)
        imagenOrig = Image.open(name)
        imagenOrig = reducir_imagen(imagenOrig)
        fotoOrig = ImageTk.PhotoImage(imagenOrig)
        labelOrig = tk.Label(ventana2, image=fotoOrig)
        labelOrig.place(x=410,y=120)
        generar_terreno_parametro = lambda: generar_terreno(ventana2)
        obtener_imagen_parametro = lambda: obtener_imagen2(entrada_esquina_superior_derecha2,entrada_esquina_inferior_derecha2,ventana2)
        importar_terreno_parametro = lambda: importar_terreno(lat1,lon1,ventana2)
        boton_generar_terreno = tk.Button(ventana2, text="Generar terreno virtual", command=generar_terreno_parametro)
        boton_generar_terreno.place(x=740,y=880)
        boton_Imagen= tk.Button(ventana2, text="Obtener imagen", command=obtener_imagen_parametro)
        boton_Imagen.place(x=90,y=240)
        boton_ImportarTerreno = tk.Button(ventana2, text="Importar terreno real", command=importar_terreno_parametro)
        boton_ImportarTerreno.place(x=740,y=840)

        label_esquina_superior_derecha = tk.Label(ventana2, text="Esquina superior izquierda")
        label_esquina_superior_derecha.place(x=75,y=120)
        entrada_esquina_superior_derecha2 = tk.Entry(ventana2)
        entrada_esquina_superior_derecha2.place(x=80,y=150)

        label_esquina_inferior_derecha = tk.Label(ventana2, text="Esquina inferior derecha")
        label_esquina_inferior_derecha.place(x=75,y=180)
        entrada_esquina_inferior_derecha2 = tk.Entry(ventana2)
        entrada_esquina_inferior_derecha2.place(x=80,y=210)

        label_imgEncontrada = tk.Label(ventana2, text="Imagen encontrada correctamente")
        label_imgEncontrada.place(x=700,y=50)
        label_titOtra = tk.Label(ventana2, text="Introduce otras coordenadas si la imagen\n no es correcta")
        label_titOtra.place(x=40,y=50)

        label_imgOrig = tk.Label(ventana2, text="Imagen original")
        label_imgOrig.place(x=510,y=90)
        label_imgFiltro = tk.Label(ventana2, text="Imagen con filtro aplicado")
        label_imgFiltro.place(x=950,y=90)
        label_imgOtsu = tk.Label(ventana2, text="Imagen con umbralización de Otsu")
        label_imgOtsu.place(x=470,y=490)
        label_imgColor = tk.Label(ventana2, text="Imagen con los árboles detectados")
        label_imgColor.place(x=930,y=490)


        ventana2.mainloop()

def reducir_imagen(imag):
    width, height = imag.size
    new_height = int(300 * (height / width))
    imagenNueva = imag.resize((300, new_height))
    return imagenNueva

def ejecutar_HC():
    subprocess.call('HC2014.exe')

def importar_terreno(lat1,lon1,ventana):
    url = "http://centrodedescargas.cnig.es/CentroDescargas/index.jsp"
    response = requests.get(url)
    if response.status_code == 200:
        webbrowser.open(url)

    crs_wgs84 = CRS.from_string("EPSG:4326")
    crs_utm = CRS.from_string("EPSG:32730")
    transformer = Transformer.from_crs(crs_wgs84, crs_utm, always_xy=True)
    utm_easting, utm_northing = transformer.transform(lon1, lat1)
    utm_northing -= 10000000
    utm_easting2 = utm_easting + 100
    utm_northing2 = utm_northing - 100
    titulo_ventana3 = tk.Label(ventana, text="Introduce las siguientes coordenadas \nen la aplicación HeightmapCreator\n\nUpper Left X:     " + str(int(utm_easting)) + "\nUpper Left Y:    " + str(int(utm_northing)) + "\nUpper Right X:    " + str(int(utm_easting2)) + "\nUpper Right Y:   " + str(int(utm_northing2)) + "\n\nAcuerdese de obtener el modelo\n correspondiente de la página web abierta")
    titulo_ventana3.place(x=40,y=700)
    proceso_thread = threading.Thread(target=ejecutar_HC)
    proceso_thread.start()
    ventana.mainloop()



def comprobar_preferencias(cord1,cord2):
    if os.path.isfile(prefs_path):
        run(cord1,cord2)
    else:
        with open(prefs_path, 'w', encoding='utf-8') as f:
            json.dump(default_prefs, f, indent=2, ensure_ascii=False)

        print(f'Preferencias creadas en la carpeta {prefs_path}\n Ejecute de nuevo el código para poner en marcha la aplicación')

def obtener_imagen():
    esq_sup_izq = entrada_esquina_superior_derecha.get()
    esq_inf_der = entrada_esquina_inferior_derecha.get()
    ventana.destroy()
    comprobar_preferencias(esq_sup_izq,esq_inf_der)

def obtener_imagen2(ent1,ent2,venti):
    esq_sup_izq1 = ent1.get()
    esq_inf_der1 = ent2.get()
    venti.destroy()
    run(esq_sup_izq1,esq_inf_der1)
    
def generar_terreno(ventanas):
    ventanas.destroy()
    subprocess.call('five.exe')

def comprobar_entradas():
    esquina_superior_derecha = entrada_esquina_superior_derecha.get()
    esquina_inferior_derecha = entrada_esquina_inferior_derecha.get()
    if esquina_superior_derecha and esquina_inferior_derecha:
        boton_obtener_imagen.config(state='normal')
    else:
        boton_obtener_imagen.config(state='disabled')

def obtener_coordenadas():
    url = "https://www.google.com/maps/@39.9943545,-3.8067684,7z"
    response = requests.get(url)

    if response.status_code == 200:
        webbrowser.open(url)

def cerrar_ventana():
    ventana1.destroy()

if os.path.isfile(prefs_path):
    # Crear ventana
    ventana = tk.Tk()
    ventana.title("Ingresa las coordenadas")
    ventana.geometry("340x160")

    # Crear labels e inputs
    label_titulo = tk.Label(ventana, text="INTRODUCE LAS COORDENADAS")
    label_titulo2 = tk.Label(ventana, text="Hazlo con el siguiente formato: latitud,longitud")
    label_titulo.pack()
    label_titulo2.pack()
    label_esquina_superior_derecha = tk.Label(ventana, text="Esquina superior izquierda")
    label_esquina_superior_derecha.pack()
    entrada_esquina_superior_derecha = tk.Entry(ventana)
    entrada_esquina_superior_derecha.pack()
    entrada_esquina_superior_derecha.bind('<KeyRelease>', lambda event: comprobar_entradas())

    label_esquina_inferior_derecha = tk.Label(ventana, text="Esquina inferior derecha")
    label_esquina_inferior_derecha.pack()
    entrada_esquina_inferior_derecha = tk.Entry(ventana)
    entrada_esquina_inferior_derecha.pack()
    entrada_esquina_inferior_derecha.bind('<KeyRelease>', lambda event: comprobar_entradas())

    # Crear botón
    boton_obtener_imagen = tk.Button(ventana, text="Obtener imagen", command=obtener_imagen, state='disabled')
    boton_obtener_imagen.pack()
    '''
    boton_coordenadas = tk.Button(ventana, text="Ir a Google Maps", command=obtener_coordenadas)
    boton_coordenadas.pack()'''

    m = folium.Map(location= [39.4699, -0.3763], zoom_start=8)
    folium.TileLayer(tiles='https://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
                    attr='Google',
                    name='Google Satellite',
                    max_zoom=20,
                    subdomains=['mt0', 'mt1', 'mt2', 'mt3']).add_to(m)
    m.add_child(folium.ClickForMarker(popup= None))
    m.save('mapa.html')
    webbrowser.open_new_tab('mapa.html')
    ventana.mainloop()
else:
    with open(prefs_path, 'w', encoding='utf-8') as f:
        json.dump(default_prefs, f, indent=2, ensure_ascii=False)
    ventana1 = tk.Tk()
    ventana1.title("Archivo de preferencias creado")
    ventana1.geometry("340x80")
    label_titulo1 = tk.Label(ventana1, text="Se ha creado el archivo de preferencias.\n Ejecute de nuevo el código para poner en marcha la aplicación")
    boton_cerrar = tk.Button(ventana1, text="Cerrar", command=cerrar_ventana)
    label_titulo1.pack()
    boton_cerrar.pack()
    ventana1.mainloop()





