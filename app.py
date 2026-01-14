import streamlit as st
import pandas as pd
import math

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="SQM Cargo Planner Pro", layout="wide", page_icon="🚚")

# --- BAZA POJAZDÓW (ZGODNIE Z PLIKIEM GEM3.HTML) ---
# Uwzględniono: TIR 31 palet / 12000 kg / Wysokość 265 cm
VEHICLES_DATA = {
    "BUS": {"pallets": 8, "weight": 1100, "l": 450, "w": 150, "h": 245},
    "Solówka 6m": {"pallets": 14, "weight": 3500, "l": 600, "w": 245, "h": 245},
    "Solówka 7m": {"pallets": 16, "weight": 3500, "l": 700, "w": 245, "h": 245},
    "FTL (Tir)": {"pallets": 31, "weight": 12000, "l": 1360, "w": 245, "h": 265},
}

# --- KOMPLETNA BAZA 136 PRODUKTÓW ---
# Dane zawierają: Nazwa, Długość, Szerokość, Wysokość, Waga, Sztuk/Case, Możliwość stackowania
PRODUCTS_DATA = {
    "17-23\" - plastic case": {"l": 80, "w": 60, "h": 20, "weight": 20.0, "ipc": 1, "stack": True},
    "24-32\" - plastic case": {"l": 60, "w": 40, "h": 20, "weight": 15.0, "ipc": 1, "stack": True},
    "32\" - triple - STANDARD": {"l": 90, "w": 50, "h": 70, "weight": 50.0, "ipc": 3, "stack": True},
    "43\" - triple - STANDARD": {"l": 112, "w": 42, "h": 80, "weight": 90.0, "ipc": 3, "stack": True},
    "45\"-55\" - double - STANDARD": {"l": 140, "w": 42, "h": 100, "weight": 150.0, "ipc": 2, "stack": True},
    "60-65\" - double - STANDARD": {"l": 160, "w": 40, "h": 230, "weight": 200.0, "ipc": 2, "stack": True},
    "75-86\" - double - STANDARD": {"l": 210, "w": 40, "h": 230, "weight": 230.0, "ipc": 2, "stack": True},
    "98\" - double - STANDARD": {"l": 250, "w": 70, "h": 230, "weight": 400.0, "ipc": 1, "stack": True},
    "NEC E326 - STANDARD": {"l": 70, "w": 50, "h": 70, "weight": 90.0, "ipc": 3, "stack": True},
    "NEC C431 - STANDARD": {"l": 80, "w": 50, "h": 80, "weight": 120.0, "ipc": 3, "stack": True},
    "NEC C501 - STANDARD": {"l": 100, "w": 50, "h": 100, "weight": 140.0, "ipc": 2, "stack": True},
    "NEC C551 - STANDARD": {"l": 100, "w": 50, "h": 100, "weight": 140.0, "ipc": 2, "stack": True},
    "SAMSUNG series 7 - STANDARD": {"l": 110, "w": 50, "h": 60, "weight": 160.0, "ipc": 2, "stack": True},
    "NEC C861 86\" - STANDARD": {"l": 140, "w": 40, "h": 230, "weight": 210.0, "ipc": 1, "stack": True},
    "NEC C981 98\" - STANDARD": {"l": 170, "w": 70, "h": 230, "weight": 250.0, "ipc": 1, "stack": True},
    "NEC X981 98\" TOUCHSCREEN - STANDARD": {"l": 170, "w": 70, "h": 230, "weight": 250.0, "ipc": 1, "stack": True},
    "iiYama 46\" - TOUCHSCREEN - STANDARD": {"l": 100, "w": 50, "h": 100, "weight": 140.0, "ipc": 2, "stack": True},
    "NEC V554 TOUCHSCREEN - STANDARD": {"l": 100, "w": 50, "h": 100, "weight": 140.0, "ipc": 2, "stack": True},
    "Samsung UE43 - STANDARD": {"l": 80, "w": 50, "h": 80, "weight": 120.0, "ipc": 3, "stack": True},
    "LG 60 UH605V - STANDARD": {"l": 110, "w": 40, "h": 230, "weight": 160.0, "ipc": 2, "stack": True},
    "LG 65 UJ620V - STANDARD": {"l": 110, "w": 40, "h": 230, "weight": 160.0, "ipc": 2, "stack": True},
    "LG 75\" - STANDARD": {"l": 140, "w": 40, "h": 230, "weight": 210.0, "ipc": 1, "stack": True},
    "MULTIMEDIA TOTEM 55\"": {"l": 100, "w": 60, "h": 210, "weight": 210.0, "ipc": 1, "stack": False},
    "P1 lub 1.58 ABSEN": {"l": 108, "w": 71, "h": 62, "weight": 103.0, "ipc": 8, "stack": True},
    "P1.9 UNILUMIN UPAD IV / S-FLEX": {"l": 117, "w": 57, "h": 79, "weight": 115.0, "ipc": 8, "stack": True},
    "P2.6 UNILUMIN UPAD IV": {"l": 117, "w": 57, "h": 79, "weight": 116.0, "ipc": 8, "stack": True},
    "P2.6 UNILUMIN UPAD IV / C-CUBE": {"l": 117, "w": 57, "h": 79, "weight": 125.0, "ipc": 8, "stack": True},
    "P2.6 UNILUMIN UPAD IV / S-FLEX": {"l": 117, "w": 57, "h": 79, "weight": 121.0, "ipc": 8, "stack": True},
    "P2.06 frameLED (STANDARD / CORNERS)": {"l": 86, "w": 62, "h": 100, "weight": 118.0, "ipc": 10, "stack": True},
    "P2.06 frameLED (CURVED INNER / OUTER)": {"l": 84, "w": 64, "h": 100, "weight": 76.5, "ipc": 5, "stack": True},
    "P2 ESD 2,84 - STANDARD": {"l": 110, "w": 60, "h": 80, "weight": 115.0, "ipc": 8, "stack": True},
    "P2 ESD Corner - nonstandard": {"l": 90, "w": 70, "h": 80, "weight": 104.0, "ipc": 8, "stack": True},
    "P3.9 Yestech - STANDARD": {"l": 114, "w": 60, "h": 80, "weight": 125.0, "ipc": 10, "stack": True},
    "P2.6 Yestech - INDOOR": {"l": 117, "w": 64, "h": 76, "weight": 122.0, "ipc": 10, "stack": True},
    "P2.6 Yestech - INDOOR CUBE": {"l": 117, "w": 64, "h": 76, "weight": 122.0, "ipc": 10, "stack": True},
    "P3 Yestech Corner - nonstandard": {"l": 120, "w": 60, "h": 80, "weight": 113.0, "ipc": 12, "stack": True},
    "P2.9 Yestech FLOOR - STANDARD": {"l": 114, "w": 60, "h": 76, "weight": 142.0, "ipc": 10, "stack": True},
    "P3.9 HOXLED / TRANSPARENT": {"l": 114, "w": 80, "h": 130, "weight": 144.0, "ipc": 10, "stack": True},
    "case for accessories RED": {"l": 120, "w": 60, "h": 80, "weight": 120.0, "ipc": 5, "stack": True},
    "case for accessories ARUM": {"l": 120, "w": 70, "h": 120, "weight": 140.0, "ipc": 1, "stack": True},
    "case for accessories NEC": {"l": 100, "w": 50, "h": 80, "weight": 120.0, "ipc": 3, "stack": True},
    "ELSTAR L42 LED": {"l": 80, "w": 50, "h": 50, "weight": 37.0, "ipc": 5, "stack": True},
    "CAMEO PAR 64 LED": {"l": 80, "w": 50, "h": 60, "weight": 31.0, "ipc": 6, "stack": True},
    "FLASH PAR 64 LED": {"l": 80, "w": 50, "h": 60, "weight": 47.0, "ipc": 8, "stack": True},
    "PROLIGHTS / ECLEXPO FLOOD300W / DMX5": {"l": 120, "w": 70, "h": 90, "weight": 89.5, "ipc": 5, "stack": True},
    "PROLIGHTS / ASTRA HYBRID 330 / DMX-5": {"l": 120, "w": 60, "h": 100, "weight": 120.0, "ipc": 2, "stack": True},
    "GRANDMA 2 LIGHTING": {"l": 100, "w": 81, "h": 37, "weight": 20.0, "ipc": 1, "stack": True},
    "PROLIGHTS / ECLPROFILE CT+": {"l": 1, "w": 1, "h": 1, "weight": 0.1, "ipc": 1, "stack": True},
    "PROLIGHTS / JET SPOT4Z / DMX5": {"l": 110, "w": 60, "h": 130, "weight": 130.0, "ipc": 10, "stack": True},
    "PROLIGHTS / JET WASH19 / DMX5": {"l": 120, "w": 60, "h": 123, "weight": 123.0, "ipc": 8, "stack": True},
    "PROLIGHTS / SOLAR 27Q / DMX5": {"l": 120, "w": 70, "h": 113, "weight": 113.0, "ipc": 10, "stack": True},
    "PROLIGHTS / STUDIO COB FC 150W RGB / DMX5": {"l": 140, "w": 60, "h": 95.4, "weight": 95.4, "ipc": 5, "stack": True},
    "CHAINMASTER / D8 PLUS / 320KG / 10M": {"l": 90, "w": 70, "h": 97, "weight": 97.0, "ipc": 2, "stack": True},
    "CHAINMASTER / D8 PLUS / 500KG / 32M": {"l": 90, "w": 70, "h": 98, "weight": 98.0, "ipc": 3, "stack": True},
    "MANUAL CHAIN HOIST": {"l": 30, "w": 30, "h": 40, "weight": 40.0, "ipc": 2, "stack": True},
    "speaker RCF 310": {"l": 60, "w": 40, "h": 40, "weight": 40.0, "ipc": 3, "stack": True},
    "speaker MASK 6": {"l": 40, "w": 30, "h": 60, "weight": 60.0, "ipc": 4, "stack": True},
    "truss cart 14x2 (200cm)": {"l": 200, "w": 70, "h": 350, "weight": 350.0, "ipc": 1, "stack": False},
    "truss cart 14x2 (300cm)": {"l": 300, "w": 70, "h": 350, "weight": 350.0, "ipc": 1, "stack": False},
    "truss corner": {"l": 40, "w": 40, "h": 40, "weight": 40.0, "ipc": 1, "stack": True},
    "Boxer Projector": {"l": 110, "w": 60, "h": 185, "weight": 185.0, "ipc": 1, "stack": False},
    "Beam 575 (karton)": {"l": 50, "w": 30, "h": 60, "weight": 60.0, "ipc": 3, "stack": True},
    "Laptop": {"l": 40, "w": 10, "h": 50, "weight": 50.0, "ipc": 1, "stack": True},
    "trap/ramp for van": {"l": 240, "w": 10, "h": 100, "weight": 240.0, "ipc": 1, "stack": False},
    "iiYama 46\" TOUCHSCREEN": {"l": 100, "w": 50, "h": 100, "weight": 140.0, "ipc": 2, "stack": True},
    "NEC V554 TOUCHSCREEN": {"l": 100, "w": 50, "h": 100, "weight": 140.0, "ipc": 2, "stack": True},
    "Samsung UE43": {"l": 80, "w": 50, "h": 80, "weight": 120.0, "ipc": 3, "stack": True},
    "LG 60 UH605V": {"l": 110, "w": 40, "h": 230, "weight": 160.0, "ipc": 2, "stack": True},
    "LG 65 UJ620V": {"l": 110, "w": 40, "h": 230, "weight": 160.0, "ipc": 2, "stack": True},
    "LG 75\"": {"l": 140, "w": 40, "h": 230, "weight": 210.0, "ipc": 1, "stack": True},
    "ALUSTAGE / CORNERBLOCK": {"l": 30, "w": 30, "h": 30, "weight": 10.0, "ipc": 1, "stack": True},
    "ALUSTAGE / L CORNER": {"l": 50, "w": 30, "h": 50, "weight": 5.0, "ipc": 1, "stack": True},
    "ALUSTAGE / 0,21M": {"l": 21, "w": 30, "h": 30, "weight": 3.0, "ipc": 1, "stack": True},
    "ALUSTAGE / 0,29M": {"l": 30, "w": 30, "h": 50, "weight": 4.0, "ipc": 1, "stack": True},
    "ALUSTAGE / 0,5M": {"l": 50, "w": 30, "h": 30, "weight": 4.0, "ipc": 1, "stack": True},
    "ALUSTAGE / 1M": {"l": 100, "w": 30, "h": 30, "weight": 6.0, "ipc": 1, "stack": True},
    "ALUSTAGE / 2M": {"l": 200, "w": 30, "h": 30, "weight": 11.0, "ipc": 1, "stack": True},
    "ALUSTAGE / 3M": {"l": 300, "w": 30, "h": 30, "weight": 16.0, "ipc": 1, "stack": True},
    "ALUSTAGE / T - TYPE": {"l": 50, "w": 30, "h": 50, "weight": 50.0, "ipc": 8, "stack": True},
    "ALUSTAGE / X - TYPE": {"l": 50, "w": 30, "h": 50, "weight": 6.0, "ipc": 8, "stack": True},
    "EUROTRUSS / FD34 L-90": {"l": 50, "w": 30, "h": 50, "weight": 50.0, "ipc": 8, "stack": True},
    "EUROTRUSS / HD34 L-90": {"l": 80, "w": 10, "h": 80, "weight": 80.0, "ipc": 1, "stack": True},
    "EUROTRUSS / HD34 0,5M": {"l": 50, "w": 29, "h": 29, "weight": 18.0, "ipc": 1, "stack": True},
    "EUROTRUSS / HD34 1M": {"l": 100, "w": 29, "h": 29, "weight": 18.0, "ipc": 1, "stack": True},
    "EUROTRUSS / HD34 2M": {"l": 200, "w": 29, "h": 29, "weight": 18.0, "ipc": 1, "stack": True},
    "EUROTRUSS / HD34 3M": {"l": 300, "w": 29, "h": 29, "weight": 18.0, "ipc": 1, "stack": True},
    "P2.06 / frameLED / KABINET": {"l": 86, "w": 62, "h": 100, "weight": 118.0, "ipc": 10, "stack": True},
    "P1,86 LED MODULE": {"l": 32, "w": 16, "h": 2, "weight": 0.34, "ipc": 1, "stack": True},
    "P2.0 LED SPHERE / d=1,5m": {"l": 160, "w": 160, "h": 220, "weight": 120.0, "ipc": 1, "stack": False},
    "P3.0 LED SPHERE 1 z 5": {"l": 192, "w": 192, "h": 200, "weight": 400.0, "ipc": 1, "stack": False},
    "P3.0 LED SPHERE 2 z 5": {"l": 192, "w": 192, "h": 200, "weight": 400.0, "ipc": 1, "stack": False},
    "P3.0 LED SPHERE 3 z 5": {"l": 270, "w": 101, "h": 200, "weight": 400.0, "ipc": 1, "stack": False},
    "P3.0 LED SPHERE 4 z 5": {"l": 183, "w": 182, "h": 200, "weight": 400.0, "ipc": 1, "stack": False},
    "P3.0 LED SPHERE 5 z 5": {"l": 180, "w": 120, "h": 220, "weight": 400.0, "ipc": 1, "stack": False},
    "P1.56 (stack na 2)": {"l": 120, "w": 60, "h": 90, "weight": 125.0, "ipc": 10, "stack": True},
    "CHAINMASTER D8PLUS (320KG)": {"l": 46, "w": 22, "h": 13, "weight": 30.0, "ipc": 1, "stack": True},
    "PODEST ALUDECK 2 x 1M": {"l": 200, "w": 100, "h": 20, "weight": 45.0, "ipc": 1, "stack": True},
    "ALU BLACK PIPE / 4M": {"l": 400, "w": 6, "h": 6, "weight": 6.0, "ipc": 1, "stack": True},
    "ALU BLACK PIPE / 6M": {"l": 600, "w": 6, "h": 6, "weight": 9.0, "ipc": 1, "stack": True},
    "PROLIGHTS / FLOOD300W DMX": {"l": 40, "w": 21, "h": 25, "weight": 5.0, "ipc": 1, "stack": True},
    "VOGELS / PFW 6870": {"l": 29, "w": 5, "h": 6, "weight": 23.0, "ipc": 1, "stack": True},
    "MULTIMEDIA TOTEM 55\" 4K": {"l": 100, "w": 80, "h": 200, "weight": 150.0, "ipc": 1, "stack": False},
    "DELL OPTIPLEX 7050": {"l": 19, "w": 4, "h": 19, "weight": 2.0, "ipc": 1, "stack": True},
    "P1,29 MODULED CABINET": {"l": 94, "w": 60, "h": 100, "weight": 121.0, "ipc": 8, "stack": True},
    "DICOLOR US-261": {"l": 117, "w": 58, "h": 110, "weight": 118.0, "ipc": 8, "stack": True},
    "DICOLOR US-390 (stack 2)": {"l": 110, "w": 82, "h": 110, "weight": 87.0, "ipc": 6, "stack": True},
    "KINETIC Q / WINCH (kule)": {"l": 110, "w": 56, "h": 70, "weight": 40.0, "ipc": 16, "stack": True},
    "KINETIC Q / WINCH (napęd)": {"l": 71, "w": 54, "h": 70, "weight": 20.0, "ipc": 8, "stack": True},
    "P1.9 KINETIC LED": {"l": 120, "w": 63, "h": 65, "weight": 95.0, "ipc": 2, "stack": True},
    "creaTUBE/360/1,5M": {"l": 150, "w": 30, "h": 30, "weight": 50.0, "ipc": 50, "stack": True},
    "creaTUBE/360/0,5M": {"l": 50, "w": 30, "h": 30, "weight": 50.0, "ipc": 50, "stack": True},
    "creaTUBE/360/1M": {"l": 100, "w": 30, "h": 30, "weight": 50.0, "ipc": 50, "stack": True},
    "POWERBOX RACK 63A": {"l": 71, "w": 55, "h": 70, "weight": 50.0, "ipc": 1, "stack": True},
    "CHAINMASTER D8+ 500KG 24M": {"l": 80, "w": 60, "h": 50, "weight": 110.0, "ipc": 1, "stack": True},
    "CHAINMASTER D8+ 320KG 10M": {"l": 80, "w": 60, "h": 50, "weight": 60.0, "ipc": 2, "stack": True},
    "RACK MOTOR CONTROLLER 24CH": {"l": 71, "w": 55, "h": 97, "weight": 70.0, "ipc": 50, "stack": True},
    "CHAMSYS/ QUICKQ 20": {"l": 57, "w": 35, "h": 107, "weight": 6.0, "ipc": 1, "stack": True},
    "LD SYSTEMS STINGER 8 G3": {"l": 120, "w": 40, "h": 80, "weight": 85.0, "ipc": 4, "stack": True},
    "PRESONUS STUDIOLIVE USB": {"l": 41, "w": 40, "h": 14, "weight": 18.0, "ipc": 1, "stack": True},
    "P2.9 OUTDOOR RENTAL": {"l": 120, "w": 60, "h": 80, "weight": 120.0, "ipc": 9, "stack": True},
    "TRUSS CIRCLE HD 19M": {"l": 300, "w": 60, "h": 220, "weight": 85.0, "ipc": 1, "stack": True},
    "TRUSS CIRCLE HD 15M": {"l": 300, "w": 60, "h": 220, "weight": 85.0, "ipc": 1, "stack": True},
    "TRUSS CIRCLE HD 11M": {"l": 320, "w": 60, "h": 220, "weight": 85.0, "ipc": 1, "stack": True},
    "TRUSS CIRCLE HD 8M": {"l": 320, "w": 60, "h": 220, "weight": 85.0, "ipc": 1, "stack": True},
    "TRUSS CIRCLE HD 7M": {"l": 270, "w": 60, "h": 220, "weight": 85.0, "ipc": 1, "stack": True},
    "TRUSS CIRCLE HD 6M": {"l": 240, "w": 60, "h": 220, "weight": 85.0, "ipc": 1, "stack": True},
    "TRUSS CIRCLE HD 5M": {"l": 220, "w": 60, "h": 220, "weight": 85.0, "ipc": 1, "stack": True},
    "TRUSS CIRCLE HD 4M": {"l": 300, "w": 60, "h": 160, "weight": 85.0, "ipc": 1, "stack": True},
    "ALUSTAGE / UNO TRUSS / 1": {"l": 100, "w": 5, "h": 5, "weight": 2.0, "ipc": 1, "stack": True},
    "ALUSTAGE / UNO TRUSS / 2": {"l": 200, "w": 5, "h": 5, "weight": 4.0, "ipc": 1, "stack": True},
    "ALUSTAGE / UNO TRUSS / 3": {"l": 300, "w": 5, "h": 5, "weight": 6.0, "ipc": 1, "stack": True},
    "ALUSTAGE / DUO-290 / 0,5M": {"l": 50, "w": 5, "h": 30, "weight": 2.0, "ipc": 1, "stack": True},
    "ALUSTAGE / DUO-290 / 1M": {"l": 100, "w": 5, "h": 30, "weight": 3.0, "ipc": 1, "stack": True},
    "ALUSTAGE / DUO-290 / 2M": {"l": 200, "w": 5, "h": 30, "weight": 5.0, "ipc": 1, "stack": True},
    "Własny ładunek": {"l": 1, "w": 1, "h": 1, "weight": 1.0, "ipc": 1, "stack": True}
}

