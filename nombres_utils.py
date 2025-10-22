#source: https://gist.github.com/franps/f491182068f7079ce7bcadeafd16b110

articulos = ['de', 'del', 'la', 'los', 'las', 'De', 'Del'
             'La', 'Los', 'Las', 'o', 'O', 'Mac', 'mac', 'di', 'Di', 'da', 'do', 'dos', 'san', 'd']


def unirArticulos(array):
    result = ['', '', '', '', '', '']
    cont = 0
    for i in array:
        if i in articulos:
            result[cont] += i + " "
        else:
            result[cont] += i
            cont += 1
    result = result[:cont]
    return result


def parsearNombre(nombre):
    nombreCompleto = {}
    aux = nombre.split()
    nombreCompleto["pnombre"] = aux[0]
    aux = aux[1:]
    largoAux = len(aux)
    if (largoAux == 1):
        nombreCompleto["papellido"] = aux[0]
        return nombreCompleto
    aux2 = unirArticulos(aux)
    if len(aux2) == 1:
        nombreCompleto["papellido"] = aux2[0]
        return nombreCompleto
    if (len(aux2) == 2):
        nombreCompleto["papellido"] = aux2[0]
        nombreCompleto["sapellido"] = aux2[1]
        return nombreCompleto
    if (len(aux2) == 3):
        nombreCompleto["snombre"] = aux2[0]
        nombreCompleto["papellido"] = aux2[1]
        nombreCompleto["sapellido"] = aux2[2]
        return nombreCompleto
    # No puedo distinguir si tiene tres nombres o tres apellidos
    # Hay más personas con tres nombres que tres apellidos
    if (len(aux2) == 4):
        nombreCompleto["snombre"] = aux2[0] + " "+aux[1]
        nombreCompleto["papellido"] = aux2[2]
        nombreCompleto["sapellido"] = aux2[3]
        return nombreCompleto
    else:
        return nombreCompleto


def pprint(list):
    for item in list:
        print(item + " : " + str(list[item]))

#print("==== Nombres no compuestos ====")
#pprint(parsearNombre("Juan Perez"))
#pprint(parsearNombre("Juan Perez Rodriguez"))
#pprint(parsearNombre("Juan Martin Perez Rodriguez"))

#print("==== Tres nombres ====")
#pprint(parsearNombre("Clara Maria Francisca Pereira Ruiz"))

#print("==== Nombres compuestos ====")
#pprint(parsearNombre("Lorena de León"))
#pprint(parsearNombre("Francisco de los Santos Perez"))
#pprint(parsearNombre("Maria de los Angeles Santos Abel"))
#pprint(parsearNombre("Mario Eduardo O Neil Rebollo"))
#pprint(parsearNombre("Jose Luis del Perpetuo Socorro"))
#pprint(parsearNombre("Nicolas Juan Herrera Mac Eachen"))
#pprint(parsearNombre("Clara Maria Francisca"))
#pprint(parsearNombre("LUIS GERARDO MEDINA ROJAS"))