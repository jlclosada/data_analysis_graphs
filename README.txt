
# temporal_series_plot_from_raster.py


Purpose:   
Este script se encarga de leer los rasters que se encuentran dentro de una carpeta y los transforma en un array de NumPy (matriz).

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

Autor:     jcaceres
Version:   1.1.0
Created:   17/05/2022
Copyright: (c) jcaceres 2022
License:   <your license>

## FUNCIONES
---------------------------------------------------------------------------------------------------------------------------------------------------------------
### def date_change(date):


Esta función se encarga de leer el nombre del archivo en cuestión, extrayendo de su nombre la fecha. Por ello, es importante que los archivos
tengan la misma nomenclatura: (variable_YYYYmmdd_NDVI_BOA_S2A_interpolada.tif) kc_20191012_NDVI_BOA_S2A_interpolada. De esta manera, la función date_change,
es capaz de retornar una fecha en formato mm/dd/YYYY a partir de la fecha, que es su argumento.
---------------------------------------------------------------------------------------------------------------------------------------------------------------
### def create_dic(n):


Esta función se encarga de crear un diccionario con un solo campo, la fecha, que contendrá una lista vacía. Además, se añadirán N campos, que es el argumento que
le pasamos a la función. El numero N hará referencia al numero de parcelas, por lo que se creará un campo para cada parcela, y en cada lista se irán almacenando
los diferentes valores extraídos del raster.
Como resultado obtendremos un diccionario de N campos + el campo de la fecha creado por defecto y lleno de listas vacías que se irán rellenando en procesos
posteriores.
---------------------------------------------------------------------------------------------------------------------------------------------------------------
### def create_lists(n):


Esta función se encarga de crear tantas listas como numero de parcelas haya. Realmente se crea una lista, llena de listas. Esto se realiza para ir
volcando todos los datos que se van extrayendo de los raster y posteriormente pasarlos al diciconario anterior.
---------------------------------------------------------------------------------------------------------------------------------------------------------------
### def get_dataframe(file_list, raster_input, parcels, num_parcels):

Se podria decir que es la función maestra. Se encarga de crear el diccionario principal mediante la funcion create_dic(n), y de crear la lista con todas las
listas que contendrán todos los valores extraidos con create_lists(n).
Crea también una lista de fechas, donde se irán guardando todas las fechas que se encuentren en los nombres de los archivos. Al aplicarle la función date_change(),
tendremos una lista con todas las fechas disponibles en un formato (mm/dd/YYYY), perfecto para que Pandas lo interprete.

Es en este punto donde se ejecuta el bucle principal del script, donde, para cada fichero con una determinada extensión que se encuentre en la carpeta elegida
por el usuario, ese fichero se lee mediante Rasterio y es transformado en un array de NumPy, para facilitar el volcado de los datos.
Mediante Rasterstats, calculamos la estadística deseada para cada parcela. Podemos escoger entre varias opciones.

Tras ello, vamos creando listas donde volcamos los datos estadísticos del raster, de las fechas leidas en los ficheros, y todo ello se va volcando a la lista de listas
que contedrá toda la información y, posteriormente, al diccionario general que creamos al principio.

Por ultimo se crea una dataframe de Pandas y se le pasa el diccionario lleno de valores como datos. Además, a todos los valores de fechas se le asigna 
un formato datetime, para que Pandas, matplotlib y seaborn lo interpreten como fechas reales y no como texto.
---------------------------------------------------------------------------------------------------------------------------------------------------------------
### def plots(dataframe, campaña, cultivo, variable, stat, mean):

### def plots2(dataframe1, dataframe2, campaña, cultivo, variable1, variable2, stat, mean):

Estas dos funciones se encargan de graficar los dataframes obtenidos anteriormente. En funcion de los rasters que seleccionemos tendremos uno o dos dataframes, y una
o dos variables. En los casos donde tengamos opciones de meter más gráficos, utilizaremos la función plots2().
Para modificar las propiedades de los gráficos y su apariencia, editar directamente las funciones.
---------------------------------------------------------------------------------------------------------------------------------------------------------------




