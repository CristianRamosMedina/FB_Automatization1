import time
import random
from ..adb_utils import crear_funciones_con_serial
from .utils import ejecteg
from ..config import hilos_activos

def gestos_videos_random(serial):
    hilos_activos[serial] = True
    run, tap, long_tap, move, write, buscarTextoEnRegion = crear_funciones_con_serial(serial)
    run("shell input keyevent 224")  # Encender pantalla
    time.sleep(1)
    move("50%","68%","50%","20%")
    time.sleep(1)

    ejecteg(serial)

    print(f"\n🚀 Abriendo TikTok en {serial}...")
    run("shell monkey -p com.zhiliaoapp.musically -c android.intent.category.LAUNCHER 1")

    time.sleep(5)
    tap("50%", "90.34%")
    time.sleep(4)

    tap("8.85%","90.87%")

    tap("79.17%", "80.26%")

    time.sleep(0.8)
    
    tap("50%", "6.4%")
    time.sleep(0.6)
    
    coords = buscarTextoEnRegion(("25.29%", "8.19%", "85.71%", "85.94%"), "Videos", umbral_similitud=0.7)
    if coords:
        tap(*coords)
    else:
        coords = buscarTextoEnRegion(("25.29%", "8.19%", "85.71%", "85.94%"), "Videos", umbral_similitud=0.6)
        if coords:
            tap(*coords)
        else:
            coords = buscarTextoEnRegion(("25.29%", "8.19%", "85.71%", "85.94%"), "Videos", umbral_similitud=0.3)
            if coords:
                tap(*coords)
            else:   
                print("No se encontró 'Camera' en pantalla, tocando en el centro")
    
    time.sleep(1.6)
    
    tap("61.48%", "16.92%"); time.sleep(0.6)
    tap("28.70%", "16.92%"); time.sleep(0.6)
    

    coords = buscarTextoEnRegion(("2.50%", "75.98%", "98.70%", "93.76%"), "Next")
    if coords:
        tap(*coords)
    else:
        tap("74.54%", "90.17%")
    
    time.sleep(4)
    ############# Musica
    coords = buscarTextoEnRegion(("5.74%", "5.30%", "98.70%", "13.12%"), "Sound")
    if coords:
        tap(*coords)
    else:
        print("\n No musica encontrada, tocando en el centro")
        tap("50%", "10.6%")

    time.sleep(0.9)
    tap("92.69%", "52.02%")
    time.sleep(1)

    music = random.choice([
        "Take Me Home, Country Roads - John Denver",
        "God Bless the USA - Lee Greenwood",
        "Cotton Fields - Creedence Clearwater Revival",
        "American Honey - Lady A",
        "Only in America - Brooks & Dunn",
        "Courtesy of the Red, White and Blue - Toby Keith",
        "Small Town Saturday Night - Hal Ketchum",
        "Where the Stars and Stripes and the Eagle Fly - Aaron Tippin",
        "Made in America - Toby Keith",
        "This Land Is Your Land - Woody Guthrie",
        "America the Beautiful - Ray Charles",
        "Born in the U.S.A. - Bruce Springsteen",
        "Ragged Old Flag - Johnny Cash",
        "Some Gave All - Billy Ray Cyrus",
        "American Soldier - Toby Keith",
        "If You're Reading This - Tim McGraw",
        "Sweet Home Alabama - Lynyrd Skynyrd",
        "Only in America - Brooks & Dunn",
        "God Bless America Again - Loretta Lynn & Conway Twitty",
        "My Town - Montgomery Gentry",
        "Workin’ Man Blues - Merle Haggard",
        "Back Where I Come From - Kenny Chesney",
        "Living in the USA - Steve Miller Band",
        "Red Solo Cup - Toby Keith",
        "The Fightin’ Side of Me - Merle Haggard"
    ])

    
    write(music)
    run("shell input keyevent 66")  
    time.sleep(6)
    long_tap("87.68%", "50.68%")    
    time.sleep(2.3)
    tap("50.46%", "29.19%")         

    time.sleep(2)
    tap("95%","18.5%")
    time.sleep(2.5)
    move("95%","89.5%","5%","89.5%",1000)  
    time.sleep(1.6)
    coords= buscarTextoEnRegion(("2.50%", "75.98%", "98.70%", "93.76%"), "overlay")
    if coords:
        tap(*coords)
    else:
        time.sleep(1.6)
        move("95%","89.5%","9%","89.5%") 
        time.sleep(1.6)
        move("95%","89.5%","7.6%","89.5%") 
        time.sleep(1.6)
        tap("1.14%", "90%")  
    time.sleep(1.6)
    
    #abre
    tap("50%", "6.4%")
    time.sleep(0.6)
    coords = buscarTextoEnRegion(("25.29%", "8.19%", "85.71%", "85.94%"), "Camera", umbral_similitud=0.7)
    if coords:
        tap(*coords)
    else:
        coords = buscarTextoEnRegion(("25.29%", "8.19%", "85.71%", "85.94%"), "Camera", umbral_similitud=0.6)
        if coords:
            tap(*coords)
        else:
            coords = buscarTextoEnRegion(("25.29%", "8.19%", "85.71%", "85.94%"), "Camera", umbral_similitud=0.3)
            if coords:
                tap(*coords)
            else:   
                print("No se encontró 'Camera' en pantalla, tocando en el centro")

    time.sleep(1.6)    
    
    sticker = random.choice([
        ("28.70%", "32.56%"),
        ("94.72%", "16.92%"),
        ("61.48%", "16.92%")
    ])

    print("Sticker en: ", *sticker)
    
    tap(*sticker)
    time.sleep(0.5)
    
    coords = buscarTextoEnRegion(("2.50%", "75.98%", "98.70%", "93.76%"), "Next")
    if coords:
        tap(*coords)
    else:
        tap("74.54%", "90.17%") 
    time.sleep(1)
    print("Estirando sticker")
    move("99.5%", "72%","99.8%","72%", duration=2000)
    time.sleep(1)
    tap("95.29%", "5.50%")
    time.sleep(1.2)
    
    caption= random.choice([
        "#MAGA #Trump2024 #TrumpTrain #AmericaFirst #Patriot",  
        "#TrumpSupporter #MakeAmericaGreatAgain #RedWave #SaveAmerica #KAG",  
        "#Conservative #ProTrump #Freedom #USA #PatriotsUnite",  
        "#TrumpWon #AmericaStrong #SupportTrump #Election2024 #PatriotPride",  
        "#Republican #AmericanPride #StandWithTrump #GodBlessTheUSA",  
        "#TrumpForever #BackTheBlue #LoveUSA #ProFreedom #MAGA2024"

    ])
    
    tap("19.96%", "11%")
    time.sleep(0.4)
    write(caption)
    time.sleep(1.2)
    
    long_tap("90%", "5.375%")        
    time.sleep(0.6)
    coords = buscarTextoEnRegion(("1%", "73%", "100%", "100%"), "Post",umbral_similitud=0.9)
    if coords:
        tap(*coords)
    else:
        coords = buscarTextoEnRegion(("1%", "73%", "100%", "100%"), "Post",umbral_similitud=0.6)
        if coords:
            tap(*coords)
        else:
            coords = buscarTextoEnRegion(("1%", "73%", "100%", "100%"), "Post",umbral_similitud=0.5)
            if coords:
                tap(*coords)
    
    time.sleep(30)
