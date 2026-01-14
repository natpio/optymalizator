import streamlit as st
import pandas as pd
import math

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Planer Załadunku SQM", layout="wide", page_icon="🚚")

# --- KOMPLETNA BAZA PRODUKTÓW (119 POZYCJI) ---
# Dane przeniesione 1:1 z Twojego pliku HTML
PRODUCTS_DATA = {
    # Monitory
    "17-23\" - plastic case": {"l": 80, "w": 60, "h": 20, "weight": 20.0, "items_per_case": 1, "stack": True},
    "24-32\" - plastic case": {"l": 60, "w": 40, "h": 20, "weight": 15.0, "items_per_case": 1, "stack": True},
    "32\" - triple - STANDARD": {"l": 90, "w": 50, "h": 70, "weight": 50.0, "items_per_case": 3, "stack": True},
    "43\" - triple - STANDARD": {"l": 120, "w": 50, "h": 80, "weight": 90.0, "items_per_case": 3, "stack": True},
    "45\"-55\" - double - STANDARD": {"l": 140, "w": 50, "h": 100, "weight": 150.0, "items_per_case": 2, "stack": True},
    "60-65\" - double - STANDARD": {"l": 160, "w": 40, "h": 110, "weight": 200.0, "items_per_case": 2, "stack": True},
    "75-86\" - double - STANDARD": {"l": 210, "w": 40, "h": 140, "weight": 230.0, "items_per_case": 2, "stack": True},
    "98\" - double - STANDARD": {"l": 250, "w": 70, "h": 170, "weight": 400.0, "items_per_case": 1, "stack": True},
    "NEC E326 - STANDARD": {"l": 70, "w": 50, "h": 70, "weight": 90.0, "items_per_case": 3, "stack": True},
    "NEC C431 - STANDARD": {"l": 80, "w": 50, "h": 80, "weight": 120.0, "items_per_case": 3, "stack": True},
    "NEC C501 - STANDARD": {"l": 100, "w": 50, "h": 100, "weight": 140.0, "items_per_case": 2, "stack": True},
    "NEC C551 - STANDARD": {"l": 100, "w": 50, "h": 100, "weight": 140.0, "items_per_case": 2, "stack": True},
    "SAMSUNG series 7 - STANDARD": {"l": 110, "w": 50, "h": 60, "weight": 160.0, "items_per_case": 2, "stack": True},
    "NEC C861 86\" - STANDARD": {"l": 140, "w": 40, "h": 140, "weight": 210.0, "items_per_case": 1, "stack": True},
    "NEC C981 98\" - STANDARD": {"l": 170, "w": 70, "h": 170, "weight": 250.0, "items_per_case": 1, "stack": True},
    "NEC X981 98\" TOUCHSCREEN - STANDARD": {"l": 170, "w": 70, "h": 170, "weight": 250.0, "items_per_case": 1, "stack": True},
    "iiYama 46\" - TOUCHSCREEN - STANDARD": {"l": 100, "w": 50, "h": 100, "weight": 140.0, "items_per_case": 2, "stack": True},
    "NEC V554 TOUCHSCREEN - STANDARD": {"l": 100, "w": 50, "h": 100, "weight": 140.0, "items_per_case": 2, "stack": True},
    "Samsung UE43 - STANDARD": {"l": 80, "w": 50, "h": 80, "weight": 120.0, "items_per_case": 3, "stack": True},
    "LG 60 UH605V - STANDARD": {"l": 110, "w": 40, "h": 110, "weight": 160.0, "items_per_case": 2, "stack": True},
    "LG 65 UJ620V - STANDARD": {"l": 110, "w": 40, "h": 110, "weight": 160.0, "items_per_case": 2, "stack": True},
    "LG 75\" - STANDARD": {"l": 140, "w": 40, "h": 140, "weight": 210.0, "items_per_case": 1, "stack": True},
    "MULTIMEDIA TOTEM 55\"": {"l": 100, "w": 60, "h": 210, "weight": 210.0, "items_per_case": 1, "stack": False},
    "MULTIMEDIA TOTEM / 55\" / 4K": {"l": 100, "w": 80, "h": 200, "weight": 150.0, "items_per_case": 1, "stack": False},

    # LED
    "P1 lub 1.58 ABSEN": {"l": 108, "w": 71, "h": 62, "weight": 103.0, "items_per_case": 8, "stack": True},
    "P1.9 UNILUMIN UPAD IV / S-FLEX": {"l": 117, "w": 57, "h": 79, "weight": 115.0, "items_per_case": 8, "stack": True},
    "P2.6 UNILUMIN UPAD IV": {"l": 117, "w": 57, "h": 79, "weight": 116.0, "items_per_case": 8, "stack": True},
    "P2.6 UNILUMIN UPAD IV / C-CUBE": {"l": 117, "w": 57, "h": 79, "weight": 125.0, "items_per_case": 8, "stack": True},
    "P2.6 UNILUMIN UPAD IV / S-FLEX": {"l": 117, "w": 57, "h": 79, "weight": 121.0, "items_per_case": 8, "stack": True},
    "P2.06 frameLED (STANDARD / CORNERS)": {"l": 86, "w": 62, "h": 75, "weight": 118.0, "items_per_case": 10, "stack": True},
    "P2.06 frameLED (CURVED INNER / OUTER)": {"l": 84, "w": 64, "h": 76, "weight": 76.5, "items_per_case": 5, "stack": True},
    "P2 ESD 2,84 - STANDARD": {"l": 110, "w": 60, "h": 80, "weight": 115.0, "items_per_case": 8, "stack": True},
    "P2 ESD Corner - nonstandard": {"l": 90, "w": 70, "h": 80, "weight": 104.0, "items_per_case": 8, "stack": True},
    "P3.9 Yestech - STANDARD": {"l": 114, "w": 60, "h": 80, "weight": 125.0, "items_per_case": 10, "stack": True},
    "P2.6 Yestech - INDOOR": {"l": 117, "w": 64, "h": 76, "weight": 122.0, "items_per_case": 10, "stack": True},
    "P2.6 Yestech - INDOOR CUBE": {"l": 117, "w": 64, "h": 76, "weight": 122.0, "items_per_case": 10, "stack": True},
    "P3 Yestech Corner - nonstandard": {"l": 120, "w": 60, "h": 80, "weight": 113.0, "items_per_case": 12, "stack": True},
    "P2.9 Yestech FLOOR - STANDARD": {"l": 114, "w": 60, "h": 76, "weight": 142.0, "items_per_case": 10, "stack": True},
    "P3.9 HOXLED / TRANSPARENT": {"l": 114, "w": 80, "h": 130, "weight": 144.0, "items_per_case": 10, "stack": True},
    "P2.06 / frameLED / KABINET": {"l": 86, "w": 62, "h": 75, "weight": 118.0, "items_per_case": 10, "stack": True},
    "P1,86 LED MODULE / 320 x160MM": {"l": 32, "w": 16, "h": 2, "weight": 0.34, "items_per_case": 1, "stack": True},
    "P2.0 LED SPHERE / d=1,5m": {"l": 160, "w": 160, "h": 220, "weight": 120.0, "items_per_case": 1, "stack": False},
    "P3.0 LED SPHERE 1 z 5": {"l": 192, "w": 192, "h": 200, "weight": 400.0, "items_per_case": 1, "stack": False},
    "P3.0 LED SPHERE 2 z 5": {"l": 192, "w": 192, "h": 200, "weight": 400.0, "items_per_case": 1, "stack": False},
    "P3.0 LED SPHERE 3 z 5": {"l": 270, "w": 101, "h": 200, "weight": 400.0, "items_per_case": 1, "stack": False},
    "P3.0 LED SPHERE 4 z 5": {"l": 183, "w": 182, "h": 200, "weight": 400.0, "items_per_case": 1, "stack": False},
    "P3.0 LED SPHERE 5 z 5": {"l": 180, "w": 120, "h": 220, "weight": 400.0, "items_per_case": 1, "stack": False},
    "P1.56 stackować na 2(!)": {"l": 120, "w": 60, "h": 90, "weight": 125.0, "items_per_case": 10, "stack": True},
    "P1,29 lub 1.2 MODULED CABINET": {"l": 94, "w": 60, "h": 75, "weight": 121.0, "items_per_case": 8, "stack": True},
    "DICOLOR US-261": {"l": 117, "w": 58, "h": 76, "weight": 118.0, "items_per_case": 8, "stack": True},
    "DICOLOR US-390": {"l": 110, "w": 82, "h": 73, "weight": 87.0, "items_per_case": 6, "stack": True},
    "P1.9 KINETIC LED CABINET": {"l": 120, "w": 63, "h": 65, "weight": 95.0, "items_per_case": 2, "stack": True},
    "P2.9 OUTDOOR RENTAL": {"l": 120, "w": 60, "h": 80, "weight": 120.0, "items_per_case": 9, "stack": True},

    # Akcesoria i Lighting
    "case for accessories RED": {"l": 120, "w": 60, "h": 80, "weight": 120.0, "items_per_case": 5, "stack": True},
    "case for accessories ARUM": {"l": 120, "w": 70, "h": 120, "weight": 140.0, "items_per_case": 1, "stack": True},
    "case for accessories NEC": {"l": 100, "w": 50, "h": 80, "weight": 120.0, "items_per_case": 3, "stack": True},
    "ELSTAR L42 LED": {"l": 80, "w": 50, "h": 50, "weight": 37.0, "items_per_case": 5, "stack": True},
    "CAMEO PAR 64 LED": {"l": 80, "w": 50, "h": 60, "weight": 31.0, "items_per_case": 6, "stack": True},
    "FLASH PAR 64 LED": {"l": 80, "w": 50, "h": 60, "weight": 47.0, "items_per_case": 8, "stack": True},
    "PROLIGHTS / ECLEXPO FLOOD300W": {"l": 120, "w": 70, "h": 90, "weight": 89.5, "items_per_case": 5, "stack": True},
    "PROLIGHTS / ECLPROFILE CT+": {"l": 1, "w": 1, "h": 1, "weight": 0.1, "items_per_case": 1, "stack": True},
    "PROLIGHTS / JET SPOT4Z": {"l": 110, "w": 60, "h": 130, "weight": 130.0, "items_per_case": 10, "stack": True},
    "PROLIGHTS / JET WASH19": {"l": 120, "w": 60, "h": 123, "weight": 123.0, "items_per_case": 8, "stack": True},
    "PROLIGHTS / SOLAR 27Q": {"l": 120, "w": 70, "h": 113, "weight": 113.0, "items_per_case": 10, "stack": True},
    "PROLIGHTS / STUDIO COB FC 150W": {"l": 140, "w": 60, "h": 95.4, "weight": 95.4, "items_per_case": 5, "stack": True},
    "CHAINMASTER / D8 PLUS / 320KG": {"l": 90, "w": 70, "h": 97, "weight": 97.0, "items_per_case": 2, "stack": True},
    "CHAINMASTER / D8 PLUS / 500KG": {"l": 90, "w": 70, "h": 98, "weight": 98.0, "items_per_case": 3, "stack": True},
    "MANUAL CHAIN HOIST": {"l": 30, "w": 30, "h": 40, "weight": 40.0, "items_per_case": 2, "stack": True},
    "speaker RCF 310": {"l": 60, "w": 40, "h": 40, "weight": 40.0, "items_per_case": 3, "stack": True},
    "speaker MASK 6": {"l": 40, "w": 30, "h": 60, "weight": 60.0, "items_per_case": 4, "stack": True},
    "truss cart 14x2 (200cm)": {"l": 200, "w": 70, "h": 350, "weight": 350.0, "items_per_case": 1, "stack": False},
    "truss cart 14x2 (300cm)": {"l": 300, "w": 70, "h": 350, "weight": 350.0, "items_per_case": 1, "stack": False},
    "truss corner": {"l": 40, "w": 40, "h": 40, "weight": 40.0, "items_per_case": 1, "stack": True},
    "Boxer Projector": {"l": 110, "w": 60, "h": 185, "weight": 185.0, "items_per_case": 1, "stack": False},
    "Beam 575 (karton)": {"l": 50, "w": 30, "h": 60, "weight": 60.0, "items_per_case": 3, "stack": True},
    "Laptop": {"l": 40, "w": 10, "h": 50, "weight": 50.0, "items_per_case": 1, "stack": True},
    "trap/ramp for van": {"l": 240, "w": 10, "h": 100, "weight": 240.0, "items_per_case": 1, "stack": False},
    "ALUSTAGE / CORNERBLOCK": {"l": 30, "w": 30, "h": 30, "weight": 10.0, "items_per_case": 1, "stack": True},
    "ALUSTAGE / L CORNER": {"l": 50, "w": 30, "h": 50, "weight": 5.0, "items_per_case": 1, "stack": True},
    "ALUSTAGE / 0,21M": {"l": 21, "w": 30, "h": 30, "weight": 3.0, "items_per_case": 1, "stack": True},
    "ALUSTAGE / 0,29M": {"l": 30, "w": 30, "h": 50, "weight": 4.0, "items_per_case": 1, "stack": True},
    "ALUSTAGE / 0,5M": {"l": 50, "w": 30, "h": 30, "weight": 4.0, "items_per_case": 1, "stack": True},
    "ALUSTAGE / 1M": {"l": 100, "w": 30, "h": 30, "weight": 6.0, "items_per_case": 1, "stack": True},
    "ALUSTAGE / 2M": {"l": 200, "w": 30, "h": 30, "weight": 11.0, "items_per_case": 1, "stack": True},
    "ALUSTAGE / 3M": {"l": 300, "w": 30, "h": 30, "weight": 16.0, "items_per_case": 1, "stack": True},
    "ALUSTAGE / T - TYPE": {"l": 50, "w": 30, "h": 50, "weight": 50.0, "items_per_case": 8, "stack": True},
    "ALUSTAGE / X - TYPE": {"l": 50, "w": 30, "h": 50, "weight": 6.0, "items_per_case": 8, "stack": True},
    "EUROTRUSS / FD34 L-90": {"l": 50, "w": 30, "h": 50, "weight": 50.0, "items_per_case": 8, "stack": True},
    "EUROTRUSS / HD34 L-90": {"l": 80, "w": 10, "h": 80, "weight": 80.0, "items_per_case": 1, "stack": True},
    "EUROTRUSS / HD34 0,5M": {"l": 50, "w": 29, "h": 29, "weight": 18.0, "items_per_case": 1, "stack": True},
    "EUROTRUSS / HD34 1M": {"l": 100, "w": 29, "h": 29, "weight": 18.0, "items_per_case": 1, "stack": True},
    "EUROTRUSS / HD34 2M": {"l": 200, "w": 29, "h": 29, "weight": 18.0, "items_per_case": 1, "stack": True},
    "EUROTRUSS / HD34 3M": {"l": 300, "w": 29, "h": 29, "weight": 18.0, "items_per_case": 1, "stack": True},
    "PROLIGHTS / ASTRA HYBRID 330": {"l": 70, "w": 50, "h": 70, "weight": 50.0, "items_per_case": 5, "stack": True},
    "PROLIGHTS / EclEXPO FLOOD300FC": {"l": 30, "w": 30, "h": 30, "weight": 40.0, "items_per_case": 3, "stack": True},
    "CAMEO PAR-64 18x8W RGBW": {"l": 60, "w": 50, "h": 50, "weight": 80.0, "items_per_case": 3, "stack": True},
    "PROLIGHTS / JET SPOT4Z (DMX5)": {"l": 80, "w": 60, "h": 80, "weight": 140.0, "items_per_case": 3, "stack": True},
    "TRUSS x HANGED CIRCLE Ø5m": {"l": 300, "w": 80, "h": 170, "weight": 128.0, "items_per_case": 1, "stack": False},
    "TRUSS x HANGED CIRCLE Ø6m": {"l": 300, "w": 80, "h": 210, "weight": 140.0, "items_per_case": 1, "stack": False},
    "TRUSS x HANGED CIRCLE Ø11m": {"l": 300, "w": 80, "h": 210, "weight": 200.0, "items_per_case": 1, "stack": False},
    "TRUSS x HANGED CIRCLE Ø19m": {"l": 320, "w": 80, "h": 230, "weight": 220.0, "items_per_case": 1, "stack": False},
    "CHAINMASTER D8PLUS (320KG)": {"l": 46, "w": 22, "h": 13, "weight": 30.0, "items_per_case": 1, "stack": True},
    "PODEST ALUDECK LIGHT 2 x 1M": {"l": 200, "w": 100, "h": 20, "weight": 45.0, "items_per_case": 1, "stack": True},
    "ALUMINIUM BLACK PIPE / 4M": {"l": 400, "w": 6, "h": 6, "weight": 6.0, "items_per_case": 1, "stack": True},
    "ALUMINIUM BLACK PIPE / 6M": {"l": 600, "w": 6, "h": 6, "weight": 9.0, "items_per_case": 1, "stack": True},
    "PROLIGHTS / ECLEXPO FLOOD300W (DMX)": {"l": 40, "w": 21, "h": 25, "weight": 5.0, "items_per_case": 1, "stack": True},
    "VOGELS / PFW 6870 BLACK": {"l": 29, "w": 5, "h": 6, "weight": 23.0, "items_per_case": 1, "stack": True},
    "DELL OPTIPLEX 7050 MICRO": {"l": 19, "w": 4, "h": 19, "weight": 2.0, "items_per_case": 1, "stack": True},
    "KINETIC Q / WINCH DMX (kule)": {"l": 110, "w": 56, "h": 70, "weight": 40.0, "items_per_case": 16, "stack": True},
    "KINETIC Q / WINCH DMX (napęd)": {"l": 71, "w": 54, "h": 70, "weight": 20.0, "items_per_case": 8, "stack": True},
    "creaTUBE/360/1,5M": {"l": 150, "w": 30, "h": 30, "weight": 50.0, "items_per_case": 50, "stack": True},
    "creaTUBE/360/0,5M": {"l": 50, "w": 30, "h": 30, "weight": 50.0, "items_per_case": 50, "stack": True},
    "creaTUBE/360/1M": {"l": 100, "w": 30, "h": 30, "weight": 50.0, "items_per_case": 50, "stack": True},
    "POWERBOX RACK 63A": {"l": 71, "w": 55, "h": 70, "weight": 50.0, "items_per_case": 1, "stack": True},
    "CHAINMASTER D8 PLUS 500 KG 24M": {"l": 80, "w": 60, "h": 50, "weight": 110.0, "items_per_case": 1, "stack": True},
    "CHAINMASTER D8 PLUS 320 KG 10M": {"l": 80, "w": 60, "h": 50, "weight": 60.0, "items_per_case": 2, "stack": True},
    "RACK MOTOR CONTROLLER 24 CHANNEL": {"l": 71, "w": 55, "h": 97, "weight": 70.0, "items_per_case": 50, "stack": True},
    "CHAMSYS/ QUICKQ 20": {"l": 57, "w": 35, "h": 107, "weight": 6.0, "items_per_case": 1, "stack": True},
    "LD SYSTEMS STINGER / 8 G3": {"l": 120, "w": 40, "h": 80, "weight": 85.0, "items_per_case": 4, "stack": True},
    "Własny ładunek": {"l": 1, "w": 1, "h": 1, "weight": 1.0, "items_per_case": 1, "stack": True}
}

