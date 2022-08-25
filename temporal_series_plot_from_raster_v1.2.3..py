#-------------------------------------------------------------------------------------------
#Name:      temporal_series_plot_from_raster.py
#Purpose:   
"""Este script se encarga de leer los rasters que se encuentran dentro de una carpeta y los transforma en un array de NumPy (matriz).

Al usuario se le piden los siguientes inputs:
- Raster a procesar: Introducir "1" o "2". El script no admite más en esta versión.
- Sacar la estadística media de todas las parcelas: Introducir "y" o "n". Si se selecciona si, el script calculará la estadística media total de todas las parcelas para cada fecha.
- Estadística a calcular: Podemos seleccionar la estadística a calcular.
- Cultivo: Según el cultivo seleccionado (maiz/remolacha) el script llamará a un fichero shp u otro.
- Localización de los archivos: Se abrirá un explorador para seleccionar las carpetas donde se encuentran los raster que queremos procesar

Para cada raster se extrae un valor estadístico dentro del shp definido. Este valor estadístico se extrae mediante la librería rasterstats y puede ser ['mean', 'max',
'mean', 'median', 'majority']. 
Una vez extraídas las estadísticas del raster para cada polígono sel shp, estos valores se van almacenando en una lista. Posteriormente, estos datos se van volcando
a diferentes listas (una para cada poligono) y después se vuelcan a un diccionario.
También se extrae la fecha del raster a partir del nombre del fichero, por ello es importante la nomenclatura de los archivos, deben tener el siguiente formato:
'kc_20191012_NDVI_BOA_S2A_interpolada.tif'
Una vez que todos los datos de los raster se vuelcan al diccionario creado, se crea un dataframe de Pandas que contendrá tantas columnas como polígonos del shp, 
además de otra columna para la fecha.
A partir de este dataframe se procede a la representación de los datos en una figura de matplotlib con gráfica seaborn."""
#Autor:     jcaceres
#Version:   1.2.3
#Created:   17/05/2022
#Copyright: (c) jcaceres 2022
#License:   <your license>
#--------------------------------------------------------------------------------------------

import geopandas as gpd
import rasterio
import rasterstats
from rasterstats import zonal_stats, point_query
from rasterio.plot import show, show_hist
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np
from datetime import datetime, timedelta
from tkinter import filedialog
from tkinter import *

#INPUTS Y CONFIGURACIÓN
num_rasters = input('¿Cuantos rasters quiere procesar? (1/2): ')
mean_plot_process = input('¿Quiere los graficos de la media total de las parcelas (y/n): ')
stat = input('¿Que estadistica quiere calcular? (mean, max, min, median, majority): ') 
cultivo = input('Seleccione cultivo de las parcelas (maiz/remolacha/alfalfa/cereal): ')
campaña = input('Seleccione campaña (2019/2020/2021): ')
if num_rasters == '1':
    extension_raster1 = input('Extension del raster 1 (tif/img): ')
else:
    extension_raster1 = input('Extension del raster 1 (tif/img): ')
    extension_raster2 = input('Extension del raster 2 (tif/img): ')

output_path = "\\\\imgwebserver\\IDIS\\DEMETER\\DATOS\\GRAFICAS"
output_tablas = "\\\\imgwebserver\\IDIS\\DEMETER\\DATOS\\GRAFICAS\\TABLAS"
shp_path = "\\\\imgwebserver\\IDIS\\DEMETER\\DATOS\\GRAFICAS\\shp_auxiliares"

#-----------------------------------------------------------------------------------------------
#funciones

def date_change(date):
    year = date[:4]
    month = date[4: 6]
    day = date[-2:]
    new_date = month + '/' + day + '/' + year
    return new_date

def create_dic(n):
    dic = {'date': []}
    for i in range(1, n+1):
        dic[str(i)] = []
    return dic

def create_lists(n):
    list = [[] for i in range(1, n+1)]
    return list

