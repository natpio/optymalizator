import streamlit as st
import pandas as pd
import math
import plotly.graph_objects as go

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="SQM Cargo Planner 3D", layout="wide", page_icon="🔐")

# --- SYSTEM JEDNEGO HASŁA ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if not st.session_state["password_correct"]:
        st.title("🔐 Autoryzacja SQM")
        pwd = st.text_input("Podaj hasło dostępowe:", type="password")
        if st.button("Zaloguj"):
            if pwd == "NowyRozdzial":
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("❌ Błędne hasło")
        return False
    return True

if check_password():
    # --- BAZA POJAZDÓW ---
    VEHICLES_DATA = {
        "BUS": {"pallets": 8, "weight": 1100, "l": 450, "w": 150, "h": 245},
        "Solówka 6m": {"pallets": 14, "weight": 3500, "l": 600, "w": 245, "h": 245},
        "Solówka 7m": {"pallets": 16, "weight": 3500, "l": 700, "w": 245, "h": 245},
        "FTL (Tir)": {"pallets": 31, "weight": 12000, "l": 1360, "w": 245, "h": 265},
    }

    # --- BAZA PRODUKTÓW SQM (Pełna lista) ---
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
        "NEC X981 98\" TOUCHSCREEN": {"l": 170, "w": 70, "h": 230, "weight": 250.0, "ipc": 1, "stack": True},
        "LG 75\" - STANDARD": {"l": 140, "w": 40, "h": 230, "weight": 210.0, "ipc": 1, "stack": True},
        "P1 lub 1.58 ABSEN": {"l": 108, "w": 71, "h": 62, "weight": 103.0, "ipc": 8, "stack": True},
        "P1.9 UNILUMIN UPAD IV": {"l": 117, "w": 57, "h": 79, "weight": 115.0, "ipc": 8, "stack": True},
        "P2.6 UNILUMIN UPAD IV": {"l": 117, "w": 57, "h": 79, "weight": 116.0, "ipc": 8, "stack": True},
        "P2.06 frameLED": {"l": 86, "w": 62, "h": 100, "weight": 118.0, "ipc": 10, "stack": True},
        "P3.9 Yestech - STANDARD": {"l": 114, "w": 60, "h": 80, "weight": 125.0, "ipc": 10, "stack": True},
        "P2.9 Yestech FLOOR": {"l": 114, "w": 60, "h": 76, "weight": 142.0, "ipc": 10, "stack": True},
        "P3.9 HOXLED / TRANSPARENT": {"l": 114, "w": 80, "h": 130, "weight": 144.0, "ipc": 10, "stack": True},
        "MULTIMEDIA TOTEM 55\"": {"l": 100, "w": 60, "h": 210, "weight": 210.0, "ipc": 1, "stack": False},
        "PROLIGHTS JET SPOT4Z": {"l": 110, "w": 60, "h": 130, "weight": 130.0, "ipc": 10, "stack": True},
        "CHAINMASTER D8 PLUS": {"l": 90, "w": 70, "h": 98, "weight": 98.0, "ipc": 3, "stack": True},
        "PODEST ALUDECK 2 x 1M": {"l": 200, "w": 100, "h": 20, "weight": 45.0, "ipc": 1, "stack": True},
        "ALUSTAGE / AL34 / FD / 2M": {"l": 200, "w": 30, "h": 30, "weight": 11.0, "ipc": 1, "stack": True},
        "EUROTRUSS / HD34 / 3M": {"l": 300, "w": 29, "h": 29, "weight": 18.0, "ipc": 1, "stack": True},
        "Własny ładunek": {"l": 120, "w": 80, "h": 100, "weight": 100.0, "ipc": 1, "stack": True},
    }

    # --- LOGIKA WIZUALIZACJI 3D ---
    def generate_3d_plot(stacks, vehicle):
        fig = go.Figure()
        # Naczepa (kontur)
        fig.add_trace(go.Mesh3d(
            x=[0, vehicle['l'], vehicle['l'], 0, 0, vehicle['l'], vehicle['l'], 0],
            y=[0, 0, vehicle['w'], vehicle['w'], 0, 0, vehicle['w'], vehicle['w']],
            z=[0, 0, 0, 0, vehicle['h'], vehicle['h'], vehicle['h'], vehicle['h']],
            i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
            opacity=0.05, color='gray'
        ))
        
        colors = ['#EF553B', '#00CC96', '#636EFA', '#AB63FA', '#FFA15A', '#19D3F3']
        for i, stack in enumerate(stacks):
            z_bot = 0
            color = colors[i % len(colors)]
            for item in stack['items']:
                dx, dy, dz = stack['l'], stack['w'], item['h']
                fig.add_trace(go.Mesh3d(
                    x=[stack['x'], stack['x']+dx, stack['x']+dx, stack['x'], stack['x'], stack['x']+dx, stack['x']+dx, stack['x']],
                    y=[stack['y'], stack['y'], stack['y']+dy, stack['y']+dy, stack['y'], stack['y'], stack['y']+dy, stack['y']+dy],
                    z=[z_bot, z_bot, z_bot, z_bot, z_bot+dz, z_bot+dz, z_bot+dz, z_bot+dz],
                    i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
                    color=color, opacity=0.85, text=f"{item['name']}", hoverinfo="text"
                ))
                z_bot += dz

        fig.update_layout(scene=dict(aspectmode='data'), margin=dict(l=0,r=0,b=0,t=0), showlegend=False)
        return fig

    # --- ALGORYTM PAKOWANIA ---
    def simulate_packing(cargo_list, vehicle):
        all_cases = []
        for item in cargo_list:
            ipc = item.get('ipc', 1)
            num_cases = math.ceil(item['qty'] / ipc)
            for _ in range(num_cases):
                all_cases.append({"name": item['name'], "l": item['l'], "w": item['w'], "h": item['h'], "weight": item['weight'], "stack": item.get('stack', True)})
        
        all_cases.sort(key=lambda x: x['l']*x['w'], reverse=True)
        stacks, unplaced = [], []
        spaces = [{"x": 0, "y": 0, "w": vehicle['w'], "l": vehicle['l']}]

        for case in all_cases:
            packed = False
            if case['stack']:
                for s in stacks:
                    if case['l'] <= s['l'] and case['w'] <= s['w'] and (s['cur_h'] + case['h']) <= vehicle['h']:
                        s['items'].append(case); s['cur_h'] += case['h']; packed = True; break
            
            if not packed:
                for i, sp in enumerate(spaces):
                    for lr, wr in [(case['l'], case['w']), (case['w'], case['l'])]:
                        if lr <= sp['l'] and wr <= sp['w']:
                            stacks.append({"x": sp['x'], "y": sp['y'], "l": lr, "w": wr, "cur_h": case['h'], "items": [case]})
                            spaces.pop(i)
                            if sp['w']-wr > 0: spaces.append({"x": sp['x']+wr, "y": sp['y'], "w": sp['w']-wr, "l": lr})
                            if sp['l']-lr > 0: spaces.append({"x": sp['x'], "y": sp['y']+lr, "w": sp['w'], "l": sp['l']-lr})
                            spaces.sort(key=lambda s: s['l']*s['w'])
                            packed = True; break
                    if packed: break
            if not packed: unplaced.append(case)
        return stacks, unplaced

    # --- INTERFEJS ---
    st.title("🚚 SQM Professional 3D Cargo Planner")
    
    if 'cargo' not in st.session_state: st.session_state.cargo = []

    col1, col2 = st.columns([1, 2])

    with col1:
        v_type = st.selectbox("Wybierz Pojazd", list(VEHICLES_DATA.keys()), index=3)
        v = VEHICLES_DATA[v_type]
        
        st.divider()
        search = st.text_input("🔍 Szukaj sprzętu w bazie...")
        filtered = [k for k in PRODUCTS_DATA.keys() if search.lower() in k.lower()]
        sel = st.selectbox("Znaleziony produkt", filtered)
        
        if st.button("➕ Dodaj do naczepy"):
            item = PRODUCTS_DATA[sel].copy()
            item['name'] = sel
            item['qty'] = 1
            st.session_state.cargo.append(item)
        
        st.divider()
        for idx, it in enumerate(st.session_state.cargo):
            with st.expander(f"{it['name']}"):
                it['qty'] = st.number_input("Ilość", 1, 500, it['qty'], key=f"q_{idx}")
                if st.button("Usuń", key=f"rm_{idx}"):
                    st.session_state.cargo.pop(idx)
                    st.rerun()

    with col2:
        if st.session_state.cargo:
            stacks, unplaced = simulate_packing(st.session_state.cargo, v)
            
            w_total = sum(sum(i['weight'] for i in s['items']) for s in stacks)
            area_total = sum(s['l']*s['w'] for s in stacks)
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Waga", f"{round(w_total,1)} kg", f"Max: {v['weight']}")
            m2.metric("Miejsca Paletowe", f"{round(area_total/(120*80), 2)}", f"Max: {v['pallets']}")
            m3.metric("Liczba stosów", len(stacks))

            if w_total > v['weight']: st.error("🚨 PRZECIĄŻENIE WAGOWE!")

            st.subheader("Wizualizacja 3D (Złap i obróć)")
            st.plotly_chart(generate_3d_plot(stacks, v), use_container_width=True)
            
            if unplaced:
                st.warning(f"⚠️ Nie zmieszczono: {len(unplaced)} skrzyń!")
        else:
            st.info("Dodaj sprzęt, aby zobaczyć plan rozmieszczenia.")

    if st.sidebar.button("Wyloguj"):
        st.session_state["password_correct"] = False
        st.rerun()
