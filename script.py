
import random


wetter = ["Sonnig", "Normal"]
limoglas = 10
Schild_kosten_klein = 20
Schild_kosten_mittel = 30
Schild_kosten_gross = 40
geld = 200
Lev = [0.2, 0.3, 0.4 ,0.5, 0.6, 0.7, 0.8, 0.9]
print("Hallo Wilkommenn im Limostand")
Steuern = 1
run = 0


while run < 100:
    run += 1
    print("Du hast ", geld, "Cent")
    Wetter = random.choice(wetter)
    print("Heute ist das Wetter " + Wetter)
    Limo_anzahl = int(input("Wie viele Limogläser wilst du heute vorbereiten? Ein Limoglas kostet " + str(limoglas) + "Cent. "))
    Limo_kosten = int(input("Wie viel soll die limo kosten "))

    Schilder_klein = int(input("Wie viele kleine Schilder wilst du heute aufstellen? Ein kleines Schild kostet " + str(Schild_kosten_klein) + "Cent. "))
    Schilder_mittel = int(input("Wie viele mittlereSchilder wilst du heute aufstellen Ein mittleres Schild kostet " + str(Schild_kosten_mittel) + "Cent. "))
    Schilder_gross = int(input("Wie viele grosse Schilder wilst du heute aufstellen Ein großes Schild kostet " + str(Schild_kosten_gross) + "Cent. "))
    if run == 2:
        wetter.append("Heiß")
        wetter.append("Bewölkt")
        wetter.append("Heiß")
        wetter.append("Bewölkt")
    #lustig
    multi = random.choice(Lev)
    schilder_count = 0
    while schilder_count != Schilder_klein:
        Lev.append(0.7)
        Lev.append(0.7)
        Lev.append(0.7)
        multi += 0.1
        schilder_count += 1
    schilder_count = 0
    while schilder_count != Schilder_mittel:
        Lev.append(0.8)
        Lev.append(0.8)
        Lev.append(0.8)
        multi += 0.2
        schilder_count += 1
    schilder_count = 0
    while schilder_count != Schilder_gross:
        Lev.append(0.9)
        Lev.append(0.9)
        Lev.append(0.9)
        multi += 0.4

        schilder_count += 1


    if wetter == "Sonnig":
        multi += 0.2
    if wetter == "Bewölkt":
        multi -= 0.2
    if wetter == "Heiß":
        multi += 0.5


    if Limo_kosten < 50:
        multi += 0.05
    if Limo_kosten < 40:
        multi += 0.05
    if Limo_kosten < 30:
        multi += 0.05
    if Limo_kosten < 20:
        multi += 0.05
    if Limo_kosten < 10:
        multi += 0.05
    if Limo_kosten < 5:
        multi += 0.05

    if Limo_kosten > 50:
        multi -= 0.05
    if Limo_kosten > 60:
        multi -= 0.05
    if Limo_kosten > 70:
        multi -= 0.05
    if Limo_kosten > 80:
        multi -= 0.05
    if Limo_kosten > 90:
        multi -= 0.05
    if Limo_kosten > 100:
        multi -= 0.1
    if Limo_kosten > 150:
        multi -= 0.15
    if Limo_kosten > 200:
        multi -= 0.5
    if multi > 1:
        multi = 1
    if multi <= 0:
        multi = 0

    Anzahl_verkaufter_limos = round(Limo_anzahl * multi, 0)
    Brutto = Anzahl_verkaufter_limos * Limo_kosten
    Netto = Brutto * Steuern
    geld+= Netto
    'geld'
    geld -= Limo_anzahl * limoglas
    geld -= Schild_kosten_klein * Schilder_klein
    geld -= Schild_kosten_mittel * Schilder_mittel
    geld -= Schild_kosten_gross * Schilder_gross
    if geld < 0:
        print("Du bist pleite")
        run = False
    #Ausgabe
    print("Du hast ", Anzahl_verkaufter_limos, "Limos verkauft")
    print("Du hast ", Brutto, "Cent verdient mit steuern also", Netto, "Cent")






