def get_dataframe(file_list, raster_input, parcels, num_parcels):
    my_dic = create_dic(num_parcels)
    list_oflists = create_lists(num_parcels)
    date_list = []
    elemento = 0
    numero_elemento_lista = len(file_list)
    for file in file_list:
        print("\n \n----------------------------------------------\nReading raster: \n" + file + '\n----------------------------------------------\n \n \n')
        raster = rasterio.open(raster_input + '\\' + file)  
        #array_var = raster.read(1)      #ERROR CON MINARET
        #affine = raster.transform
        #Calculating zonal statistics
        try:
            average_var = zonal_stats(parcels, raster.name)
        except UserWarning:
            print('We are taking value -999 from raster as NoData')
        #Extracting mean data from array dic
        var_mean = []
        i = 0
        while i < len(average_var):
            var_mean.append(average_var[i]['mean'])
            i = i + 1
        date = date = file.split('_')[1]
        f_date = date_change(date)
        date_list.append(f_date)
        j = 0
        for v in var_mean:
            list_oflists[j].append(var_mean[j])
            j = j + 1
        l = 0
        for l in range(1, num_parcels + 1):
            my_dic[str(l)] = list_oflists[l - 1]
        l = l + 1
        elemento = elemento + 1
        porcentaje = int(elemento * 100 / numero_elemento_lista)
        tiempo_consulta = datetime.now() - startTime
        print(f"Se han procesado: {elemento} rasters.\nProceso: {porcentaje} %\nTiempo transcurrido: {tiempo_consulta}")
    
    my_dic['date'] = date_list

    data = pd.DataFrame(my_dic)
    data['date'] = pd.to_datetime(data['date'], format = '%m/%d/%Y')
    return data

def plots(dataframe, campaña, cultivo, variable, stat, mean):   #Función para generar gráficos a partir de un dataframe.
    if mean == True:
        total_mean_column = dataframe.mean(axis = 1)
        dataframe[stat] = total_mean_column
        #fig, ax = plt.subplots(figsize = (15, 4.5))
        fig = plt.figure(figsize = (15, 5), layout = 'constrained')

        #ax.grid(alpha = 0.2, color = 'SteelBlue', linestyle = "-.", linewidth = 1.5)
        plt.plot('date', 'mean', data = dataframe, label = f'{variable} media', linewidth = 2.5, color = 'b')
        plt.title(f'Serie temporal media total {variable} en {campaña} (' + cultivo + ')', fontsize = 24, fontweight = 'bold')
        plt.xlabel('Fecha', fontsize = 14, color = 'b', fontweight = 'bold')
        plt.ylabel(f'{variable}', fontsize = 14, color = 'b', fontweight = 'bold')
        plt.xticks(fontsize = 12, color = 'black', rotation = 45)
        plt.yticks(fontsize = 12, color = 'black')
        plt.grid()

        #sns.lineplot(x = 'date', y = 'mean', data = dataframe)
        #plt.legend(f'{variable}', loc='best', fontsize = 'medium', fancybox = True, shadow = True)
        plt.legend(fontsize = 'medium', fancybox = True, shadow = True)
        return fig
    else:
        fig, ax = plt.subplots(figsize = (15, 4.5))
    

        ax.grid(alpha = 0.2, color = 'SteelBlue', linestyle = "-.", linewidth = 1.5)
        plt.title(f'Serie temporal {variable} en {campaña} por parcela (' + cultivo + ')', fontsize = 16, fontweight = 'bold')
        plt.xlabel('Fecha', fontsize = 14, color = 'b', fontweight = 'bold')
        plt.ylabel(f'{variable}', fontsize = 14, color = 'b', fontweight = 'bold')
        plt.xticks(fontsize = 12, color = 'black', rotation = 45)
        plt.yticks(fontsize = 12, color = 'black')
        plt.grid()

        for column in dataframe.columns:
            if column != 'date':
                sns.lineplot(x = 'date', y = str(column), data = dataframe)
        plt.legend()
            
        
        return fig

