import streamlit as st
import pandas as pd
import math

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="SQM Cargo Planner Pro", layout="wide", page_icon="🚚")

# --- BAZA POJAZDÓW (ZGODNIE Z PLIKIEM GEM3.HTML) ---
VEHICLES_DATA = {
    "BUS": {"pallets": 8, "weight": 1100, "l": 450, "w": 150, "h": 245},
    "Solówka 6m": {"pallets": 14, "weight": 3500, "l": 600, "w": 245, "h": 245},
    "Solówka 7m": {"pallets": 16, "weight": 3500, "l": 700, "w": 245, "h": 245},
    "FTL (Tir)": {"pallets": 31, "weight": 12000, "l": 1360, "w": 245, "h": 265},
}

# --- KOMPLETNA BAZA PRODUKTÓW ---
# Klucz 'ipc' oznacza Items Per Case (sztuk w skrzyni)
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
    "PROLIGHTS / ECLEXPO FLOOD300W": {"l": 120, "w": 70, "h": 90, "weight": 89.5, "ipc": 5, "stack": True},
    "PROLIGHTS / ASTRA HYBRID 330": {"l": 120, "w": 60, "h": 100, "weight": 120.0, "ipc": 2, "stack": True},
    "GRANDMA 2 LIGHTING": {"l": 100, "w": 81, "h": 37, "weight": 20.0, "ipc": 1, "stack": True},
    "PROLIGHTS / ECLPROFILE CT+": {"l": 1, "w": 1, "h": 1, "weight": 0.1, "ipc": 1, "stack": True},
    "PROLIGHTS / JET SPOT4Z": {"l": 110, "w": 60, "h": 130, "weight": 130.0, "ipc": 10, "stack": True},
    "PROLIGHTS / JET WASH19": {"l": 120, "w": 60, "h": 123, "weight": 123.0, "ipc": 8, "stack": True},
    "PROLIGHTS / SOLAR 27Q": {"l": 120, "w": 70, "h": 113, "weight": 113.0, "ipc": 10, "stack": True},
    "PROLIGHTS / STUDIO COB FC 150W": {"l": 140, "w": 60, "h": 95.4, "weight": 95.4, "ipc": 5, "stack": True},
    "CHAINMASTER / D8 PLUS / 320KG": {"l": 90, "w": 70, "h": 97, "weight": 97.0, "ipc": 2, "stack": True},
    "CHAINMASTER / D8 PLUS / 500KG": {"l": 90, "w": 70, "h": 98, "weight": 98.0, "ipc": 3, "stack": True},
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
    "ALUSTAGE / 1M": {"l": 100, "w": 30, "h": 30, "weight": 6.0, "ipc": 1, "stack": True},
    "ALUSTAGE / 2M": {"l": 200, "w": 30, "h": 30, "weight": 11.0, "ipc": 1, "stack": True},
    "ALUSTAGE / 3M": {"l": 300, "w": 30, "h": 30, "weight": 16.0, "ipc": 1, "stack": True},
    "EUROTRUSS / HD34 2M": {"l": 200, "w": 29, "h": 29, "weight": 18.0, "ipc": 1, "stack": True},
    "EUROTRUSS / HD34 3M": {"l": 300, "w": 29, "h": 29, "weight": 18.0, "ipc": 1, "stack": True},
    "PODEST ALUDECK 2 x 1M": {"l": 200, "w": 100, "h": 20, "weight": 45.0, "ipc": 1, "stack": True},
    "ALU BLACK PIPE / 6M": {"l": 600, "w": 6, "h": 6, "weight": 9.0, "ipc": 1, "stack": True},
    "MULTIMEDIA TOTEM 55\" 4K": {"l": 100, "w": 80, "h": 200, "weight": 150.0, "ipc": 1, "stack": False},
    "P2.9 OUTDOOR RENTAL": {"l": 120, "w": 60, "h": 80, "weight": 120.0, "ipc": 9, "stack": True},
    "Własny ładunek": {"l": 100, "w": 100, "h": 100, "weight": 100.0, "ipc": 1, "stack": True}
}

