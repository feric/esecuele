# esecuele
El método para imprimir los <b>request</b> y  los <b> Response </b> de todas las peticiones es
<b> showData() </b>.

Para hacer uso de ésta función debes habilitar la función de verbose, agregue la opción <b>-v</b> y la función
<b>def setVerbosity(self,simon)</b>
Debes agregar esta línea en la parte en donde tu código realiza las consultas a la aplicación web:


	if self.verbosity:

		self.showData(objeto=Attempt,vulnerable=True,lll=unquote(repr(Attempt.request.body)))

Cambia el argumento <b>Attempt.request.body</b> por el payload que estas lanzando
