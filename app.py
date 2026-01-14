import streamlit as st
import pandas as pd
import math

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Planer Załadunków - SQM", layout="wide")

# --- BAZA DANYCH ---
PRODUCTS_DATA = {
    "17-23\" - plastic case": {"length": 80, "width": 60, "height": 20, "weight": 20, "items_per_case": 1, "stackable": True},
    "24-32\" - plastic case": {"length": 60, "width": 40, "height": 20, "weight": 15, "items_per_case": 1, "stackable": True},
    "32\" - triple - STANDARD": {"length": 90, "width": 50, "height": 70, "weight": 50, "items_per_case": 3, "stackable": True},
    "43\" - triple - STANDARD": {"length": 120, "width": 50, "height": 80, "weight": 90, "items_per_case": 3, "stackable": True},
    "45\"-55\" - double - STANDARD": {"length": 140, "width": 50, "height": 100, "weight": 150, "items_per_case": 2, "stackable": True},
    "60-65\" - double - STANDARD": {"length": 160, "width": 40, "height": 110, "weight": 200, "items_per_case": 2, "stackable": True},
    "75-86\" - double - STANDARD": {"length": 210, "width": 40, "height": 140, "weight": 230, "items_per_case": 2, "stackable": True},
    "98\" - double - STANDARD": {"length": 250, "width": 70, "height": 170, "weight": 400, "items_per_case": 1, "stackable": True},
    "MULTIMEDIA TOTEM 55\"": {"length": 100, "width": 60, "height": 210, "weight": 210, "items_per_case": 1, "stackable": False},
    "PODEST ALUDECK LIGHT 2 x 1M": {"length": 200, "width": 100, "height": 20, "weight": 45, "items_per_case": 1, "stackable": True},
    "Własny ładunek": {"length": 0, "width": 0, "height": 0, "weight": 0, "items_per_case": 1, "stackable": True}
}

VEHICLES_DATA = {
    "BUS": {"pallets": 8, "weight": 1100, "l": 450, "w": 150, "h": 245},
    "Solówka 6m": {"pallets": 14, "weight": 3500, "l": 600, "w": 245, "h": 245},
    "Solówka 7m": {"pallets": 16, "weight": 3500, "l": 700, "w": 245, "h": 245},
    "FTL (Tir)": {"pallets": 33, "weight": 24000, "l": 1360, "w": 245, "h": 245},
}

EURO_PALLET_AREA = 120 * 80

# --- UI APLIKACJI ---
st.title("🚚 Planer Załadunku SQM Multimedia")
st.markdown("Narzędzie do optymalizacji przestrzeni na naczepie.")

col1, col2 = st.columns([1, 2])

with col1:
    st.header("1. Parametry transportu")
    v_type = st.selectbox("Wybierz pojazd", list(VEHICLES_DATA.keys()))
    v = VEHICLES_DATA[v_type]
    
    st.info(f"Limit: {v['weight']}kg | {v['pallets']} palet | {v['l']}x{v['w']}x{v['h']} cm")

    st.header("2. Dodaj ładunki")
    if 'cargo_list' not in st.session_state:
        st.session_state.cargo_list = []

    selected_prod = st.selectbox("Wybierz produkt z bazy", list(PRODUCTS_DATA.keys()))
    if st.button("➕ Dodaj do listy"):
        p = PRODUCTS_DATA[selected_prod].copy()
        p['name'] = selected_prod
        p['qty'] = 1
        st.session_state.cargo_list.append(p)

with col2:
    st.header("3. Twoja lista załadunkowa")
    final_items = []
    
    if not st.session_state.cargo_list:
        st.write("Lista jest pusta.")
    else:
        for i, item in enumerate(st.session_state.cargo_list):
            with st.expander(f"{item['name']} (Sztuk: {item.get('qty', 1)})", expanded=True):
                c_cols = st.columns(4)
                l = c_cols[0].number_input("Dł (cm)", value=item['length'], key=f"l_{i}")
                w = c_cols[1].number_input("Szer (cm)", value=item['width'], key=f"w_{i}")
                h = c_cols[2].number_input("Wys (cm)", value=item['height'], key=f"h_{i}")
                weight = c_cols[3].number_input("Waga (kg)", value=item['weight'], key=f"wg_{i}")
                
                c_cols2 = st.columns(3)
                qty = c_cols2[0].number_input("Ilość sztuk", min_value=1, value=item.get('qty', 1), key=f"q_{i}")
                stack = c_cols2[1].checkbox("Stackowalny", value=item['stackable'], key=f"s_{i}")
                if c_cols2[2].button("🗑️ Usuń", key=f"del_{i}"):
                    st.session_state.cargo_list.pop(i)
                    st.rerun()
                
                # Przeliczanie na case'y
                num_cases = math.ceil(qty / item['items_per_case'])
                for _ in range(num_cases):
                    final_items.append({
                        "name": item['name'], "l": l, "w": w, "h": h, 
                        "weight": weight, "stackable": stack, "area": l*w
                    })

    if st.button("🚀 OBLICZ OPTYMALIZACJĘ", type="primary"):
        # --- PROSTY ALGORYTM PAKOWANIA (Greedy) ---
        final_items.sort(key=lambda x: x['area'], reverse=True)
        
        placed_stacks = [] # {x, y, w, l, current_h, items}
        available_spaces = [{"x": 0, "y": 0, "w": v['w'], "l": v['l']}]
        
        total_w = 0
        total_area = 0
        unloaded = []

        for item in final_items:
            placed = False
            
            # Próba stackowania
            if item['stackable']:
                for s in placed_stacks:
                    if s['current_h'] + item['h'] <= v['h'] and item['l'] <= s['l'] and item['w'] <= s['w']:
                        s['current_h'] += item['h']
                        s['items'].append(item)
                        total_w += item['weight']
                        placed = True
                        break
            
            # Próba podłogi
            if not placed:
                for idx, space in enumerate(available_spaces):
                    if item['l'] <= space['l'] and item['w'] <= space['w']:
                        new_stack = {
                            "x": space['x'], "y": space['y'], 
                            "w": item['w'], "l": item['l'], 
                            "current_h": item['h'], "items": [item]
                        }
                        placed_stacks.append(new_stack)
                        total_w += item['weight']
                        total_area += (item['l'] * item['w'])
                        
                        # Podział przestrzeni (uproszczony)
                        available_spaces.pop(idx)
                        if space['w'] - item['w'] > 0:
                            available_spaces.append({"x": space['x']+item['w'], "y": space['y'], "w": space['w']-item['w'], "l": item['l']})
                        if space['l'] - item['l'] > 0:
                            available_spaces.append({"x": space['x'], "y": space['y']+item['l'], "w": space['w'], "l": space['l']-item['l']})
                        
                        placed = True
                        break
            
            if not placed:
                unloaded.append(item)

        # --- WYNIKI ---
        st.divider()
        res_col1, res_col2, res_col3 = st.columns(3)
        
        occ_pallets = round(total_area / EURO_PALLET_AREA, 2)
        weight_perc = round((total_w / v['weight']) * 100, 1)
        
        res_col1.metric("Waga całkowita", f"{total_w} kg", f"{weight_perc}%")
        res_col2.metric("Miejsca paletowe", f"{occ_pallets}", f"Limit: {v['pallets']}")
        res_col3.metric("Załadowane case'y", f"{len(final_items) - len(unloaded)}/{len(final_items)}")

        if unloaded:
            st.error(f"⚠️ Nie zmieszczono {len(unloaded)} elementów!")
        else:
            st.success("✅ Wszystkie ładunki mieszczą się w wybranym pojeździe.")
