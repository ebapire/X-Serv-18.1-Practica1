#!/usr/bin/python

import webapp
import urllib
import csv
import sys


class Cutter (webapp.webApp):

    dicc_corto = {} #el key es la url entera y el value el localhost:1234/3
    dicc_largo = {} #el key es el numero y el value la url entera
    contador = str(0);
    #abro los archivos csv y los copio

    try:
        with open('urls.csv','r') as fcsv:
            reader = csv.reader(fcsv)
            for row in reader:
                url_num = row[0]
                contador = str(int(url_num) + 1)
                url_c = 'http://localhost:1236/' + url_num
                url_l = row[1]
                dicc_corto[url_l] = url_c
                dicc_largo[url_num] = url_l

            fcsv.close()
    except IOError: #no encuentro el archivo csv asi que me creo uno nuevo (como si fuera a escribir de el)
        fcsv  = open('urls.csv', 'w')
        fcsv.close()
        contador = str(0);

    def parse(self, request):
        #Return the resource name (including /)
        try:
            metodo = request.split()[0]
            recurso = request.split()[1]
            if metodo == 'POST':
                cuerpo = request.split("\r\n\r\n")[1]
            else:
                cuerpo = ''
        except IndexError:
            return None
        return (metodo, recurso, cuerpo)

    def process(self, parsedRequest):
        metodo, recurso, cuerpo = parsedRequest

        if metodo == 'GET' and recurso == '/':
                httpCode = '200 OK'
                formulario = '<FORM action="http://localhost:1236"' + \
                         ' method="POST" accept-charset="UTF-8">' + \
                         'URL: <input type="text" name="url">' + \
                         '<input type="submit" value="Acortar"></p></form>'
                lista_urls = ""
                for url_corta in self.dicc_corto:
                    lista_urls += '<p>' + '<a href="' + self.dicc_corto[url_corta] +\
                            '">' +self.dicc_corto[url_corta] +'</a> => <a href="'+\
                            str(url_corta) +'">' + str(url_corta) + '</a></p>'
                htmlBody = '<html><head><b>Servidor acortador</b></head>\
                            <body>'+ formulario + lista_urls +'</body></html>'

        elif metodo == 'POST' and recurso == '/':
            url = cuerpo.split('=')[1]
            url = urllib.unquote(url).decode('utf8')
            #si no tiene http o https lo tengo que anadir
            if url[0:6] == 'http://' or url[0:7] == 'https://':
                pass
            else:
                url = 'http://' + url
            try:
                urlfound = self.dicc_corto[url]
            except KeyError:
                #si no la he encontrado en el diccionario la anado
                url_corta = 'http//localhost:1236/' + self.contador
                self.dicc_largo[self.contador] = url
                self.dicc_corto[url] = url_corta
                #escribo en los csv
                with open ('urls.csv', 'a') as fcsv:
                    write = csv.writer(fcsv)
                    write.writerow([self.contador, url])
                    fcsv.close()
                self.contador = str(int(self.contador) + 1)

            httpCode = '200 OK'
            htmlBody = '<html><body><p><a href="' + url_corta + '">Ve a la URL que\
                        has pedido</a></p><p><a href="http://localhost:1236">Ve al home</a>' + \
                        '</p></html></body>'
        elif metodo == 'GET':
            recurso = recurso.split('/')[1]
            try:
                recursonum = int(recurso)
                try:
                    urlfound = self.dicc_largo[recurso]
                    httpCode = '300 Found'
                    htmlBody = '<html><body><head><meta ' + \
                            'http-equiv="refresh" content="1; url=' +\
                            urlfound + '" />'
                except KeyError:
                    httpCode = '200 OK'
                    htmlBody = '<html><head><b>Servidor acortador</b></head>\
                                <br/><body>El key que buscas no esta \
                                en el diccionario</body></html>'
            except ValueError:
                httpCode = '400 Bad Request'
                htmlBody = 'Try another key'

        else:
            httpCode = '405 Method Not Allowed'
            htmlBody = 'Go Away!'
        return (httpCode, htmlBody)


if __name__ == "__main__":
    CutterApp = Cutter("localhost", 1236)
