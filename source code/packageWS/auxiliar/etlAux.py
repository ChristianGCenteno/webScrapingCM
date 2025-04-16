'''
Funciones y Procedimientos utilizados en el moduleETL para ayudar con la limpieza de los datos extraidos
'''
import re
import unicodedata
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

##============DEFINICIÓN FUN Y PRO LIMPIAS ============##

''' Función que obtiene el valor de las ventas confirmadas del vendedor '''
def limpiarVentas (Sales):
    
    auxSales = Sales[0].strip()
    auxSales = auxSales.replace(' Sales','')
    return auxSales

''' Función que obtiene el valor del stock actual del vendedor '''
def limpiarStock (Available):
    
    auxAva = Available[1].strip()
    auxAva = auxAva.replace(' Available items','')
    return auxAva

''' Función que obtiene el valor del pais del Vendedor '''
def limpiarPais (Pais):
    
    auxPais = Pais.replace('Item location: ','')
    return auxPais

''' Función que obtiene el precio en formato float '''
def limpiarPrecio (precioMoneda):
    
    auxPrecio = precioMoneda[0]
    
    #Quitar el punto de miles poner el de decimal
    precio = auxPrecio.replace('.','')
    precio = precio.replace(',','.')
    
    #Otros método más enrevesado
    #precio = auxPrecio[auxPrecio.find(','):].replace(',','.')
    #precio = auxPrecio[:auxPrecio.find(',')].replace('.','')

    #Devolver el precio en formato float con 2 decimales
    return float("{:.2f}".format(float(precio)))

''' Función que obtiene la moneda del precio en fomrato str '''
def limpiarMoneda (precioMoneda):
    
    moneda = precioMoneda[1]
    return str(moneda)

''' Función que obtiene la url del icono de la expansión '''
def limpiarUrlIco (style):
    
    print(str(style).strip())
    url = re.findall(r"url\(['\"]?(.*?)['\"]?\)", str(style).strip())
    
    return url

##============DEFINICIÓN FUN Y PRO AUX ============##

''' A partir del script que se usa para pintar el gráfico, se obtendrá el diccionario con la relación fecha:valor '''
# -- ASOCIADO AL GRÁFICO DE VENTAS
def obtenerGrafico (contenedor):
    
    #declaracion del diccionario
    parametros    = str(contenedor.get_text().strip().split(';'))

    # Aplicando Regex obtenemos el contenido de los corchetes que nos interese
    dates         = re.findall(r'"labels":\[(.*?)\]', parametros)
    prices        = re.findall(r'"data":\[(.*?)\]', parametros)
    
    # Convertir las fechas en listados de string
    dates_list    = list(map(str, dates[0].replace('"','').split(',')))
    
    # Convertir el string de los precios en una lista de números flotantes
    prices_list   = list(map(float, prices[0].split(',')))
    
    # Declaración del diccionario donde irá los datos de las gráficas
    graficas = {}
    # Bucle para recorrer a la vez ambos listados
    for k in dates_list:
        graficas[k] = prices_list[dates_list.index(k)]
    
    return graficas

# -- ASOCIADO AL HEADER
def obtenerHeader (contenedor):
    
    #declaracion del diccionario
    auxImg = contenedor.find('img',{'class':'is-front'})
    auxTab = contenedor.find('dl',{'class':'labeled row mx-auto g-0'})
    auxRar = auxTab.find('svg')
    auxExp = auxTab.find('a',{'class':'expansion-symbol is-pokemon icon is-24x24'})
    #auxEIc = auxExp.find('span')
    
    img    = auxImg.get('src')
    Rar    = auxRar.get('data-bs-original-title')
    Exp    = auxExp.get('data-bs-original-title')
    #ExpIco = limpiarUrlIco(auxEIc.get('style'))
    
    return str(img),str(Exp),str(Rar)

# -- ASOCIADO A DATOS DE VENDEDOR

''' Devuelve los valores de ventas y stock de los vendedores '''
def obtenerVentasStock (contenedor):
    
    #Obtención del fragmento span donde se encuentra el dato
    auxDisponibilidad = contenedor.find('span',{'class':'badge text-bg-faded d-none d-sm-inline-flex has-content-centered me-1 sell-count'})
    
    #Recuperación del valor de interes
    # Versión sin selenium
    #auxDisponibilidad = auxDisponibilidad.get('title')
    auxDisponibilidad = auxDisponibilidad.get('data-bs-original-title')
    
    #Limpiar valores
    Disponibilidad    = unicodedata.normalize("NFKD",auxDisponibilidad).split('|')
    ventas = limpiarVentas(Disponibilidad)
    stock  = limpiarStock(Disponibilidad)
    
    #Devolver dupla en formato de lista
    return [int(ventas), int(stock)]

