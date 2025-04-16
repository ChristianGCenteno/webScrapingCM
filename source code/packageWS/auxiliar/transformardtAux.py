'''
Funciones y Procedimientos utilizados en el moduleETL para ayudar con la unificación de resultados
'''
import pandas as pd
#from datetime import datetime

#pd.set_option("display.max_columns", None)
#pd.set_option("display.max_rows", None)

''' Función que combina los csv de histórico (solo añade los campos en los que no coincidan) '''
def limpiarVentas (pdOld,pdNew):
    
    pdFinal = pd.concat([pdOld,pdNew],ignore_index=True)
    pdFinal = pdFinal.drop_duplicates(subset=['fecha','pormedioVenta'],keep='first')
    
    return pdFinal

''' Función que combina los csv de ofertas (cuando ya no hay un registro antiguo marca la fecha que se ejecutó el programa) '''
def ActualizarOfertas (pdOld,pdNew,fechaActual):
        
    #Crear campo marcador sobre los nuevos (para identificarlo)
    pdOld['checkOld'] = 0
    pdNew['checkNew'] = 1
    
    #Debido al formato en el que se guardan las fehcas. Se recuperará el formato de las fechas
    #pdOld['finiOferta'] = pdOld['finiOferta'].apply(lambda x: datetime.strptime(str(x),'%d/%m/%Y').strftime('%Y-%m-%d'))
    #pdOld.loc[pdOld['ffinOferta'].notna(),'ffinOferta'] = pdOld.loc[pdOld['ffinOferta'].notna(),'ffinOferta'].apply(lambda x: datetime.strptime(str(x),'%d/%m/%Y').strftime('%Y-%m-%d'))
    
    #Unir campos, lo que permitirá ver la marca de los 1
    pdFinal = pdOld.merge(pdNew,how='outer',on = ['idOferta','nick','pais','tipoVendedor','language','quality','hayIconoEsp','iconoEsp','hayFoto','hayComentario','comentario','quantity','precio','moneda'])
    
    #Nos quedamos con la Finicio de la oferta correcta
    pdFinal.loc[(pdFinal['checkOld'] == 0)      , 'finiOferta'] = pdFinal['finiOferta_x']
    pdFinal.loc[(pdFinal['finiOferta_x'].isna()), 'finiOferta'] = pdFinal['finiOferta_y']
    
    #Mantenemos/Creamos la fecha fin de la oferta
    pdFinal.loc[(pdFinal['checkNew'].isna()) & (pdFinal['ffinOferta_x'].notna()), 'ffinOferta'] = pdFinal['ffinOferta_x']
    pdFinal.loc[(pdFinal['checkNew'].isna()) & (pdFinal['ffinOferta_x'].isna()) , 'ffinOferta'] = fechaActual
    
    #Actualizamos la ventas/stock del vendedor
    pdFinal.loc[(pdFinal['checkNew'].isna()), 'ventas'] = pdFinal['ventas_x']
    pdFinal.loc[(pdFinal['checkNew'] == 1)  , 'ventas'] = pdFinal['ventas_y']
    pdFinal.loc[(pdFinal['ventas_x'].isna()), 'ventas'] = pdFinal['ventas_y']   
    
    pdFinal.loc[(pdFinal['checkNew'].isna()), 'stock'] = pdFinal['stock_x']
    pdFinal.loc[(pdFinal['checkNew'] == 1)  , 'stock'] = pdFinal['stock_y']
    pdFinal.loc[(pdFinal['stock_x'].isna()) , 'stock'] = pdFinal['stock_y'] 
    
    
    #Reordenamos columnas (nos quedamos con las que queramos)
    pdFinal = pdFinal[['idOferta','nick','pais','tipoVendedor','ventas','stock','language','quality','hayIconoEsp','iconoEsp','hayFoto','hayComentario','comentario','quantity','precio','moneda','finiOferta','ffinOferta']]

    return pdFinal
    