VEHICLES_DATA = {
    "BUS": {"pallets": 8, "weight": 1100, "l": 450, "w": 150, "h": 245},
    "Solówka 6m": {"pallets": 14, "weight": 3500, "l": 600, "w": 245, "h": 245},
    "Solówka 7m": {"pallets": 16, "weight": 3500, "l": 700, "w": 245, "h": 245},
    "FTL (Tir)": {"pallets": 31, "weight": 12000, "l": 1360, "w": 245, "h": 245},
}

EURO_PALLET_AREA = 120 * 80  # cm2

# --- UI APLIKACJI ---
st.title("🚚 Planer Załadunków SQM Multimedia")
st.markdown("---")

if 'cargo_list' not in st.session_state:
    st.session_state.cargo_list = []

col_config, col_results = st.columns([1, 2])

with col_config:
    st.header("1. Konfiguracja")
    v_type = st.selectbox("Wybierz typ pojazdu", list(VEHICLES_DATA.keys()))
    v = VEHICLES_DATA[v_type]
    
    st.info(f"**Limit:** {v['weight']}kg | {v['pallets']} palet | {v['l']}x{v['w']}x{v['h']} cm")
    
    st.divider()
    st.header("2. Dodaj ładunek")
    
    # Wyszukiwarka produktów
    search_query = st.text_input("Szukaj sprzętu (np. NEC, LED, P2.6)...")
    filtered_options = [k for k in PRODUCTS_DATA.keys() if search_query.lower() in k.lower()]
    
    selected_name = st.selectbox("Wybierz z bazy danych", filtered_options)
    
    if st.button("➕ Dodaj do listy załadunkowej", use_container_width=True):
        new_item = PRODUCTS_DATA[selected_name].copy()
        new_item['name'] = selected_name
        new_item['id'] = len(st.session_state.cargo_list)
        st.session_state.cargo_list.append(new_item)

