'''
Módulo que se encarga de devolver las urls con sus respectivos nombres
'''
import os

def ejecutarRead():
    
    #Listado final de direcciones
    direcciones = []
    
    #Find the path of the file
    nombre_fichero = os.path.join(os.getcwd(),'recurso\listadourl.txt')
    
    #Primero se tiene que volcar el contenido del documenteo
    try:
        #Abre el fichero, con "permiso" de lectura Y LO RECORRE SEPARANDOLO EN LINEAS
        with open(nombre_fichero, 'r') as f:
            lineas = f.read().strip().split('\n')
    except FileNotFoundError:
        print("No existe el nombre del fichero: {}".format(nombre_fichero))
        
    #Se ignora los comentarios (los que empiezan por -- y se extrae la url con su "alias")
    for index,linea in enumerate(lineas):
        
        #Se incrementa en uno el valor de index para que coincida con el número de línea "humano"
        index += 1

        if(linea[0:2] != '--' and linea != ""):
            
            #Comprueba si la línea tiene separador
            checkSep = '::' in linea
            if(checkSep is False):
                print('la línea ' + str(index) + ' del archivo no presenta separador(::). Se cancela la lectura')
                exit()
            
            #Obtención de los valores clave
            valores = linea.split('::')
            url,carta = valores[0],valores[1]
            #Obtención de los checks para verificar si la línea es válida
            checkUrl,checkCarta = (url!=''),(carta!='')
            
            #Comprueba si la sintaxis de la url es válida. De no ser así se corta operación
            if(checkUrl is False):
                print('la línea ' + str(index) + ' del archivo no presenta url. Se cancela lectura')
                exit()
            if(checkCarta is False):
                print('la línea ' + str(index) + ' del archivo no presenta el nombre de la carta. Se cancela lectura')
                exit()
                
            #Los casos válidos, los irá almacenando en un listado de url con el nombre de la carta
            direcciones.append([url,carta])
            
    return direcciones