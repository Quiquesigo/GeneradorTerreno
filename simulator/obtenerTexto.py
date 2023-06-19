import numpy as np
import cv2
import os

def obtenerTextoConImagen(imagen):
    aux = 0
    auxY=0
    if(os.path.exists("map.txt")):
        os.remove("map.txt")

    def escribirTexto(linea,letra):
        if(os.path.exists("map.txt")):
            with open('map.txt','r') as file:
                file.seek(0)
                content=file.read()
                file.close()
            with open('map.txt','w') as f:
                f.seek(0)
                if linea:
                    f.write(content+letra)
                else:
                    f.write(content+"\n"+letra)
        else:
            with open('map.txt','w') as file:
                file.write(letra)
                
    def calcular_centro(contour,esY):
        m = cv2.moments(contour)
        if m["m00"] != 0:
            if esY:
                ratio = m["m01"] / m["m00"]
            else:
                ratio = m["m10"] / m["m00"]
        else:
            ratio = 0.0
        return ratio

    # Load image
    img = cv2.imread(imagen)

    # Define upper and lower bounds for vegetation detection
    upperbound = np.array([70, 255, 175])
    lowerbound = np.array([0, 0, 0])

    # Create mask for vegetation detection
    mask = cv2.inRange(img, lowerbound, upperbound)

    # Apply mask to original image
    masked_img = cv2.bitwise_and(img, img, mask=mask)

    # Convert image to grayscale and apply blur
    gray_img = cv2.cvtColor(masked_img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray_img, (19, 19), 0)

    # Apply Otsu threshold
    _, thr = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)


    # Encontrar contornos de las regiones blancas en la imagen
    contours, hierarchy = cv2.findContours(thr, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    contours = sorted(contours, key=lambda contour: (calcular_centro(contour,True),calcular_centro(contour,False)))
    i=0
    while i < len(contours)-1:
            contour = contours[i]
            next_contour = contours[i+1]

            y=calcular_centro(contours[i],True)
            next_y=calcular_centro(contours[i+1],True)
            x=calcular_centro(contours[i],False)
            next_x=calcular_centro(contours[i+1],False)
            if next_y - y < 50:
                # Ordenar por X
                if x > next_x:
                    contours[i], contours[i+1] = next_contour, contour
                    i=0
                else:
                    i += 1
            else:
                i += 1

    print("Arboles ordenados correctamente")

    for contour in contours:
        # Calcular el área del contorno
        area = cv2.contourArea(contour)
        
        # Si el área es mayor que el umbral mínimo, dibujar un cuadrado que encierra el contorno
        if area > 500 and area < 5000:
            # Calcular los momentos del contorno
            M = cv2.moments(contour)
            # Calcular el centro del contorno
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])

            # Imprimir el centro del contorno
            print("Centro: ({}, {})".format(cx, cy))

            x,y,w,h = cv2.boundingRect(contour)
            print("Objeto encontrado en ({}, {}), ancho = {}, alto = {} con el area de {}".format(x, y, w, h, area))
            aux += 1

            if (y-auxY>25):
                linea = False
            else:
                linea = True
            if area <= 700:
                letra = "B "
                cv2.rectangle(img, (x,y), (x+w,y+h), (0,0,0), 2) #Negro
            elif area <= 1200:
                letra = "C "
                cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2) #Azul
            elif area <= 1700:
                letra = "D "
                cv2.rectangle(img, (x,y), (x+w,y+h), (0,0,255), 2) #Rojo
            elif area <= 2100:
                letra = "E "
                cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2) #Verde
            elif area <= 2500:
                letra = "G "
                cv2.rectangle(img, (x,y), (x+w,y+h), (255,255,0), 2) #Azul Claro
            elif area <= 2900:
                letra = "H "
                cv2.rectangle(img, (x,y), (x+w,y+h), (255,255,255), 2) #Blanco
            elif area <= 3300:
                letra = "I "
                cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,255), 2) #Amarillo
            else:
                letra = "J "
                cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,255), 2) #Rosa
            escribirTexto(linea,letra)
            auxY = y

    # Show images
    cv2.imshow('satellite image', img)
    cv2.imshow('vegetation detection', masked_img)
    cv2.imshow('thresholded image', thr)
    print(aux)
    cv2.waitKey(0) 
    cv2.destroyAllWindows()
    return True