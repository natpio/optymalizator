import streamlit as st
import pandas as pd
import math
import plotly.graph_objects as go

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="SQM Cargo Planner Pro 3D", layout="wide", page_icon="🚚")

# --- BAZA POJAZDÓW ---
VEHICLES_DATA = {
    "BUS": {"pallets": 8, "weight": 1100, "l": 450, "w": 150, "h": 245},
    "Solówka 6m": {"pallets": 14, "weight": 3500, "l": 600, "w": 245, "h": 245},
    "Solówka 7m": {"pallets": 16, "weight": 3500, "l": 700, "w": 245, "h": 245},
    "FTL (Tir)": {"pallets": 31, "weight": 12000, "l": 1360, "w": 245, "h": 265},
}

# --- KOMPLETNA BAZA PRODUKTÓW (Z PLIKU HTML) ---
# Klucz 'ipc' to items per case (sztuk w skrzyni)
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
    "PROLIGHTS / JET SPOT4Z": {"l": 110, "w": 60, "h": 130, "weight": 130.0, "ipc": 10, "stack": True},
    "PROLIGHTS / JET WASH19": {"l": 120, "w": 60, "h": 123, "weight": 123.0, "ipc": 8, "stack": True},
    "PROLIGHTS / SOLAR 27Q": {"l": 120, "w": 70, "h": 113, "weight": 113.0, "ipc": 10, "stack": True},
    "PROLIGHTS / STUDIO COB FC 150W": {"l": 140, "w": 60, "h": 95.4, "weight": 95.4, "ipc": 5, "stack": True},
    "CHAINMASTER / D8 PLUS / 320KG": {"l": 90, "w": 70, "h": 97, "weight": 97.0, "ipc": 2, "stack": True},
    "CHAINMASTER / D8 PLUS / 500KG": {"l": 90, "w": 70, "h": 98, "weight": 98.0, "ipc": 3, "stack": True},
    "speaker RCF 310": {"l": 60, "w": 40, "h": 40, "weight": 40.0, "ipc": 3, "stack": True},
    "truss cart 14x2 (200cm)": {"l": 200, "w": 70, "h": 350, "weight": 350.0, "ipc": 1, "stack": False},
    "truss cart 14x2 (300cm)": {"l": 300, "w": 70, "h": 350, "weight": 350.0, "ipc": 1, "stack": False},
    "Boxer Projector": {"l": 110, "w": 60, "h": 185, "weight": 185.0, "ipc": 1, "stack": False},
    "PODEST ALUDECK 2 x 1M": {"l": 200, "w": 100, "h": 20, "weight": 45.0, "ipc": 1, "stack": True},
    "ALUMINIUM BLACK PIPE / 6M": {"l": 600, "w": 6, "h": 6, "weight": 9.0, "ipc": 1, "stack": True},
    "P2.9 OUTDOOR RENTAL": {"l": 120, "w": 60, "h": 80, "weight": 120.0, "ipc": 9, "stack": True},
    "Własny ładunek": {"l": 100, "w": 100, "h": 100, "weight": 100.0, "ipc": 1, "stack": True}
}

