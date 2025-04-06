import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd
import matplotlib.cm as cm

st.set_page_config(layout="wide")
st.title("Frise Chronologique Médicamenteuse Interactive")

# Initialisation
if 'chronic_treatments' not in st.session_state:
    st.session_state.chronic_treatments = []
if 'acute_treatments' not in st.session_state:
    st.session_state.acute_treatments = {}
if 'adverse_effects' not in st.session_state:
    st.session_state.adverse_effects = {}

# Formulaires
st.header("➕ Ajouter un traitement chronique")
col1, col2, col3 = st.columns(3)
with col1:
    chrono_name = st.text_input("Nom du médicament")
with col2:
    chrono_start = st.date_input("Date de début", value=datetime(2020,1,1), min_value=datetime(1900,1,1), max_value=datetime(2100,12,31), format="DD/MM/YYYY")
with col3:
    chrono_end = st.date_input("Date de fin", value=datetime(2020,1,2), min_value=datetime(1900,1,1), max_value=datetime(2100,12,31), format="DD/MM/YYYY")

if st.button("Ajouter le traitement chronique"):
    st.session_state.chronic_treatments.append({
        "name": chrono_name, "start": chrono_start, "end": chrono_end
    })
    st.success(f"Ajouté : {chrono_name} de {chrono_start} à {chrono_end}")

st.divider()
st.header("💊 Ajouter un traitement ponctuel")
acute_name = st.text_input("Nom du traitement ponctuel")
acute_dates = st.text_input("Dates (JJ/MM/AAAA, séparées par des virgules)")

if st.button("Ajouter le traitement ponctuel"):
    try:
        dates = [datetime.strptime(d.strip(), "%d/%m/%Y").date() for d in acute_dates.split(",") if d.strip()]
        st.session_state.acute_treatments[acute_name] = dates
        st.success(f"Ajouté : {acute_name} aux dates {dates}")
    except:
        st.error("Format de date invalide. Utilisez JJ/MM/AAAA.")
# Suite du code dans l'étape suivante

st.divider()
st.header("⚠️ Ajouter un effet indésirable")
ei_name = st.text_input("Nom de l'effet indésirable")
ei_start = st.date_input("Date de début EI", value=datetime(2020,1,1), min_value=datetime(1900,1,1), max_value=datetime(2100,12,31), format="DD/MM/YYYY")
ei_end_text = st.text_input("Date de fin de l'EI (optionnelle)", placeholder="JJ/MM/AAAA")

if st.button("Ajouter l'effet indésirable"):
    if ei_name not in st.session_state.adverse_effects:
        st.session_state.adverse_effects[ei_name] = []
    try:
        ei_end = datetime.strptime(ei_end_text.strip(), "%d/%m/%Y").date() if ei_end_text.strip() else None
    except:
        ei_end = None
    st.session_state.adverse_effects[ei_name].append({"start": ei_start, "end": ei_end})
    st.success(f"Ajouté : {ei_name} le {ei_start}" + (f" au {ei_end}" if ei_end else ""))

st.divider()
st.header("📋 Synthèse clinique")
desc = st.text_area("🩺 Description clinique", placeholder="Décrire les symptômes, évolution, traitement symptomatique...")
hep = st.text_area("🧪 Bilan hépatique", placeholder="ASAT, ALAT, PAL, GGT, bilirubine...")
renal = st.text_area("💧 Fonction rénale", placeholder="Créatinine, valeur de base...")
nfs = st.text_area("🧬 NFS : formule leucocytaire", placeholder="Leucocytes, PNN, PNE, lymphocytes...")
fievre = st.text_input("🌡️ Fièvre", placeholder="Oui/Non + température max")
pcr = st.text_area("🧫 PCR et sérologies", placeholder="PCR HHV6, EBV, CMV...")
biopsie = st.text_area("🔬 Biopsie cutanée", placeholder="Résultat de la biopsie si faite")
autres = st.text_area("🧾 Autres paramètres biologiques", placeholder="CRP, CPK...")
produit_contraste = st.text_input("🧴 Produit de contraste iodé", placeholder="Oui/Non + date de la dernière injection")

