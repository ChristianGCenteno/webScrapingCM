'''
MÓDULO PRINCIPAL ORQUESTADOR
'''
#Importación de los módulos
from packageWS.modulos.moduleReadUrl import ejecutarRead
from packageWS.modulos.moduleETL     import runETL


#Obtener el listado de las direcciones a analizar
direcciones = ejecutarRead()

#Ejecutar el ETL para cada uno de los valores de forma concurrente
runETL(direcciones,3,30)