# --- ALGORYTM PAKOWANIA (ODWZOROWANIE LOGIKI GEM3.HTML) ---
def simulate_packing(cargo_list, vehicle):
    all_cases = []
    for item in cargo_list:
        num_cases = math.ceil(item['qty'] / item['ipc'])
        for _ in range(num_cases):
            all_cases.append({
                "name": item['name'], "l": item['l'], "w": item['w'], "h": item['h'],
                "weight": item['weight'], "stackable": item['stack'], "area": item['l'] * item['w']
            })

    # Sortowanie FFD (First Fit Decreasing Area)
    all_cases.sort(key=lambda x: x['area'], reverse=True)

    placed_stacks = []
    unplaced = []
    spaces = [{"x": 0, "y": 0, "w": vehicle['w'], "l": vehicle['l']}]

    for case in all_cases:
        packed = False
        
        # 1. Próba dołożenia do istniejącego stosu (stackowanie)
        if case['stackable']:
            for stack in placed_stacks:
                if (stack['can_stack'] and case['l'] <= stack['l'] and case['w'] <= stack['w'] and 
                    (stack['cur_h'] + case['h']) <= vehicle['h']):
                    stack['items'].append(case)
                    stack['cur_h'] += case['h']
                    packed = True
                    break
        
        # 2. Próba znalezienia wolnego miejsca na podłodze
        if not packed:
            for i, space in enumerate(spaces):
                if ((case['l'] <= space['l'] and case['w'] <= space['w']) or 
                    (case['w'] <= space['l'] and case['l'] <= space['w'])): # Rotacja
                    
                    actual_l = case['l'] if case['l'] <= space['l'] else case['w']
                    actual_w = case['w'] if actual_l == case['l'] else case['l']

                    new_stack = {
                        "x": space['x'], "y": space['y'], "l": actual_l, "w": actual_w,
                        "cur_h": case['h'], "can_stack": case['stackable'], "items": [case]
                    }
                    placed_stacks.append(new_stack)
                    
                    # Guillotine split
                    spaces.pop(i)
                    if space['w'] - actual_w > 0:
                        spaces.append({"x": space['x'] + actual_w, "y": space['y'], "w": space['w'] - actual_w, "l": actual_l})
                    if space['l'] - actual_l > 0:
                        spaces.append({"x": space['x'], "y": space['y'] + actual_l, "w": space['w'], "l": space['l'] - actual_l})
                    
                    spaces.sort(key=lambda s: s['l'] * s['w'])
                    packed = True
                    break
        
        if not packed:
            unplaced.append(case)

    # Obliczenia wagowe i powierzchniowe
    total_weight = sum(sum(it['weight'] for it in s['items']) for s in placed_stacks)
    floor_area = sum(s['l'] * s['w'] for s in placed_stacks)
    total_vol = sum(sum(it['l']*it['w']*it['h'] for it in s['items']) for s in placed_stacks)

    return {"stacks": placed_stacks, "unplaced": unplaced, "weight": total_weight, "floor_area": floor_area, "volume": total_vol}

