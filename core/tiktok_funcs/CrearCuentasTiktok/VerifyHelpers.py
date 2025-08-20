import time, requests,datetime,imaplib,re,email
from datetime import timezone,timedelta
from ..utils import parse_coord,get_screen_size,crear_funciones_con_serial
from email.utils import parsedate_to_datetime
from bs4 import BeautifulSoup

def esperar_nickname_o_verificar(serial,correo,apodo):
    w,h=get_screen_size(serial)
    run, tap, long_tap, move, write, buscarTextoEnRegion, detectarColorOTap ,leerTextoEnRegion = crear_funciones_con_serial(serial)
    x1=parse_coord("6.67%",w)
    y1=parse_coord("13.29%",h)
    x2=parse_coord("76.57%",w)
    y2=parse_coord( "18.76%",h)
    region = (x1,y1,x2,y2)
    texto = leerTextoEnRegion(region)

    if "create nickname" in texto:
        print("✅ Detectado. Continuamos.")
        write(apodo)
        coords = buscarTextoEnRegion(("1.76%", "37.39%", "96.39%", "93.59%"),"continue")
        if coords:
            tap(*coords)
        else:
            coords = buscarTextoEnRegion(("1.76%", "37.39%", "96.39%", "93.59%"),"next")
            if coords:
                tap(*coords) 
            else:    
                tap("86.57%", "97.47%")
                time.sleep(1)
                tap("50%","90.38%")

    elif "verify email" in texto:
        print("🔐 Detectado verify. Ejecutando verify()...")
        verify(serial,correo)
        time.sleep(4)

        texto = leerTextoEnRegion(region)
        if "create nickname" in texto:
            print("✅ Detectado tras verify. Continuamos.")
            write(apodo)
            coords = buscarTextoEnRegion(("1.76%", "37.39%", "96.39%", "93.59%"),"continue")
            if coords:
                tap(*coords)
            else:
                coords = buscarTextoEnRegion(("1.76%", "37.39%", "96.39%", "93.59%"),"next")
                if coords:
                    tap(*coords) 
                else:    
                    tap("86.57%", "97.47%")
                    time.sleep(1)
                    tap("50%","90.38%")
        else:
            print("❌ No se detectó nickname luego de verify. Continuamos sin escribir apodo.")

    else:
        print("❌ Texto no esperado. Continuamos sin hacer nada.")


def verify(serial,correo):
    run, tap, long_tap, move, write, buscarTextoEnRegion , leerTextoEnRegion = crear_funciones_con_serial(serial)
    print("\n⏳ Esperando correo...")
    for i in range(30):  # ~2.5 minutos max
        print(f"🔁 Intento {i+1}/30")
        codigo = buscar_codigo_de_cuenta_hija(
            user="previ4303@gmail.com",
            app_password="tibf uoar hpvl kuog",
            cuenta_hija= correo
        )
        if codigo:
            print(f"✅ Código: {codigo}")
            write(codigo)
            break
        time.sleep(5)
    else:
        print("❌ No se encontró el código tras varios intentos.")


