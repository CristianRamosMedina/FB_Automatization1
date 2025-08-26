import time, requests, imaplib, re, email
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from bs4 import BeautifulSoup
from ..utils import parse_coord, get_screen_size, crear_funciones_con_serial


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
    elif "check your email" in texto:
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
    run, tap, long_tap, move, write, buscarTextoEnRegion, detectarColorOTap ,leerTextoEnRegion = crear_funciones_con_serial(serial)
    print("\n⏳ Esperando correo...")
    for i in range(15):  # ~2.5 minutos max
        print(f"🔁 Intento {i+1}/30")
        codigo = buscar_codigo_de_cuenta_hija(
            serial,
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

def buscar_codigo_de_cuenta_hija(
    serial,
    user,
    app_password,
    cuenta_hija,
    remitentes=("noreply@account.tiktok.com", "register@account.tiktok.com")
):
    """
    Busca un código de verificación (5-6 dígitos) enviado hoy (UTC) y con <= 20 min de antigüedad
    para la cuenta hija indicada (en el campo 'To'), desde cualquiera de los remitentes dados.
    Prioriza Gmail X-GM-RAW; si no está disponible, usa IMAP puro con OR anidado válido.

    Retorna el código como str si lo encuentra; en caso contrario, None.
    """
    print(f"📬 Buscando código para: {cuenta_hija}")

    mail = None
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(user, app_password)
        mail.select("inbox")

        # ---------- Búsqueda robusta multi-remitente ----------
        ids = []
        try:
            # 1) Gmail: X-GM-RAW
            gm_from = " OR ".join([f'from:{r}' for r in remitentes]) if remitentes else ''
            # to: filtra por destinatario; si la cuenta trae alias/plus addressing, puedes aflojar este filtro
            gm_query = f'({gm_from}) to:{cuenta_hija}'.strip()
            result, data = mail.search(None, 'X-GM-RAW', gm_query)
            if result == "OK" and data and data[0]:
                ids = data[0].split()[::-1]  # más recientes primero
            else:
                raise RuntimeError("X-GM-RAW sin resultados")
        except Exception:
            # 2) Fallback IMAP: OR anidado binario correcto
            terms = [f'(FROM "{r}")' for r in remitentes] or ['(FROM "")']
            or_chain = terms[0]
            for t in terms[1:]:
                or_chain = f'(OR {or_chain} {t})'
            # Filtramos también por destinatario
            query = f'({or_chain} TO "{cuenta_hija}")'
            result, data = mail.search(None, query)
            if result != "OK":
                print(f"💥 SEARCH IMAP falló: {result} {data}")
                return None
            ids = data[0].split()[::-1] if data and data[0] else []

        if not ids:
            print("❌ No hay coincidencias para remitentes/destino.")
            return None

        now_utc = datetime.now(timezone.utc)
        hoy_utc = now_utc.date()

        for i in ids:
            res, msg_data = mail.fetch(i, "(RFC822)")
            if res != "OK" or not msg_data or not msg_data[0]:
                continue

            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)

            to = (msg.get("To") or "").lower()
            subject = msg.get("Subject") or ""
            date_str = msg.get("Date") or ""
            from_ = msg.get("From") or ""

            # Si el 'To' no contiene la cuenta hija, saltar (reduce falsos positivos)
            if cuenta_hija.lower() not in to:
                continue

            # Parseo de fecha a UTC
            try:
                msg_datetime = parsedate_to_datetime(date_str)
                if msg_datetime.tzinfo is None:
                    msg_datetime = msg_datetime.replace(tzinfo=timezone.utc)
                else:
                    msg_datetime = msg_datetime.astimezone(timezone.utc)
            except Exception as e:
                print(f"⚠️ Error al interpretar la fecha: {e}")
                continue

            # Solo correos de HOY (UTC)
            if msg_datetime.date() != hoy_utc:
                # print(f"⏳ Correo descartado: no es de hoy ({msg_datetime.date()})")
                continue

            # No más viejo de 20 minutos
            if (now_utc - msg_datetime) > timedelta(minutes=20):
                # print(f"⏰ Correo descartado: >20 min ({msg_datetime})")
                continue

            # Extraer cuerpo texteable
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    ctype = part.get_content_type()
                    if ctype == "text/plain":
                        try:
                            body = part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8", errors="ignore")
                            break
                        except Exception:
                            body = part.get_payload(decode=True).decode(errors="ignore")
                            break
                if not body:
                    # Si no hubo text/plain, intentamos text/html y quitamos tags rápido
                    for part in msg.walk():
                        if part.get_content_type() == "text/html":
                            try:
                                html = part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8", errors="ignore")
                            except Exception:
                                html = part.get_payload(decode=True).decode(errors="ignore")
                            body = re.sub(r"<[^>]+>", " ", html)
                            break
            else:
                try:
                    body = msg.get_payload(decode=True).decode(msg.get_content_charset() or "utf-8", errors="ignore")
                except Exception:
                    body = (msg.get_payload(decode=True) or b"").decode(errors="ignore")

            # Buscar código (5 o 6 dígitos)
            texto = f"{subject} {body}"
            match = re.search(r"\b(\d{5,6})\b", texto)
            if match:
                codigo = match.group(1)
                print("✅ Código encontrado:")
                print(f"📧 Para: {to}")
                print(f"👤 De: {from_}")
                print(f"🧾 Asunto: {subject}")
                print(f"📅 Fecha: {msg_datetime} (UTC)")
                print(f"🔑 Código: {codigo}")
                return codigo

        print("❌ No se encontró código reciente válido para esa cuenta hija.")
        return None

    except imaplib.IMAP4.error as e:
        print(f"💥 Error IMAP: {e}")
        return None
    except Exception as e:
        print(f"💥 Error general: {e}")
        return None
    finally:
        try:
            if mail is not None:
                try:
                    mail.close()
                except Exception:
                    pass
                mail.logout()
        except Exception:
            pass

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
