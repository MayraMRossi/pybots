# This is a sample Python script.

# Press Mayús+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import json
import os
import request

def decapitalize_first_letter(s, upper_rest = False):
  return ''.join([s[:1].lower(), (s[1:].upper() if upper_rest else s[1:])])

def crear_steps(mock_utils_asign_inserted, midd):
    if not os.path.isdir('steps'):
        os.mkdir('steps')
    if not os.path.isdir('steps/{midd}'.format(midd=midd)):
        os.mkdir('steps/{midd}'.format(midd=midd))


    mock_utils_asign = [
        {"programInternList": ["PEKM"], "programFormat1": "datos_kyc"},
        {"programInternList": ["PEKM", "PE00", "PE10"], "programFormat1": "data_test_kyc"}
    ]

    if mock_utils_asign_inserted != None:
        mock_utils_asign = mock_utils_asign_inserted

    programas_nombres = [elemento["programFormat1"] for elemento in mock_utils_asign]
    programasNombres = [(''.join([word.capitalize() for word in elemento["programFormat1"].split("_")])) for elemento in mock_utils_asign]

    for i in range(len(programasNombres)):
        f = open('base.txt', 'r')
        programaNuevo = f.read()
        programaNuevo = programaNuevo.replace("XXXX", programasNombres[i])
        programaNuevo = programaNuevo.replace("YYYY", programas_nombres[i])
        programaNuevo = programaNuevo.replace("AAAA", midd)
        programaNuevo = programaNuevo.replace("BBBB", midd.capitalize())
        programaNuevo = programaNuevo.replace("CCCC", decapitalize_first_letter(programasNombres[i]))
        nf = open('steps/{midd}/{nombre}Step.java'.format(nombre=programasNombres[i], midd=midd), 'w')
        nf.write(programaNuevo)
        nf.close()
        f.close()

def snake_a_cammel(palabra_snake):
    return ''.join([word.capitalize() for word in palabra_snake.split("_")])

def crear_archivos_jsons(datos, nombre, tipo, version, programas):
    tipoResponse = tipo
    if tipo == "":
        tipoResponse = "Ok"
    if not os.path.isdir('jsons'):
        os.mkdir('jsons')
    nombreArchivoGenerico = "jsons/Request{nombre}{tipo}{numero}.json"
    nombreArchivoGenericoResponse = "jsons/Response{nombre}{tipo}{numero}.json"
    dataTitulos = datos["DATA_TITULOS"].split(datos["SEPARADOR_REQ"])
    dataTitulos.pop(0)
    dataTitulos.pop(0)
    dataTitulos.pop(0)
    dataTitulos.pop(-1)

    contador = 1
    for data_datos in datos["DATAS_DATOS"]:
        dataDatos = data_datos.split(datos["SEPARADOR_REQ"])
        dataDatos.pop(0)
        dataDatos.pop(-1)
        jsonRequest = {
            "header": {
                "channel": datos["HEADER_REQUEST"]
            },
            "data": {}
        }
        if (datos["TIENE_OK_Y_CODIGO"]):
            dataDatos.pop(0)
            dataDatos.pop(0)

        for i in range(len(dataTitulos)):
            if (dataDatos[i].strip() != ""):
                jsonRequest["data"][dataTitulos[i].strip()] = dataDatos[i].strip()
        if contador != 1:
            nombreArchivo = nombreArchivoGenerico.format(nombre=snake_a_cammel(nombre), tipo=tipo, numero=str(contador))
            ResponseArchivo = nombreArchivoGenericoResponse.format(nombre=snake_a_cammel(nombre), tipo=tipoResponse, numero=str(contador))
        else:
            nombreArchivo = nombreArchivoGenerico.format(nombre=snake_a_cammel(nombre), tipo=tipo, numero="")
            ResponseArchivo = nombreArchivoGenericoResponse.format(nombre=snake_a_cammel(nombre), tipo=tipoResponse, numero="")
        with open(nombreArchivo, "w") as outfile:
            outfile.write(json.dumps(jsonRequest, indent=4))
        with open(ResponseArchivo, "w") as outfile:

            url = ''
            myobj = {json.dumps(jsonRequest, indent=4)}

            for programa in programas:
                url = 'https://midd-tnconnector-1-0-dev.apps.ocp4-tst.intranet.local/tnconnector/' + version + "/" + programa+ "\n"
            x = requests.post(url, json=myobj)
            outfile.write(x.text)

        contador += 1

