import os
import json
import re
import cv2
from datetime import datetime
from PIL import Image
import numpy as np
import cv2
import webbrowser
import folium
import subprocess

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
        subprocess.call('five.exe')

def comprobar_preferencias(cord1,cord2):
    if os.path.isfile(prefs_path):
        run(cord1,cord2)
    else:
        with open(prefs_path, 'w', encoding='utf-8') as f:
            json.dump(default_prefs, f, indent=2, ensure_ascii=False)

        print(f'Preferencias creadas en la carpeta {prefs_path}\n Ejecute de nuevo el código para poner en marcha la aplicación')

import tkinter as tk

def obtener_imagen():
    esq_sup_izq = entrada_esquina_superior_derecha.get()
    esq_inf_der = entrada_esquina_inferior_derecha.get()
    comprobar_preferencias(esq_sup_izq,esq_inf_der)
    ventana.destroy()
    

def comprobar_entradas():
    esquina_superior_derecha = entrada_esquina_superior_derecha.get()
    esquina_inferior_derecha = entrada_esquina_inferior_derecha.get()
    if esquina_superior_derecha and esquina_inferior_derecha:
        boton_obtener_imagen.config(state='normal')
    else:
        boton_obtener_imagen.config(state='disabled')

def obtener_coordenadas():
    import requests
    import webbrowser

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





