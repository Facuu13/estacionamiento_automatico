# Manual de usuario — Estacionamiento QR

Este sistema permite **entrar** con un QR o enlace, **obtener un ticket digital**, **estacionar sin pagar al ingreso**, y al **salir** ver el tiempo de uso, **pagar con el celular** (Mercado Pago) y **abrir la barrera**, sin app nativa ni efectivo.

## 1. Ingreso

1. En la entrada, escaneá el **QR de ingreso** (o abrí el enlace que te indique el operador). Podés ver un ejemplo en la web en **QR de ingreso para imprimir** (`/entrada`).
2. En la pantalla **Ingreso**, escribí la **patente** del vehículo (como en la cédula verde).
3. Tocá **Obtener ticket y abrir barrera**. Se crea una sesión, se muestra el **ticket digital** y la barrera de entrada recibe la orden de abrirse (en hardware real, vía el dispositivo en el molinete).
4. **No tenés que pagar todavía**: el monto se calcula **al salir** según el tiempo de uso.

## 2. Ticket y estacionamiento

1. En el ticket verás la patente, la hora de ingreso y un **QR de salida** (o podés usar el enlace **Salida** cuando te vayas).
2. Guardá el token de salida o usá el mismo navegador para que quede guardado.

## 3. Salida y pago

1. **En producción**, en la barrera de salida hay un **cartel con un QR** impreso: al escanearlo se abre la pantalla de salida con tu sesión.
2. En la pantalla **Salida** ves el **tiempo de uso** y el **monto estimado** (se fija al iniciar el pago en Mercado Pago).
3. Tocá **Pagar con Mercado Pago** y completá el pago con tarjeta u otros medios habilitados.
4. Cuando el pago esté **aprobado**, tocá **Abrir barrera**. El backend autoriza la salida (en hardware real, el ESP32 abriría el relé unos segundos).

En **modo desarrollo** (`MOCK_PAYMENTS=true`), el sistema puede simular el pago sin cobro real; seguí las indicaciones en pantalla.

## Problemas frecuentes

- **“Pago pendiente”**: esperá a que Mercado Pago confirme el pago o revisá tu correo/notificaciones de MP.
- **“Ya se registró la salida”**: el token de salida ya se usó; si necesitás ayuda, contactá al operador del estacionamiento (este MVP no incluye soporte remoto automático).