with col_results:
    st.header("3. Twoja naczepa")
    
    if not st.session_state.cargo_list:
        st.warning("Lista załadunkowa jest pusta. Dodaj produkty z panelu po lewej.")
    else:
        total_weight = 0
        total_area = 0
        final_packing_list = []

        # Tabela edycji
        for i, item in enumerate(st.session_state.cargo_list):
            with st.expander(f"📦 {item['name']}", expanded=True):
                c1, c2, c3, c4 = st.columns(4)
                l = c1.number_input("Długość (cm)", value=int(item['l']), key=f"l_{i}")
                w = c2.number_input("Szerokość (cm)", value=int(item['w']), key=f"w_{i}")
                h = c3.number_input("Wysokość (cm)", value=int(item['h']), key=f"h_{i}")
                wg = c4.number_input("Waga (kg)", value=float(item['weight']), key=f"wg_{i}")

                q1, q2, q3 = st.columns([2, 1, 1])
                qty = q1.number_input("Ilość sztuk sprzętu", min_value=1, value=1, key=f"qty_{i}")
                stk = q2.checkbox("Stackuj", value=item['stack'], key=f"stk_{i}")
                if q3.button("🗑️ Usuń", key=f"del_{i}"):
                    st.session_state.cargo_list.pop(i)
                    st.rerun()

                # Obliczenia dla danej pozycji
                num_cases = math.ceil(qty / item['items_per_case'])
                total_weight += (wg * num_cases)
                
                # Uproszczona logika zajętości podłogi (uwzględniająca stackowanie)
                if not stk:
                    total_area += (l * w * num_cases)
                else:
                    # Zakładamy, że przy stackowaniu oszczędzamy 50% powierzchni podłogi 
                    # (można to rozbudować o realną wysokość naczepy)
                    total_area += (l * w * math.ceil(num_cases / 2))

        # PODSUMOWANIE
        st.divider()
        m1, m2, m3, m4 = st.columns(4)
        
        pallet_equiv = round(total_area / EURO_PALLET_AREA, 2)
        weight_perc = round((total_weight / v['weight']) * 100, 1)
        
        m1.metric("Waga całkowita", f"{total_weight} kg", f"{weight_perc}%")
        m2.metric("Miejsca paletowe", f"{pallet_equiv}", f"Limit: {v['pallets']}")
        m3.metric("Zajęta pow.", f"{round(total_area/10000, 1)} m²")
        m4.metric("Liczba casów", f"{len(st.session_state.cargo_list)}")

        if total_weight > v['weight'] or pallet_equiv > v['pallets']:
            st.error("⚠️ UWAGA: Załadunek przekracza dopuszczalne parametry pojazdu!")
        else:
            st.success("✅ Ładunek mieści się w parametrach pojazdu.")

        if st.button("🔄 Wyczyść wszystko"):
            st.session_state.cargo_list = []
            st.rerun()

st.sidebar.markdown("""
### O aplikacji
To narzędzie zostało stworzone dla **SQM Multimedia Solutions** do szybkiej oceny zapotrzebowania transportowego. 
Logika obliczeń bazuje na ekwiwalencie powierzchni paletowej i dopuszczalnej ładowności.
""")
