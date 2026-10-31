# Lab-07-Entra-ID-Sign-in-Logs

## 1. Descripción del proyecto

Este laboratorio está inspirado en el capítulo 6 de la primera temporada de *La que se avecina*: **«Un voyeur, una inspección y una tarjeta de crédito»**.

Tras extraviar su cartera en Mirador de Montepinar, Antonio Recio convoca una junta para interrogar a los vecinos y descubrir quién está utilizando su tarjeta de crédito. Javi le advierte que no puede acusar a nadie sin pruebas, pero pronto descubre que Lola ha encontrado la cartera y ha realizado una compra con la tarjeta de su vecino. Berta recomienda cancelar la tarjeta, aunque Antonio se niega porque está obsesionado con desenmascarar al responsable. La situación se complica cuando otros vecinos, conocedores del incidente, también empiezan a utilizarla.

Trasladando esta situación al entorno digital de Mirador de Montepinar S.L., la tarjeta de crédito representa las credenciales de una identidad corporativa. Antonio ha perdido el control de su cuenta y comienzan a producirse distintos intentos de acceso que requieren una investigación.

Nuestra misión será descubrir qué ha sucedido utilizando los registros de inicio de sesión (*Sign-in Logs*) de Microsoft Entra ID. A través de Microsoft Graph PowerShell y herramientas de análisis, investigaremos las autenticaciones, identificaremos comportamientos anómalos y recopilaremos evidencias para reconstruir el incidente.

Al igual que Javi insiste en no acusar a ningún vecino sin pruebas, nuestro objetivo será diferenciar los hechos registrados de las simples sospechas y elaborar un diagnóstico fundamentado en evidencias técnicas.

### Objetivos técnicos

- Localizar y consultar los registros de inicio de sesión de Microsoft Entra ID.
- Interpretar los resultados de autenticación y los códigos de error disponibles.
- Diferenciar los posibles fallos de credenciales, autenticación multifactor y Acceso Condicional.
- Examinar los detalles de los intentos de inicio de sesión para formular y comprobar hipótesis.
- Correlacionar las evidencias disponibles con la identidad, la aplicación, el dispositivo y el contexto del acceso.
- Identificar patrones de autenticación fallida y posibles comportamientos sospechosos.
- Recuperar y exportar registros mediante Microsoft Graph PowerShell.
- Automatizar el filtrado y análisis de eventos utilizando PowerShell.
- Documentar el incidente, las evidencias recopiladas y las posibles acciones correctivas.
- Comprender las limitaciones de los registros disponibles según los permisos, las licencias y la configuración del tenant.

## 2. Estructura del proyecto

Antonio Recio quiere saber quién está utilizando su tarjeta y qué ha ocurrido realmente en Mirador de Montepinar. Para investigar el incidente, el laboratorio se organiza en cinco bloques: datos, scripts, consultas, informes y evidencias.

### `data/` — Los registros de Montepinar

Almacena muestras anonimizadas de los registros de inicio de sesión (*Sign-in Logs*) obtenidos desde Microsoft Entra ID. Estos datos servirán para realizar pruebas y analizar los eventos sin publicar información sensible del tenant.

### `scripts/` — La investigación de Antonio Recio

Contiene los scripts PowerShell utilizados para conectarse a Microsoft Graph, recuperar los registros de autenticación, filtrar eventos y automatizar su análisis.

### `queries/` — El interrogatorio de Montepinar

Incluye las consultas KQL utilizadas para investigar patrones de autenticación en Azure Log Analytics, como intentos fallidos, resultados de MFA y actividad sospechosa.

### `reports/` — Los informes de la junta

Guarda los resultados del análisis, incluyendo exportaciones CSV e informes en Markdown con los errores detectados, los eventos relevantes y las conclusiones de la investigación.

### `screenshots/` — Las pruebas del delito

Contiene las capturas de pantalla que documentan la configuración del entorno, las consultas realizadas y los resultados obtenidos durante las pruebas.

### Flujo de trabajo

1. Se generan distintos eventos de autenticación en Microsoft Entra ID.
2. Se consultan los Sign-in Logs y se recuperan los registros mediante Microsoft Graph PowerShell.
3. Se procesan los eventos mediante scripts PowerShell y, opcionalmente, consultas KQL.
4. Se documentan los hallazgos y se generan los informes correspondientes.
5. Se recopilan las evidencias para reconstruir el incidente y proponer medidas correctivas.

Así, Antonio podrá dejar de sospechar de todos los vecinos por igual y descubrir qué ha ocurrido realmente con su identidad. Porque en Montepinar se puede acusar a cualquiera, pero en IAM hacen falta evidencias.