''' Devuelve el pais al que pertenece el vendedor '''
def obtenerLugarVendedor (contenedor):

    #Obtención del fragmento span donde se encuentra el dato
    auxPais = contenedor.find('span',{'class':'icon d-flex has-content-centered me-1'})
    #Recuperación del valor de interes
    #Versión sin selenium
    #auxPais = auxPais.get('title')
    auxPais = auxPais.get('data-bs-original-title')
    
    #Limpiar valores
    pais = limpiarPais(auxPais)
    
    #Devolver valor
    return str(pais)

''' Devuelve el nickname del vendedor '''
def obtenerNombreVendedor (contenedor):

    #Obtención del fragmento span donde se encuentra el dato
    auxNick = contenedor.find('span',{'class':'d-flex has-content-centered me-1'})
    #Recuperación del valor de interes
    auxNick = auxNick.get_text()
    #Limpiar valores
    nickname = auxNick.strip()
    
    #Devolver valor
    return str(nickname)

''' Devuelve el tipo de vendedor que es (si no existe es Private) '''
def obtenerTipoVendedor (contenedor):

    #Obtención del fragmento span donde se encuentra el dato (hay que pasar el if para evitar los vacíos)
    if (contenedor.find('span',{'class':'fonticon-users-professional'}) is not None):
        auxNivel = contenedor.find('span',{'class':'fonticon-users-professional'}) 
        
        #Versión sin selenium
        #auxNivel = auxNivel.get('title')
        auxNivel = auxNivel.get('data-bs-original-title')
        
        #Limpiar valores
        nivel = auxNivel.strip()  
        #Devolver valor      
        return str(nivel) 
    else:
        return 'Private'

# -- ASOCIADO A DATOS DE PRODUCTO

''' Devuelve la calidad de la carta '''
def obtenerCalidadCarta (contenedor):

    #Obtención del fragmento span donde se encuentra el dato
    auxQ = contenedor.find('span',{'class':'badge'})
    #Recuperación del valor de interes
    auxQ = auxQ.get_text()
    #Limpiar valores
    quality = auxQ.strip()
    
    #Devolver valor
    return str(quality)

''' Devuelve el idioma de la carta '''
def obtenerIdiomaCarta (contenedor):

    #Obtención del fragmento span donde se encuentra el dato
    auxL = contenedor.find('span',{'class':'icon me-2'})
    #Recuperación del valor de interes
    auxL = auxL.get('data-original-title')
    #Limpiar valores
    language = auxL.strip()
    
    #Devolver valor
    return str(language)

''''''
def comprobarIconoEspecial (contenedor):

    if (contenedor.find('span',{'class':'icon st_SpecialIcon mr-1'}) is not None):
        return True
    else:
        return False

''''''
def obtenerIconoEspecial (contenedor):
    
    if(comprobarIconoEspecial(contenedor)):
        auxIco = contenedor.find('span',{'class':'icon st_SpecialIcon mr-1'}) 
        icono = auxIco.get('data-bs-original-title')
        return icono
    else:
        return '-'


''' Comprueba si existe la foto '''
def comprobarFoto (contenedor):

    if (contenedor.find('span',{'class':'fonticon-camera'}) is not None):
        return True
    else:
        return False


''' Comprueba si existe comentario '''
def comprobarComentario (contenedor):

    if (contenedor.find('span',{'class':'fonticon-comments fonticon-color-primary d-lg-none ms-auto'}) is not None):
        return True
    else:
        return False

''' devuelve comentario si es que existe '''
def obtenerComentario (contenedor):
    
    if(comprobarComentario(contenedor)):
        auxCom = contenedor.find('span',{'class':'fonticon-comments fonticon-color-primary d-lg-none ms-auto'}) 
        comentario = auxCom.get('data-bs-original-title')
        return comentario
    else:
        return '-'

''' Devuelve la cantidad de la carta que se le puede comprar '''    
def obtenerCantidadDisponible (contenedor):

    #Obtención del fragmento span donde se encuentra el dato
    auxQ = contenedor.find('span',{'class':'item-count small text-end'})
    #Recuperación del valor de interes
    auxQ = auxQ.get_text()
    #Limpiar valores
    quantity = auxQ.strip()
    
    #Devolver valor
    return int(quantity)    

''' Devuelve el precio de venta de la carta '''
def obtenerPrecio (contenedor):

    #Obtención del fragmento span donde se encuentra el dato
    auxP = contenedor.find('span',{'class':'color-primary small text-end text-nowrap fw-bold'})
    #Recuperación del valor de interes
    auxP = auxP.get_text()
    #Limpiar valores
    precioMoneda = auxP.strip().split(" ")
    precio       = limpiarPrecio(precioMoneda)
    moneda       = limpiarMoneda(precioMoneda)
    
    #Devolver valor
    return [precio,moneda]

''' Comprueba con selenium si existe un elemento '''
def check_exists_by_xpath(driver,xpath):
    try:
        driver.find_element(By.XPATH, xpath)
    except NoSuchElementException:
        return False
    return True