def buscar_codigo_de_cuenta_hija(serial,user, app_password, cuenta_hija, remitente_filtro="noreply@account.tiktok.com"):
    print(f"📬 Buscando código para: {cuenta_hija}")

    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(user, app_password)
    mail.select("inbox")

    result, data = mail.search(None, f'(FROM "{remitente_filtro}")')
    ids = data[0].split()[::-1]  # Correos más recientes primero

    now_utc = datetime.now(timezone.utc)
    hoy_utc = now_utc.date()

    for i in ids:
        res, msg_data = mail.fetch(i, "(RFC822)")
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        to = msg.get("To", "").lower()
        subject = msg.get("Subject", "")
        date_str = msg.get("Date", "")
        from_ = msg.get("From", "")

        if cuenta_hija.lower() not in to:
            continue

        # Parsear fecha del correo
        try:
            msg_datetime = parsedate_to_datetime(date_str)
            if msg_datetime.tzinfo is None:
                msg_datetime = msg_datetime.replace(tzinfo=timezone.utc)
            else:
                msg_datetime = msg_datetime.astimezone(timezone.utc)
        except Exception as e:
            print(f"⚠️ Error al interpretar la fecha: {e}")
            continue

        # Filtrar correos que no son del día de hoy (en UTC)
        if msg_datetime.date() != hoy_utc:
            print(f"⏳ Correo descartado: no es de hoy ({msg_datetime.date()})")
            continue

        # Filtrar correos con más de 20 minutos de antigüedad
        if (now_utc - msg_datetime) > timedelta(minutes=20):
            print(f"⏰ Correo descartado: más de 20 minutos de antigüedad ({msg_datetime})")
            continue

        # Leer el contenido
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode(errors="ignore")
                    break
        else:
            body = msg.get_payload(decode=True).decode(errors="ignore")

        # Buscar código
        match = re.search(r"\b(\d{5,6})\b", subject + " " + body)
        if match:
            codigo = match.group(1)
            print("✅ Código encontrado:")
            print(f"📧 Para: {to}")
            print(f"🧾 Asunto: {subject}")
            print(f"📅 Fecha: {msg_datetime} (UTC)")
            print(f"🔑 Código: {codigo}")
            return codigo

    print("❌ No se encontró código reciente válido para esa cuenta hija.")
    return None


def buscar_y_verificar_link(serial ,user, app_password, cuenta_hija, remitente_filtro="noreply@account.tiktok.com"):
    print(f"📬 Buscando enlace de verificación para: {cuenta_hija}")

    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(user, app_password)
    mail.select("inbox")

    result, data = mail.search(None, f'(FROM "{remitente_filtro}")')
    ids = data[0].split()[::-1]  # Correos más recientes primero

    now_utc = datetime.now(timezone.utc)
    hoy_utc = now_utc.date()

    for i in ids:
        res, msg_data = mail.fetch(i, "(RFC822)")
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        to = msg.get("To", "").lower()
        subject = msg.get("Subject", "")
        date_str = msg.get("Date", "")

        if cuenta_hija.lower() not in to:
            continue

        try:
            msg_datetime = parsedate_to_datetime(date_str)
            if msg_datetime.tzinfo is None:
                msg_datetime = msg_datetime.replace(tzinfo=timezone.utc)
            else:
                msg_datetime = msg_datetime.astimezone(timezone.utc)
        except Exception as e:
            print(f"⚠️ Error al interpretar la fecha: {e}")
            continue

        if msg_datetime.date() != hoy_utc:
            continue

        if (datetime.now(timezone.utc) - msg_datetime) > timedelta(minutes=60):
            continue

        # Leer contenido HTML
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if "html" in content_type:
                    body = part.get_payload(decode=True).decode(errors="ignore")
                    break
        else:
            body = msg.get_payload(decode=True).decode(errors="ignore")

        # Buscar con BeautifulSoup
        soup = BeautifulSoup(body, "html.parser")
        link_encontrado = None

        for a in soup.find_all("a", href=True):
            if "verify your email address" in a.get_text(strip=True).lower():
                link_encontrado = a["href"]
                break
        if link_encontrado:
            print("✅ Link de verificación encontrado:")
            print(f"🔗 {link_encontrado}")

            ok = verificar_link_en_backend(link_encontrado,serial)
            if ok:
                print("🎉 Verificación completada desde Python.")
            else:
                print("❌ El backend respondió con error.")
            return link_encontrado

    print("❌ No se encontró un enlace reciente válido para esa cuenta hija.")
    return None

def verificar_link_en_backend(link,serial):
    try:
        response = requests.get(link, timeout=10)
        print(f"🌐 Petición enviada al link. Código de respuesta: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error al abrir el link: {e}")
        return False