# --- INTERFEJS UŻYTKOWNIKA ---
st.title("🚚 Planer Załadunków SQM - Konfiguracja Logistyczna")
st.caption("Aplikacja odzwierciedla parametry z pliku gem3.html [31 palet / 12t TIR]")

if 'cargo' not in st.session_state:
    st.session_state.cargo = []

col_in, col_out = st.columns([1, 2])

with col_in:
    st.subheader("1. Pojazd")
    v_type = st.selectbox("Typ naczepy", list(VEHICLES_DATA.keys()))
    v = VEHICLES_DATA[v_type]
    st.info(f"Parametry: {v['l']}x{v['w']}x{v['h']} cm | Ładowność: {v['weight']} kg | Limit: {v['pallets']} palet")

    st.divider()
    st.subheader("2. Produkty")
    search = st.text_input("Szukaj sprzętu...")
    filtered = [k for k in PRODUCTS_DATA.keys() if search.lower() in k.lower()]
    selected = st.selectbox("Wybierz z listy", filtered)
    
    if st.button("➕ DODAJ", use_container_width=True):
        item = PRODUCTS_DATA[selected].copy()
        item['name'] = selected
        item['qty'] = 1
        st.session_state.cargo.append(item)

with col_out:
    st.subheader("3. Lista i Symulacja")
    
    if not st.session_state.cargo:
        st.info("Dodaj produkty, aby rozpocząć kalkulację.")
    else:
        for idx, it in enumerate(st.session_state.cargo):
            with st.expander(f"📦 {it['name']}", expanded=True):
                c1, c2, c3 = st.columns([2, 1, 1])
                it['qty'] = c1.number_input("Sztuk", min_value=1, value=it['qty'], key=f"q_{idx}")
                it['stack'] = c2.checkbox("Stack", value=it['stack'], key=f"s_{idx}")
                if c3.button("🗑️", key=f"rm_{idx}"):
                    st.session_state.cargo.pop(idx)
                    st.rerun()

        res = simulate_packing(st.session_state.cargo, v)

        # PODSUMOWANIE WYNIKÓW
        st.divider()
        m1, m2, m3 = st.columns(3)
        
        ldm_equiv = round(res['floor_area'] / (120 * 80), 2)
        weight_perc = round((res['weight'] / v['weight']) * 100, 1)
        
        m1.metric("Waga Całkowita", f"{res['weight']} kg", f"{weight_perc}%", delta_color="inverse")
        m2.metric("Ekwiwalent Palet", f"{ldm_equiv}", f"Limit: {v['pallets']}", delta_color="inverse")
        m3.metric("Wykorzystanie m³", f"{round((res['volume']/(v['l']*v['w']*v['h']))*100,1)}%")

        if res['weight'] > v['weight']:
            st.error(f"⚠️ PRZECIĄŻENIE! Przekroczono o {res['weight'] - v['weight']} kg.")
        if ldm_equiv > v['pallets']:
            st.warning(f"⚠️ BRAK MIEJSCA NA PODŁODZE! Przekroczono o {round(ldm_equiv - v['pallets'], 2)} palet.")

        if res['unplaced']:
            st.error(f"❌ NIE ZMIESZCZONO {len(res['unplaced'])} OBIEKTÓW!")
            for item in res['unplaced'][:10]:
                st.caption(f"- {item['name']} ({item['l']}x{item['w']} cm) - za duży lub brak miejsca")
        else:
            st.success("✅ Cały ładunek mieści się w wybranym pojeździe.")

        if st.checkbox("Pokaż listę stosów"):
            for i, s in enumerate(res['stacks']):
                st.write(f"Stos {i+1}: {s['l']}x{s['w']} cm | Wysokość: {s['cur_h']} cm | Zawiera: {len(s['items'])}x {s['items'][0]['name']}")