def obtener_datos_y_o_crear_jsons(version,crear_jsons = True):
    ESPERANDO = 0
    EXTRAER_NOMBRES = 1
    EXTRAER_DATOS = 2

    tipo_actual = "" #Tipo ok o error
    estado_actual = 0

    path = 'gherkings'
    if not os.path.isdir('gherkings'):
        os.mkdir('gherkings')
    listado_de_nombres_archivos = os.listdir(path)
    print(listado_de_nombres_archivos)
    listado_mock = []

    for nombre_archivo in listado_de_nombres_archivos:
        archivo = open(path + '/' + nombre_archivo , 'r')
        lineas = archivo.readlines()
        datos = {
            "HEADER_REQUEST": "autotest",
            "TIENE_OK_Y_CODIGO": True,
            "DATA_TITULOS": "",
            "DATAS_DATOS": [],
            "SEPARADOR_REQ": "|"
        }
        mock = {
            "programInternList": [],
            "programFormat1": nombre_archivo.split(".")[0],
            "cantidadOk": 0,
            "cantidadError": 0
        }

        for linea in lineas:
            if estado_actual == EXTRAER_DATOS and linea.find("|") != -1:
                datos["DATAS_DATOS"].append(linea)
            elif estado_actual == EXTRAER_DATOS:
                if crear_jsons:
                    crear_archivos_jsons(datos, nombre_archivo.split(".")[0], tipo_actual, version, mock["programInternList"])
                if tipo_actual == "":
                    mock["cantidadOk"] = len(datos["DATAS_DATOS"])
                elif tipo_actual == "Error":
                    mock["cantidadError"] = len(datos["DATAS_DATOS"])
                datos = {
                    "HEADER_REQUEST": "autotest",
                    "TIENE_OK_Y_CODIGO": True,
                    "DATA_TITULOS": "",
                    "DATAS_DATOS": [],
                    "SEPARADOR_REQ": "|"
                }
                estado_actual = ESPERANDO
            elif estado_actual == EXTRAER_NOMBRES:
                datos["DATA_TITULOS"] = linea
                estado_actual = EXTRAER_DATOS

            if linea.find("@Ok") != -1:
                tipo_actual = ""
            elif linea.find("@Error") != -1:
                tipo_actual = "Error"
            if linea.find("Examples:") != -1:
                estado_actual = EXTRAER_NOMBRES
            if linea.find("Transacción") != -1:
                linea_actual = linea.replace("Transacción", "")
                mock["programInternList"] = [servicios.strip() for servicios in linea_actual.split(",")]

        if estado_actual == EXTRAER_DATOS:
            if crear_jsons:
                crear_archivos_jsons(datos, nombre_archivo.split(".")[0], tipo_actual,version, mock["programInternList"])
            if tipo_actual == "":
                mock["cantidadOk"] = len(datos["DATAS_DATOS"])
            elif tipo_actual == "Error":
                mock["cantidadError"] = len(datos["DATAS_DATOS"])
            estado_actual = ESPERANDO
        listado_mock.append(mock)
        print(str(mock) + ",")
    return listado_mock



aceptar = False
carpetaMidd = None
opcion_crear_jsons = None
opcion_crear_steps = None
opcion_num_vers = None
while aceptar == False:
    carpetaMidd = input("ingrese el nombre del MIDD: ")
    opcion_crear_jsons = input("quiere crear los jsons: Si(1) No(0) ")
    opcion_crear_steps = input("quiere crear los steps: Si(1) No(0) ")
    opcion_num_vers = input("inserte num de version: ")
    opcion_json = "NO"
    opcion_step = "NO"
    if opcion_crear_jsons == "1":
        opcion_json = "SI"
    if opcion_crear_steps == "1":
        opcion_step = "SI"
    print("usted eligio la capeta midd {carpeta}, {opcion_json} hacer los jsons, {opcion_step} hacer los steps y la version {opcion_num_vers}".format(carpeta=carpetaMidd,opcion_json=opcion_json,opcion_step=opcion_step,opcion_num_vers=opcion_num_vers))
    correcto = input("¿Es correcto? Si(1) No(0): ")
    if correcto == "1":
        aceptar = True

if opcion_crear_jsons == "1":
    listado_de_mocks = obtener_datos_y_o_crear_jsons(opcion_num_vers,True)
else:
    listado_de_mocks = obtener_datos_y_o_crear_jsons(False)
if opcion_crear_steps == "1":
    crear_steps(listado_de_mocks, carpetaMidd)
