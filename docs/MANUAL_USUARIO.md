# Manual de usuario — Estacionamiento QR

Este sistema permite **entrar**, **pagar con el celular** (Mercado Pago) y **salir** escaneando un QR, sin app nativa ni efectivo.

## 1. Ingreso

1. Abrí en el celular el enlace o escaneá el QR de **ingreso** en la entrada.
2. En la pantalla **Ingreso**, escribí la **patente** del vehículo (como en la cédula verde).
3. Tocá **Continuar al pago**. Se crea una sesión de estacionamiento.

## 2. Pago

1. En la pantalla de pago, tocá **Ir a pagar**.
2. Se abre **Mercado Pago** (Checkout Pro) para completar el pago con tarjeta u otros medios habilitados.
3. En **modo desarrollo** (`MOCK_PAYMENTS=true`), el sistema puede simular el pago sin cobro real; seguí las indicaciones en pantalla.

Hasta que el pago no esté **aprobado**, no podés autorizar la salida.

## 3. Salida

1. En la salida, escaneá el **QR de salida** (o abrí el enlace que te dio el sistema al ingresar).
2. Si hace falta, pegá el **token de salida** que recibiste al registrar el ingreso.
3. Tocá **Abrir barrera**. Si el pago está confirmado, la barrera recibe la orden de abrir unos segundos.

Si el pago está pendiente o fue rechazado, verás un mensaje indicando que no podés salir todavía.

## Problemas frecuentes

- **“Pago pendiente”**: esperá a que Mercado Pago confirme el pago o revisá tu correo/notificaciones de MP.
- **“Ya se registró la salida”**: el token de salida ya se usó; si necesitás ayuda, contactá al operador del estacionamiento (este MVP no incluye soporte remoto automático).