def plots2(dataframe1, dataframe2, campaña, cultivo, variable1, variable2, stat, mean):
    if mean == True:
        total_mean_column1 = dataframe1.mean(axis = 1)
        dataframe1[stat] = total_mean_column1

        total_mean_column2 = dataframe2.mean(axis = 1)
        dataframe2[stat] = total_mean_column2

        #fig, ax = plt.subplots(figsize = (15, 4.5))
        fig = plt.figure(figsize = (15, 5), layout = 'constrained')

        #ax.grid(alpha = 0.2, color = 'SteelBlue', linestyle = "-.", linewidth = 1.5)
        plt.plot('date', 'mean', data = dataframe1, label = f'{variable1} media', linewidth = 2.5, color = 'b')
        plt.plot('date', 'mean', data = dataframe2, label = f'{variable2} media', linewidth = 2.5, color = 'r')
        plt.title(f'Serie temporal media total {variable1} - {variable2} en {campaña} (' + cultivo + ')', fontsize = 16, fontweight = 'bold')
        plt.xlabel('Fecha', fontsize = 14, color = 'b', fontweight = 'bold')
        plt.ylabel(f'{variable1}', fontsize = 14, color = 'b', fontweight = 'bold')
        plt.xticks(fontsize = 12, color = 'black', rotation = 45)
        plt.yticks(fontsize = 12, color = 'black')
        plt.grid()

        #sns.lineplot(x = 'date', y = 'mean', data = dataframe1)
        #sns.lineplot(x = 'date', y = 'mean', data = dataframe2)

        plt.legend(fontsize = 'medium', fancybox = True, shadow = True)
        
        return fig
    else:
        fig1, ax1 = plt.subplots(figsize = (15, 4.5))

        ax1.grid(alpha = 0.2, color = 'SteelBlue', linestyle = "-.", linewidth = 1.5)
        plt.title(f'Serie temporal media total {variable1} en {campaña} (' + cultivo + ')', fontsize = 16, fontweight = 'bold')
        plt.xlabel('Fecha', fontsize = 14, color = 'b', fontweight = 'bold')
        plt.ylabel(f'{variable1}', fontsize = 14, color = 'b', fontweight = 'bold')

        for column in dataframe1.columns:
            if column != 'date':
                sns.lineplot(x = 'date', y = str(column), data = dataframe1)
        
        fig2, ax2 = plt.subplots(figsize = (15, 4.5))

        ax2.grid(alpha = 0.2, color = 'SteelBlue', linestyle = "-.", linewidth = 1.5)
        plt.title(f'Serie temporal media {variable2} en {campaña} (' + cultivo + ')', fontsize = 16, fontweight = 'bold')
        plt.xlabel('Fecha', fontsize = 14, color = 'b', fontweight = 'bold')
        plt.ylabel(f'{variable2}', fontsize = 14, color = 'b', fontweight = 'bold')

        for column in dataframe2.columns:
            if column != 'date':
                sns.lineplot(x = 'date', y = str(column), data = dataframe2)
                
        return fig1, fig2

#-------------------------------------------------------------------------------------------------
#LECTURA DE SHAPES Y RASTERS PARA CADA CASO

if num_rasters == '1':
    parcels = gpd.read_file(shp_path + f"\\{campaña}\\parcelas_{cultivo}_{campaña}.shp")
    raster_input = filedialog.askdirectory(title = 'Seleccione la ubicación de los raster', initialdir = "\\\\imgwebserver\\IDIS\\DEMETER")
    try:
        file_list = [i for i in os.listdir(raster_input) if i.endswith(extension_raster1)]
        var = (file_list[1].split('_')[0])
    except:
        file_list = [i for i in os.listdir(raster_input) if i.endswith(extension_raster2)]
        var = (file_list[1].split('_')[0])
    num_parcelas = parcels.count()['ID']
    startTime = datetime.now()

    print('Leyendo los siguientes raster\nEsperar, por favor...')
    print('\n')
    for file in file_list:
        print(file)

    df = get_dataframe(file_list, raster_input, parcels, num_parcelas)

    if mean_plot_process == 'y':
        grafico = plots(df, campaña, cultivo, var, stat, mean = True)
        grafico.savefig(output_path + f"\\{campaña}\\serie_temporal_{var}_{cultivo}_media_" + file_list[0].split('_')[1] + '_' + file_list[-1].split('_')[1] + ".jpg")
        df.to_csv(output_tablas + f"\\{campaña}\\data_{var}_{cultivo}_media_" + file_list[0].split('_')[1] + '_' + file_list[-1].split('_')[1] + ".csv", sep = ';')
        grafico.show()
        print("Se ha guardado la figura correctamente en la carpeta: " + output_path + f"\\{campaña}") 
    
    elif mean_plot_process == 'n':
        grafico = plots(df, campaña, cultivo, var, stat, mean = False)
        
        grafico.savefig(output_path + f"\\{campaña}\\serie_temporal_{var}_{cultivo}_" + file_list[0].split('_')[1] + '_' + file_list[-1].split('_')[1] + ".jpg")
        df.to_csv(output_tablas + f"\\{campaña}\\data_{var}_{cultivo}_" + file_list[0].split('_')[1] + '_' + file_list[-1].split('_')[1] + ".csv", sep = ';')
        grafico.show()
        print("Se ha guardado la figura correctamente en la carpeta: " + output_path + f"\\{campaña}")

    else:
        print("Introduzca un valor valido\nO 'y' o 'n'")

