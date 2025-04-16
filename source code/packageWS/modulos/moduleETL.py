'''
Módulo que se encarga de toda la actividad de la ETL
'''
from packageWS.auxiliar import etlAux as aux 
from packageWS.auxiliar import transformardtAux as tdt
import pandas as pd
from bs4 import BeautifulSoup
from urllib.request import HTTPError
import os
import time
from datetime import datetime

#from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException #,NoSuchElementException
from selenium.webdriver.chrome.options import Options
#Allow concurrent to selenium
from concurrent.futures import ThreadPoolExecutor


# --- PRINCIPAL MODULE --- #
def runETL(direcciones,loteSize=5,sleepTime=5):
    
    with ThreadPoolExecutor(max_workers=loteSize) as executor:
        
        #split in lotes
        for i in range(0,len(direcciones),loteSize):
            
            lote = direcciones[i:i + loteSize]
            executor.map(ejecutarETL,lote) ### <-- CORE
            #executor.map(print,lote)
            
            #If is the last lote, don't wait
            if (i+loteSize < len(direcciones)):
                time.sleep(sleepTime)
                

##============ CORE OF THE MODULE ============##
def ejecutarETL(listado,retry=0):

    #Comprueba si no se ha intentado 3 veces seguidos
    if retry >= 3:
        print("Se ha reintentado más de 3 veces, se cancela ejecución")
        exit()
    
    
    try:
        
        #Declare elements of the list
        url,carta = listado
        
        #Parámetros para Selenium
        opts = Options()
        #Añaidr el agente para evitar problemas
        opts.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36") #For 
        opts.add_argument("--headless") #Disable browser window
        opts.add_argument("--disable-search-engine-choice-screen")
        
        #Añadiendo Selenium
        driver = webdriver.Chrome(options=opts)
        driver.get(url)
        #Declarar el botón de "Cargar más"
        XpathBoton = '//button[@id="loadMoreButton"]'
        
        #Con selenium, se va a automatizar el botón de "mostrar mas" para obtener todos los registros que permita la página (max 500)
        #Se realizará un bucle para que dé a ese botón mientras exista (sea visible)
        if(aux.check_exists_by_xpath(driver,XpathBoton)):
            while driver.find_element(By.XPATH,XpathBoton).is_displayed():
                
                #WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH,'//button[@id="loadMoreButton"]')))
                botonMas = driver.find_element(By.XPATH, XpathBoton)
                
                #Pulsar el botón
                driver.execute_script("arguments[0].click();", botonMas)
                
                #Reposar 3 segundos para asegurar que la página cargue bien
                time.sleep(3)
            
        
        #Una vez obtenida la página con la máxima información, se aplica el BS para obtener todo el registro
        soup = BeautifulSoup(driver.page_source,'html.parser')
        #print(soup.prettify())
        
        #Listado que se llenará con cada oferta disponible
        ofertas = []
    
        ##Obtención de la gráfica
        contenedor_grafico = soup.find('div',{'class':'tab-content'})
        datos_grafico = contenedor_grafico.find('script',{'class':'chart-init-script'})
        
        #Extraer los valores del script para tener el dccionario de los valores
        grafico = aux.obtenerGrafico(datos_grafico)
        #print(grafico)
        ##Obtención de la cabecera
        datos_header = contenedor_grafico.find('div',{'class':'row g-0 small justify-content-center'})
    
        #Extraer los valores del header
        headers = []
        header = aux.obtenerHeader(datos_header)
        headers.append(header)
        #print(headers)
    
        ##Parte de la tabla de ofertas -----------------------
    
        #Bucle que recorrerá cada uno de los elemntos
        for i in soup.find_all('div',{'class':'row g-0 article-row'}):
            
            #Obtener el identificador de la fila de la tabla de ofertas
            idOferta = i.get('id')
            #print(idOferta)
        
            #Recorreremos el contenido de la venta (que es la parte donde está toda la información importante)
            contenedor_oferta = i.find('div',{'class':'col-sellerProductInfo col'})
            #print(contenedor_oferta)
            datos_vendedor = contenedor_oferta.find('div',{'class':'col-seller col-12 col-lg-auto'})
            #print(datos_vendedor)
            datos_carta = contenedor_oferta.find('div',{'class':'col-product col-12 col-lg'})
            #print(datos_carta)
        
            ventas,stock = aux.obtenerVentasStock(datos_vendedor)
            #print(str(ventas) + ' | '+ str(stock))
            pais = aux.obtenerLugarVendedor(datos_vendedor)
            #print(pais)
            nick = aux.obtenerNombreVendedor(datos_vendedor)
            #print(nick)
            tipoVendedor = aux.obtenerTipoVendedor(datos_vendedor)
            #print(tipoVendedor)
            quality = aux.obtenerCalidadCarta(datos_carta)
            #print(quality)
            language = aux.obtenerIdiomaCarta(datos_carta)
            #print(language)
            hayIconoEsp = aux.comprobarIconoEspecial(datos_carta)
            #print(hayIconoEsp)
            iconoEsp = aux.obtenerIconoEspecial(datos_carta)
            #print(iconoEsp)
            hayFoto = aux.comprobarFoto(datos_carta)
            #print(hayFoto)
            hayComentario = aux.comprobarComentario(datos_carta)
            #print(hayComentario)
            comentario = aux.obtenerComentario(datos_carta)
            #print(comentario)
            quantity = aux.obtenerCantidadDisponible(datos_carta)
            #print(quantity)
            precio,moneda = aux.obtenerPrecio(datos_carta)
            #print(str(precio) + ' | '+ str(moneda))
        
            #Fecha de Recolección de fecha
            finiOferta = datetime.today().strftime('%Y-%m-%d')
            #print(datetime.today().strftime('%Y-%m-%d'))
            
            ##Una vez obtenido todos los campos importantes, se van a tener que almacenar dentro de una variable
        
            #Creación del listado de la oferta
            oferta = []
            #oferta.extend([str(i),nick,pais,tipoVendedor,ventas,stock,language,quality,hayFoto,hayComentario,quantity,precio,moneda])
            oferta = [str(idOferta),nick,pais,tipoVendedor,ventas,stock,language,quality,hayIconoEsp,iconoEsp,hayFoto,hayComentario,comentario,quantity,precio,moneda,finiOferta,'']
        
            # Añadirlo al listado de las ofertas la oferta
            ofertas.append(oferta)
            
        #Crear los dataFrame a partir de los campos
        dtOfertas = pd.DataFrame(ofertas,columns=['idOferta','nick','pais','tipoVendedor','ventas','stock','language','quality','hayIconoEsp','iconoEsp','hayFoto','hayComentario','comentario','quantity','precio','moneda','finiOferta','ffinOferta'])
        #print(dtOfertas)
    
        dtHistorial = pd.DataFrame(grafico.items(),columns=['fecha','pormedioVenta'])
        #print(dtHistorial)
        
        dtCard = pd.DataFrame(headers,columns=['Photo','Expansion','Rarity'])
        #print(dtCard)
    
        #Obtener la ruta de la carpeta donde se guardará las carpetas
        pathOfertas = os.getcwd() + '\csv\ofertas'
        pathVentas  = os.getcwd() + '\csv\historialVentas'
        pathCards   = os.getcwd() + '\csv\cards'
    
        #Nombre de los csv
        nombrecsvOfertas = 'ofertas_' + carta + '.csv'
        nombrecsvHVentas = 'historialVentas_' + carta + '.csv'
        nombrecsvCards   = 'card_' + carta + '.csv'
    
        #Dirección del archivo a crear
        archivoOfertas   = os.path.join(pathOfertas,nombrecsvOfertas)
        archivoHistorial = os.path.join(pathVentas,nombrecsvHVentas)
        archivoCards     = os.path.join(pathCards,nombrecsvCards)
    
        #Creará o actualizará el documento de Ofertas en función de si el archivo ya existía
        if os.path.exists(archivoOfertas):
            #En el caso en el que el fichero no exista, se tiene que unificar y actualizar los datos cambiados
            print("El archivo " + nombrecsvOfertas + " ya existe. Actualizando... ", end="")
            historialOfertas = pd.read_csv(archivoOfertas,sep=';',decimal=',')
            
            #Actualizar
            dtFinal = tdt.ActualizarOfertas(historialOfertas,dtOfertas,finiOferta)
            dtFinal.to_csv(archivoOfertas,index=False,header=True,sep=';',decimal=',',encoding="utf_8_sig")
            print("Actualizado")

        else:
            #Crear los csv
            print("Creación del archivo " + nombrecsvOfertas)
            dtOfertas.to_csv(archivoOfertas,index=False,header=True,sep=';',decimal=',',encoding="utf_8_sig")
        
        
        #Creará o actualizará el documento de historial de Ventas en función de si el archivo ya existída
        if os.path.exists(archivoHistorial):
            #En el caso en el que el fichero no exista, se tiene que unificar y actualizar los datos cambiados
            print("El archivo " + nombrecsvHVentas + " ya existe. Actualizando... ", end="")
            historialVentas = pd.read_csv(archivoHistorial,sep=';',decimal=',')

            #Actualizar
            dtFinal = tdt.limpiarVentas(historialVentas,dtHistorial)
            #Crear nuevo csv con los datos actualizados
            dtFinal.to_csv(archivoHistorial,index=False,header=True,sep=';',decimal=',',encoding="utf_8_sig")  
            print("Actualizado")
            
        else:
            #Crear los csv
            print("Creación del archivo " + nombrecsvHVentas)
            dtHistorial.to_csv(archivoHistorial,index=False,header=True,sep=';',decimal=',',encoding="utf_8_sig") 
            
        #Creará (no hace falta actualizar) los datos genéricos de una carta
        if os.path.exists(archivoCards):
            #En el caso en el que exista, no hace falta hacer nada
            print("El archivo " + nombrecsvCards + " ya existe. No hace falta crear el fichero")

            
        else:
            #Crear los csv
            print("Creación del archivo " + nombrecsvCards)
            dtCard.to_csv(archivoCards,index=False,header=True,sep=';',decimal=',',encoding="utf_8_sig")    
        
    except HTTPError as err:
        
        retry+=1
        print('intento nº: ' + str(retry) + ' por el error: ' + str(err))
        #Esperar 10 segundos antes de volver a intentar
        time.sleep(10)
        ejecutarETL(url,carta,retry)
    
    except TimeoutException as err:
        
        retry+=1
        print('intento nº: ' + str(retry) + ' por el error: ' + str(err))
        #Esperar 10 segundos antes de volver a intentar
        time.sleep(10)
        ejecutarETL(url,carta,retry)