st.divider()
if st.button("📊 Générer la frise"):
    all_dates = set()
    for t in st.session_state.chronic_treatments:
        all_dates.add(t['start'])
        all_dates.add(t['end'])
    for dates in st.session_state.acute_treatments.values():
        all_dates.update(dates)
    for ei_list in st.session_state.adverse_effects.values():
        for ei in ei_list:
            all_dates.add(ei['start'])
            if ei['end']:
                all_dates.add(ei['end'])

    all_dates = sorted(list(all_dates))
    x_positions = {date: i for i, date in enumerate(all_dates)}
    all_names = [t["name"] for t in st.session_state.chronic_treatments] + list(st.session_state.acute_treatments.keys())
    y_positions = {name: i for i, name in enumerate(all_names)}

    fig, ax = plt.subplots(figsize=(14, 7))
    for trt in st.session_state.chronic_treatments:
        y = y_positions[trt['name']]
        ax.hlines(y, x_positions[trt['start']], x_positions[trt['end']], color='green', linewidth=2)

    for name, dates in st.session_state.acute_treatments.items():
        y = y_positions[name]
        for d in dates:
            ax.plot(x_positions[d], y, 'bo')

    ei_names = list(st.session_state.adverse_effects.keys())
    base_y = len(y_positions)
    for idx, name in enumerate(ei_names):
        y = base_y + idx
        for i, period in enumerate(st.session_state.adverse_effects[name]):
            x = x_positions[period['start']]
            if period['end']:
                x_end = x_positions[period['end']]
                ax.hlines(y, x, x_end, color='red', linestyle='--', linewidth=4, label=name if i == 0 else None)
            else:
                ax.axvline(x, color='red', linestyle='--', linewidth=4)
                ax.text(x, y + 0.2, name, rotation=90, verticalalignment='bottom', horizontalalignment='center', fontsize=8, color='red')

    ax.set_yticks(list(range(len(y_positions) + len(ei_names))))
    ax.set_yticklabels(list(y_positions.keys()) + ei_names)
    ax.set_xticks(list(x_positions.values()))
    ax.set_xticklabels([f"{d.strftime('%d/%m')}
{d.strftime('%Y')}" for d in all_dates], rotation=0, ha='center')
    ax.set_ylabel("Traitements / EI")
    ax.grid(axis='x', linestyle=':', linewidth=0.5)
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=3)
    st.pyplot(fig)

    st.markdown("---")
    st.subheader("⏱️ Délais entre traitements et survenue des effets indésirables")
    for ei_name, ei_periods in st.session_state.adverse_effects.items():
        for period in ei_periods:
            ei_date = period['start']
            st.markdown(f"**Effet indésirable : {ei_name} (début : {ei_date.strftime('%d/%m/%Y')})**")
            rows = []
            for trt in st.session_state.chronic_treatments:
                start = trt['start']
                end = trt['end']
                if start <= ei_date <= end:
                    delay = (ei_date - start).days
                    rows.append(f"- `{trt['name']}` : survenu {delay} jours après le début du traitement.")
                elif ei_date > end:
                    delay = (ei_date - end).days
                    rows.append(f"- `{trt['name']}` : survenu {delay} jours après la fin du traitement.")
            for name, dates in st.session_state.acute_treatments.items():
                for d in dates:
                    if d <= ei_date:
                        delay = (ei_date - d).days
                        rows.append(f"- `{name}` : survenu {delay} jours après l'administration.")
            if rows:
                st.markdown("\n".join(rows))
            else:
                st.markdown("Aucun traitement administré avant la survenue de cet effet indésirable.")

    st.markdown("---")
    st.subheader("🧾 Synthèse clinique")
    st.markdown(f"**🩺 Description clinique** : {desc or 'Non renseigné'}")
    st.markdown(f"**🧪 Bilan hépatique** : {hep or 'Non renseigné'}")
    st.markdown(f"**💧 Fonction rénale** : {renal or 'Non renseigné'}")
    st.markdown(f"**🧬 NFS** : {nfs or 'Non renseigné'}")
    st.markdown(f"**🌡️ Fièvre** : {fievre or 'Non renseigné'}")
    st.markdown(f"**🧫 PCR et sérologies** : {pcr or 'Non renseigné'}")
    st.markdown(f"**🔬 Biopsie cutanée** : {biopsie or 'Non renseigné'}")
    st.markdown(f"**🧾 Autres paramètres biologiques** : {autres or 'Non renseigné'}")
    st.markdown(f"**🧴 Produit de contraste iodé** : {produit_contraste or 'Non renseigné'}")

st.info("Remplissez les champs ci-dessus puis cliquez sur \"Générer la frise\" pour afficher les résultats.")