elif num_rasters == '2':
    parcels = gpd.read_file(shp_path + f"\\{campaña}\\parcelas_{cultivo}_{campaña}.shp")
    raster1_input = filedialog.askdirectory(title = 'Seleccione la ubicación de los raster', initialdir = "\\\\imgwebserver\\IDIS\\DEMETER")
    raster2_input = filedialog.askdirectory(title = 'Seleccione la ubicación de los siguientes raster', initialdir = "\\\\imgwebserver\\IDIS\\DEMETER")

    try:
        file_list1 = [i for i in os.listdir(raster1_input) if i.endswith(extension_raster1)]
        extension_raster1 = 'tif'
        var1 = (file_list1[1].split('_')[0])

        file_list2 = [i for i in os.listdir(raster2_input) if i.endswith(extension_raster2)]
        extension_raster2 = 'tif'
        var2 = (file_list2[1].split('_')[0])
    except:
        file_list1 = [i for i in os.listdir(raster1_input) if i.endswith(extension_raster1)]
        extension_raster1 = 'img'
        var1 = (file_list1[1].split('_')[0])

        file_list2 = [i for i in os.listdir(raster2_input) if i.endswith(extension_raster2)]
        extension_raster2 = 'img'
        var2 = (file_list2[1].split('_')[0])
    num_parcelas = parcels.count()['ID']
    startTime = datetime.now()

    print('Leyendo los siguientes raster\nEsperar, por favor...')
    print('\n')
    for file in file_list1:
        print(file)

    for file in file_list2:
        print(file)

    df1 = get_dataframe(file_list1, raster1_input, parcels, num_parcelas)
    df2 = get_dataframe(file_list2, raster2_input, parcels, num_parcelas)

    if mean_plot_process == 'y':
        grafico = plots2(df1, df2, campaña, cultivo, var1, var2, stat, mean = True)

        grafico.savefig(output_path + f"\\{campaña}\\serie_temporal_{var1}_{var2}_{cultivo}_media_" + file_list1[0].split('_')[1] + '_' + file_list1[-1].split('_')[1] + ".jpg")
        df1.to_csv(output_tablas + f"\\{campaña}\\data_{var1}_{cultivo}_media_" + file_list1[0].split('_')[1] + '_' + file_list1[-1].split('_')[1] + ".csv", sep = ';')
        df2.to_csv(output_tablas + f"\\{campaña}\\data_{var2}_{cultivo}_media_" + file_list2[0].split('_')[1] + '_' + file_list2[-1].split('_')[1] + ".csv", sep = ';')
        print("Se ha guardado la figura correctamente en la carpeta: " + output_path + f"\\{campaña}")
        grafico.show()

    elif mean_plot_process == 'n':
        graficos = plots2(df1, df2, campaña, cultivo, var1, var2, stat, mean = False)

        graficos.savefig(output_path + f"\\{campaña}\\serie_temporal_{var1}_{cultivo}_" + file_list1[0].split('_')[1] + '_' + file_list1[-1].split('_')[1] + ".jpg")
        df1.to_csv(output_tablas + f"\\{campaña}\\data_{var1}_{cultivo}_" + file_list2[0].split('_')[1] + '_' + file_list2[-1].split('_')[1] + ".csv", sep = ';')
        df2.to_csv(output_tablas + f"\\{campaña}\\data_{var2}_{cultivo}_" + file_list2[0].split('_')[1] + '_' + file_list2[-1].split('_')[1] + ".csv", sep = ';')
        plt.show()
    else:
        print("Introduzca un valor valido\nO 'y' o 'n'")
else:
    print("Se tiene que introducir un numero válido\nO '1' o '2'")