# --- ALGORYTM PAKOWANIA (WZMOCNIONY O OBSŁUGĘ BŁĘDÓW) ---
def simulate_packing(cargo_list, vehicle):
    all_cases = []
    for item in cargo_list:
        # POBIERANIE IPC Z OBSŁUGĄ RÓŻNYCH NAZW KLUCZY
        ipc_value = item.get('ipc', item.get('items_per_case', 1))
        
        num_cases = math.ceil(item['qty'] / ipc_value)
        for _ in range(num_cases):
            all_cases.append({
                "name": item['name'], 
                "l": item['l'], "w": item['w'], "h": item['h'],
                "weight": item['weight'], 
                "stackable": item.get('stack', True), 
                "area": item['l'] * item['w']
            })

    # Sortowanie FFD (Największe powierzchnie na początek)
    all_cases.sort(key=lambda x: x['area'], reverse=True)

    placed_stacks = []
    unplaced = []
    # Guillotine-based available spaces
    spaces = [{"x": 0, "y": 0, "w": vehicle['w'], "l": vehicle['l']}]

    for case in all_cases:
        packed = False
        
        # 1. Próba stackowania na istniejących stosach
        if case['stackable']:
            for stack in placed_stacks:
                if (stack['can_stack'] and case['l'] <= stack['l'] and case['w'] <= stack['w'] and 
                    (stack['cur_h'] + case['h']) <= vehicle['h']):
                    stack['items'].append(case)
                    stack['cur_h'] += case['h']
                    packed = True
                    break
        
        # 2. Próba znalezienia miejsca na podłodze (z rotacją)
        if not packed:
            for i, space in enumerate(spaces):
                # Sprawdzamy orientację normalną i obróconą o 90 stopni
                for l_orient, w_orient in [(case['l'], case['w']), (case['w'], case['l'])]:
                    if l_orient <= space['l'] and w_orient <= space['w']:
                        new_stack = {
                            "x": space['x'], "y": space['y'], "l": l_orient, "w": w_orient,
                            "cur_h": case['h'], "can_stack": case['stackable'], "items": [case]
                        }
                        placed_stacks.append(new_stack)
                        
                        # Podział wolnej przestrzeni (Guillotine Split)
                        spaces.pop(i)
                        if space['w'] - w_orient > 0:
                            spaces.append({"x": space['x'] + w_orient, "y": space['y'], "w": space['w'] - w_orient, "l": l_orient})
                        if space['l'] - l_orient > 0:
                            spaces.append({"x": space['x'], "y": space['y'] + l_orient, "w": space['w'], "l": space['l'] - l_orient})
                        
                        spaces.sort(key=lambda s: s['l'] * s['w'])
                        packed = True
                        break
                if packed: break
        
        if not packed:
            unplaced.append(case)

    # Statystyki końcowe
    total_weight = sum(sum(it['weight'] for it in s['items']) for s in placed_stacks)
    floor_area = sum(s['l'] * s['w'] for s in placed_stacks)
    total_vol = sum(sum(it['l']*it['w']*it['h'] for it in s['items']) for s in placed_stacks)

    return {"stacks": placed_stacks, "unplaced": unplaced, "weight": total_weight, "floor_area": floor_area, "volume": total_vol}

# --- UI STREAMLIT ---
st.title("🚚 SQM Cargo Planner Pro")
st.caption("System logistyczny SQM Multimedia Solutions - Pełna zgodność z gem3.html")

if 'cargo' not in st.session_state:
    st.session_state.cargo = []

col_in, col_out = st.columns([1, 2])

with col_in:
    st.subheader("1. Parametry Transportu")
    v_type = st.selectbox("Wybierz pojazd", list(VEHICLES_DATA.keys()))
    v = VEHICLES_DATA[v_type]
    
    st.info(f"🚚 **{v_type}**\n- Max Masa: {v['weight']} kg\n- Max Palet: {v['pallets']}\n- Wymiary: {v['l']}x{v['w']}x{v['h']} cm")

    st.divider()
    st.subheader("2. Dodaj Sprzęt")
    search = st.text_input("Szukaj w bazie...")
    filtered = [k for k in PRODUCTS_DATA.keys() if search.lower() in k.lower()]
    selected = st.selectbox("Wyniki wyszukiwania", filtered)
    
    if st.button("➕ DODAJ DO LISTY", use_container_width=True):
        item = PRODUCTS_DATA[selected].copy()
        item['name'] = selected
        item['qty'] = 1
        st.session_state.cargo.append(item)

with col_out:
    st.subheader("3. Lista Załadunkowa i Symulacja")
    
    if not st.session_state.cargo:
        st.warning("Lista jest pusta. Dodaj produkty z panelu po lewej.")
    else:
        for idx, it in enumerate(st.session_state.cargo):
            with st.expander(f"📦 {it['name']}", expanded=True):
                c1, c2, c3 = st.columns([2, 1, 1])
                it['qty'] = c1.number_input("Sztuk", min_value=1, value=it['qty'], key=f"q_{idx}")
                it['stack'] = c2.checkbox("Stackuj", value=it.get('stack', True), key=f"s_{idx}")
                if c3.button("🗑️ Usuń", key=f"rm_{idx}"):
                    st.session_state.cargo.pop(idx)
                    st.rerun()

        # URUCHOMIENIE SYMULACJI
        res = simulate_packing(st.session_state.cargo, v)

        # WYNIKI
        st.divider()
        m1, m2, m3 = st.columns(3)
        
        ldm_equiv = round(res['floor_area'] / (120 * 80), 2)
        weight_perc = round((res['weight'] / v['weight']) * 100, 1)
        
        m1.metric("Masa Całkowita", f"{res['weight']} kg", f"{weight_perc}%", delta_color="inverse")
        m2.metric("Zajęte Palety", f"{ldm_equiv}", f"Limit: {v['pallets']}", delta_color="inverse")
        m3.metric("Wypełnienie m³", f"{round((res['volume']/(v['l']*v['w']*v['h']))*100,1)}%")

        # OSTRZEŻENIA
        if res['weight'] > v['weight']:
            st.error(f"🚨 PRZECIĄŻENIE! Przekroczono ładowność o {res['weight'] - v['weight']} kg.")
        if ldm_equiv > v['pallets']:
            st.warning(f"🚨 BRAK MIEJSCA! Przekroczono limit palet o {round(ldm_equiv - v['pallets'], 2)}.")

        if res['unplaced']:
            st.error(f"❌ NIE ZMIESZCZONO {len(res['unplaced'])} SKRZYŃ!")
            for item in res['unplaced'][:5]:
                st.caption(f"- {item['name']} ({item['l']}x{item['w']} cm) - brak wolnej powierzchni")
        else:
            st.success("✅ Wszystkie elementy zostały rozmieszczone.")

        if st.checkbox("Pokaż Raport Stosów (Layout)"):
            for i, s in enumerate(res['stacks']):
                st.write(f"**Stos {i+1}:** {s['l']}x{s['w']} cm | Wys: {s['cur_h']} cm | Zawiera: {len(s['items'])} szt.")
