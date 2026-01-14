import streamlit as st
import pandas as pd
import math
import plotly.graph_objects as go

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="SQM Cargo Planner Pro 3D", layout="wide", page_icon="🚚")

# --- SYSTEM HASŁA ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if not st.session_state["password_correct"]:
        st.title("🔐 SQM Multimedia Solutions")
        st.subheader("System Planowania Załadunków")
        pwd = st.text_input("Hasło dostępowe:", type="password")
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
    VEHICLES = {
        "FTL (Tir)": {"l": 1360, "w": 245, "h": 265, "weight": 12000, "pallets": 33},
        "Solówka 7m": {"l": 700, "w": 245, "h": 245, "weight": 3500, "pallets": 16},
        "Solówka 6m": {"l": 600, "w": 245, "h": 245, "weight": 3500, "pallets": 14},
        "BUS": {"l": 450, "w": 150, "h": 245, "weight": 1100, "pallets": 8},
    }

    # --- PEŁNA BAZA PRODUKTÓW SQM (Z PLIKU HTML) ---
    PRODUCTS = {
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
        "P1 lub 1.58 ABSEN": {"l": 108, "w": 71, "h": 62, "weight": 103.0, "ipc": 8, "stack": True},
        "P1.9 UNILUMIN UPAD IV": {"l": 117, "w": 57, "h": 79, "weight": 115.0, "ipc": 8, "stack": True},
        "P2.6 UNILUMIN UPAD IV": {"l": 117, "w": 57, "h": 79, "weight": 116.0, "ipc": 8, "stack": True},
        "P2.06 frameLED": {"l": 86, "w": 62, "h": 100, "weight": 118.0, "ipc": 10, "stack": True},
        "P3.9 Yestech - STANDARD": {"l": 114, "w": 60, "h": 80, "weight": 125.0, "ipc": 10, "stack": True},
        "P2.9 Yestech FLOOR": {"l": 114, "w": 60, "h": 76, "weight": 142.0, "ipc": 10, "stack": True},
        "Case for accessories RED": {"l": 120, "w": 60, "h": 80, "weight": 120.0, "ipc": 5, "stack": True},
        "PROLIGHTS JET SPOT4Z": {"l": 110, "w": 60, "h": 130, "weight": 130.0, "ipc": 10, "stack": True},
        "CHAINMASTER D8 PLUS": {"l": 90, "w": 70, "h": 98, "weight": 98.0, "ipc": 3, "stack": True},
        "PODEST ALUDECK 2x1M": {"l": 200, "w": 100, "h": 20, "weight": 45.0, "ipc": 1, "stack": True},
        "ALUSTAGE / AL34 / 2M": {"l": 200, "w": 30, "h": 30, "weight": 11.0, "ipc": 1, "stack": True},
        "EUROTRUSS / HD34 / 3M": {"l": 300, "w": 29, "h": 29, "weight": 18.0, "ipc": 1, "stack": True},
        "Własny ładunek": {"l": 120, "w": 80, "h": 100, "weight": 100.0, "ipc": 1, "stack": True},
    }

    # --- FUNKCJA RYSOWANIA 3D ---
    def add_box(fig, x, y, z, l, w, h, name, color):
        gap = 0.5 # Minimalny odstęp wizualny
        l_g = l - gap; w_g = w - gap; h_g = h - gap
        
        # Wierzchołki bryły
        x_c = [x, x+l_g, x+l_g, x, x, x+l_g, x+l_g, x]
        y_c = [y, y, y+w_g, y+w_g, y, y, y+w_g, y+w_g]
        z_c = [z, z, z, z, z+h_g, z+h_g, z+h_g, z+h_g]
        
        fig.add_trace(go.Mesh3d(
            x=x_c, y=y_c, z=z_c,
            i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6],
            color=color, opacity=0.9, flatshading=True, name=name, hoverinfo="text",
            text=f"Produkt: {name}<br>Poziom Z: {z} cm"
        ))

    # --- ALGORYTM PAKOWANIA ---
    def pack_cargo(cargo_list, v):
        to_pack = []
        for c in cargo_list:
            num = math.ceil(c['qty'] / c['ipc'])
            for _ in range(num):
                to_pack.append(c)
        
        # Sortowanie po powierzchni podstawy
        to_pack.sort(key=lambda x: x['l']*x['w'], reverse=True)
        
        placed_stacks = []
        unplaced = []
        
        # Uproszczony algorytm rozmieszczenia na podłodze
        curr_x, curr_y, max_y_in_row = 0, 0, 0
        
        for item in to_pack:
            packed = False
            # 1. Próba dołożenia na istniejący stos
            if item.get('stack', True):
                for s in placed_stacks:
                    if item['l'] <= s['l'] and item['w'] <= s['w'] and (s['cur_h'] + item['h']) <= v['h']:
                        s['items'].append(item)
                        s['cur_h'] += item['h']
                        packed = True
                        break
            
            # 2. Nowy stos na podłodze
            if not packed:
                # Sprawdzenie rotacji
                for l_r, w_r in [(item['l'], item['w']), (item['w'], item['l'])]:
                    if curr_x + l_r <= v['l'] and curr_y + w_r <= v['w']:
                        placed_stacks.append({
                            'x': curr_x, 'y': curr_y, 'l': l_r, 'w': w_r,
                            'cur_h': item['h'], 'items': [item]
                        })
                        max_y_in_row = max(max_y_in_row, w_r)
                        curr_x += l_r
                        packed = True
                        break
                
                # Nowa linia
                if not packed:
                    curr_x = 0
                    curr_y += max_y_in_row
                    max_y_in_row = 0
                    if curr_y + item['w'] <= v['w'] and curr_x + item['l'] <= v['l']:
                        placed_stacks.append({
                            'x': curr_x, 'y': curr_y, 'l': item['l'], 'w': item['w'],
                            'cur_h': item['h'], 'items': [item]
                        })
                        max_y_in_row = item['w']
                        curr_x += item['l']
                        packed = True

            if not packed:
                unplaced.append(item)
        
        return placed_stacks, unplaced

    # --- INTERFEJS ---
    st.title("🚚 SQM Cargo Planner Pro 3D")
    
    if 'cargo' not in st.session_state: st.session_state.cargo = []

    c1, c2 = st.columns([1, 2])
    
    with c1:
        v_name = st.selectbox("Pojazd", list(VEHICLES.keys()), index=0)
        v = VEHICLES[v_name]
        
        st.divider()
        search = st.text_input("🔍 Szukaj sprzętu...")
        filt = [k for k in PRODUCTS.keys() if search.lower() in k.lower()]
        sel = st.selectbox("Wybierz z bazy", filt)
        
        if st.button("➕ Dodaj do listy"):
            it = PRODUCTS[sel].copy()
            it['name'] = sel
            it['qty'] = 1
            st.session_state.cargo.append(it)
            
        for idx, it in enumerate(st.session_state.cargo):
            with st.expander(f"{it['name']} (x{it['qty']})"):
                it['qty'] = st.number_input("Ilość", 1, 500, it['qty'], key=f"q_{idx}")
                if st.button("Usuń", key=f"r_{idx}"):
                    st.session_state.cargo.pop(idx); st.rerun()

    with c2:
        if st.session_state.cargo:
            stacks, unplaced = pack_cargo(st.session_state.cargo, v)
            
            w_total = sum(sum(i['weight'] for i in s['items']) for s in stacks)
            area_total = sum(s['l']*s['w'] for s in stacks)
            
            m1, m2 = st.columns(2)
            m1.metric("Waga Razem", f"{round(w_total,1)} kg", f"Limit: {v['weight']}")
            m2.metric("Powierzchnia (m2)", f"{round(area_total/10000, 2)}", f"Palety eq: {round(area_total/(120*80), 1)}")

            # WIZUALIZACJA 3D
            fig = go.Figure()
            
            # Kontur naczepy
            fig.add_trace(go.Scatter3d(
                x=[0, v['l'], v['l'], 0, 0, 0, v['l'], v['l'], 0, 0],
                y=[0, 0, v['w'], v['w'], 0, 0, 0, v['w'], v['w'], 0],
                z=[0, 0, 0, 0, 0, v['h'], v['h'], v['h'], v['h'], v['h']],
                mode='lines', line=dict(color='black', width=4), name='Naczepa'
            ))

            colors = ['#EF553B', '#00CC96', '#636EFA', '#AB63FA', '#FFA15A', '#19D3F3', '#FF6692']
            
            for i, s in enumerate(stacks):
                z_ptr = 0
                for item in s['items']:
                    add_box(fig, s['x'], s['y'], z_ptr, s['l'], s['w'], item['h'], item['name'], colors[i % len(colors)])
                    z_ptr += item['h']

            fig.update_layout(scene=dict(aspectmode='data'), margin=dict(l=0, r=0, b=0, t=0))
            st.plotly_chart(fig, use_container_width=True)
            
            if unplaced:
                st.error(f"⚠️ Nie zmieszczono {len(unplaced)} elementów!")
            
            if st.button("Wyloguj"):
                st.session_state["password_correct"] = False
                st.rerun()