# --- FUNKCJA WIZUALIZACJI 3D ---
def generate_3d_plot(stacks, vehicle):
    fig = go.Figure()

    # Rysowanie obrysu naczepy
    fig.add_trace(go.Mesh3d(
        x=[0, vehicle['l'], vehicle['l'], 0, 0, vehicle['l'], vehicle['l'], 0],
        y=[0, 0, vehicle['w'], vehicle['w'], 0, 0, vehicle['w'], vehicle['w']],
        z=[0, 0, 0, 0, vehicle['h'], vehicle['h'], vehicle['h'], vehicle['h']],
        i=[7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2],
        j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
        k=[0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
        opacity=0.1, color='gray', name='Naczepa'
    ))

    colors = ['#EF553B', '#00CC96', '#636EFA', '#AB63FA', '#FFA15A', '#19D3F3']
    
    for i, stack in enumerate(stacks):
        z_bottom = 0
        color = colors[i % len(colors)]
        for item in stack['items']:
            x, y, z = stack['x'], stack['y'], z_bottom
            dx, dy, dz = stack['l'], stack['w'], item['h']
            
            fig.add_trace(go.Mesh3d(
                x=[x, x+dx, x+dx, x, x, x+dx, x+dx, x],
                y=[y, y, y+dy, y+dy, y, y, y+dy, y+dy],
                z=[z, z, z, z, z+dz, z+dz, z+dz, z+dz],
                i=[7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2],
                j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
                k=[0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
                color=color, opacity=0.8,
                hoverinfo="text",
                text=f"Produkt: {item['name']}<br>Wymiary: {dx}x{dy}x{dz} cm<br>Poz: {x},{y}"
            ))
            z_bottom += dz

    fig.update_layout(
        scene=dict(
            xaxis=dict(title='Długość (cm)', range=[0, vehicle['l']]),
            yaxis=dict(title='Szerokość (cm)', range=[0, vehicle['w']]),
            zaxis=dict(title='Wysokość (cm)', range=[0, vehicle['h']]),
            aspectmode='data'
        ),
        margin=dict(l=0, r=0, b=0, t=0),
        showlegend=False
    )
    return fig

# --- ALGORYTM PAKOWANIA ---
def simulate_packing(cargo_list, vehicle):
    all_cases = []
    for item in cargo_list:
        # NAPRAWA KeyError: 'ipc'
        ipc = item.get('ipc', item.get('items_per_case', 1))
        num_cases = math.ceil(item['qty'] / ipc)
        for _ in range(num_cases):
            all_cases.append({
                "name": item['name'], "l": item['l'], "w": item['w'], "h": item['h'],
                "weight": item['weight'], "stackable": item.get('stack', True),
                "vol": item['l'] * item['w'] * item['h']
            })

    # Sortowanie FFD (największa powierzchnia najpierw)
    all_cases.sort(key=lambda x: x['l'] * x['w'], reverse=True)

    placed_stacks = []
    unplaced = []
    spaces = [{"x": 0, "y": 0, "w": vehicle['w'], "l": vehicle['l']}]

    for case in all_cases:
        packed = False
        # 1. Próba stackowania
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
                for l_rot, w_rot in [(case['l'], case['w']), (case['w'], case['l'])]:
                    if l_rot <= space['l'] and w_rot <= space['w']:
                        new_stack = {
                            "x": space['x'], "y": space['y'], "l": l_rot, "w": w_rot,
                            "cur_h": case['h'], "can_stack": case['stackable'], "items": [case]
                        }
                        placed_stacks.append(new_stack)
                        # Podział przestrzeni (Guillotine Split)
                        spaces.pop(i)
                        if space['w'] - w_rot > 0:
                            spaces.append({"x": space['x'] + w_rot, "y": space['y'], "w": space['w'] - w_rot, "l": l_rot})
                        if space['l'] - l_rot > 0:
                            spaces.append({"x": space['x'], "y": space['y'] + l_rot, "w": space['w'], "l": space['l'] - l_rot})
                        spaces.sort(key=lambda s: s['l'] * s['w'])
                        packed = True
                        break
                if packed: break
        
        if not packed:
            unplaced.append(case)

    # Statystyki
    total_w = sum(sum(it['weight'] for it in s['items']) for s in placed_stacks)
    total_area = sum(s['l'] * s['w'] for s in placed_stacks)
    total_vol = sum(sum(it['vol'] for it in s['items']) for s in placed_stacks)

    return {
        "stacks": placed_stacks, 
        "unplaced": unplaced, 
        "weight": total_w, 
        "area": total_area, 
        "vol": total_vol
    }

# --- INTERFEJS STREAMLIT ---
st.title("🚚 SQM Cargo Planner 3D")
st.caption("Zaawansowany system planowania załadunków - SQM Multimedia Solutions")

if 'cargo' not in st.session_state:
    st.session_state.cargo = []

col_in, col_out = st.columns([1, 2])

with col_in:
    st.subheader("📦 Konfiguracja")
    v_type = st.selectbox("Wybierz pojazd", list(VEHICLES_DATA.keys()), index=3)
    v = VEHICLES_DATA[v_type]
    
    st.info(f"Parametry: {v['l']}x{v['w']} cm | Max {v['weight']} kg")

    st.divider()
    search = st.text_input("Szukaj sprzętu...")
    filtered = [k for k in PRODUCTS_DATA.keys() if search.lower() in k.lower()]
    selected = st.selectbox("Wybierz z bazy", filtered)
    
    if st.button("➕ Dodaj do listy"):
        item = PRODUCTS_DATA[selected].copy()
        item['name'] = selected
        item['qty'] = 1
        st.session_state.cargo.append(item)

    st.divider()
    if st.session_state.cargo:
        for idx, it in enumerate(st.session_state.cargo):
            with st.expander(f"{it['name']}", expanded=True):
                c1, c2 = st.columns(2)
                it['qty'] = c1.number_input("Sztuk", 1, 500, it['qty'], key=f"q_{idx}")
                it['stack'] = c2.checkbox("Stackuj", it.get('stack', True), key=f"s_{idx}")
                if st.button("Usuń", key=f"rm_{idx}"):
                    st.session_state.cargo.pop(idx)
                    st.rerun()

with col_out:
    if st.session_state.cargo:
        res = simulate_packing(st.session_state.cargo, v)
        
        # Wskaźniki
        m1, m2, m3 = st.columns(3)
        pallets_eq = round(res['area'] / (120 * 80), 2)
        m1.metric("Waga", f"{res['weight']} kg", f"{round((res['weight']/v['weight'])*100,1)}%")
        m2.metric("Miejsca Paletowe", f"{pallets_eq}", f"Limit: {v['pallets']}")
        m3.metric("Objętość", f"{round((res['vol']/(v['l']*v['w']*v['h']))*100,1)}%")

        if res['weight'] > v['weight']: st.error("🚨 PRZECIĄŻENIE WAGOWE!")
        if pallets_eq > v['pallets']: st.warning("🚨 BRAK MIEJSCA NA PODŁODZE!")

        # WIZUALIZACJA 3D
        st.subheader("Model 3D Załadunku")
        fig = generate_3d_plot(res['stacks'], v)
        st.plotly_chart(fig, use_container_width=True)

        if res['unplaced']:
            st.error(f"❌ Nie zmieszczono {len(res['unplaced'])} skrzyń!")
    else:
        st.write("Dodaj przedmioty, aby zobaczyć wizualizację.")
