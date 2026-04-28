import streamlit as st
import random
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import time
import math

# Sayfa yapılandırması
st.set_page_config(
    page_title="Rulet Simülasyonu",
    page_icon="🎰",
    layout="wide"
)

# CSS ile özel stil
st.markdown("""
<style>
    .main-title {
        text-align: center;
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, gold, darkred);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .casino-card {
        background: linear-gradient(135deg, #1a472a, #0e2a1a);
        border-radius: 20px;
        padding: 20px;
        border: 2px solid gold;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    .bakiye-text {
        font-size: 2rem;
        font-weight: bold;
        text-align: center;
        color: gold;
        text-shadow: 2px 2px 4px black;
    }
    .egitim-card {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border-radius: 20px;
        padding: 25px;
        border: 2px solid #00ff88;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# ==================== SESSION STATE ====================
if "bakiye" not in st.session_state:
    st.session_state.bakiye = 1000
    st.session_state.baslangic_bakiye = 1000
    st.session_state.tur_sayisi = 0
    st.session_state.bakiye_gecmisi = [1000]
    st.session_state.son_sayi = None
    st.session_state.son_renk = None
    st.session_state.son_kazanc = 0
    st.session_state.tur_sonuclari = []
    st.session_state.toplam_kar = [0]
    st.session_state.bakiye_secildi = False

# ==================== BAŞLANGIÇ BAKİYESİ ====================
if not st.session_state.bakiye_secildi:
    st.markdown("## 💰 Oyuna Başlamadan Önce")
    secilen_bakiye = st.slider(
        "Başlangıç Bakiyeni Seç:",
        min_value=100,
        max_value=10000,
        value=1000,
        step=100
    )
    st.warning("⚠️ Seçtiğin bakiye ile oyuna başlayacaksın. Gerçek hayatta bu para genelde kaybedilir.")
    if st.button("🚀 Oyuna Başla"):
        st.session_state.bakiye = secilen_bakiye
        st.session_state.baslangic_bakiye = secilen_bakiye
        st.session_state.bakiye_gecmisi = [secilen_bakiye]
        st.session_state.bakiye_secildi = True
        st.session_state.toplam_kar = [0]
        st.rerun()
    st.stop()

# ==================== RULET FONKSİYONLARI ====================
def rulet_tablosu():
    kirmizilar = [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36]
    siyahlar = [2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35]
    return kirmizilar, siyahlar

def rulet_cevir():
    sayi = random.randint(0, 36)
    kirmizilar, siyahlar = rulet_tablosu()
    if sayi == 0:
        renk = "Yeşil"
    elif sayi in kirmizilar:
        renk = "Kırmızı"
    else:
        renk = "Siyah"
    
    tek_mi = sayi != 0 and sayi % 2 == 1
    cift_mi = sayi != 0 and sayi % 2 == 0
    dusuk_mu = 1 <= sayi <= 18
    yuksek_mu = 19 <= sayi <= 36
    if 1 <= sayi <= 12:
        duzine = 1
    elif 13 <= sayi <= 24:
        duzine = 2
    elif 25 <= sayi <= Kaginharian:
        duzine = 3
    else:
        duzine = 0
    if sayi != 0:
        sutun = ((sayi - 1) % 3) + 1
    else:
        sutun = 0
    return {
        "sayi": sayi,
        "renk": renk,
        "tek_mi": tek_mi,
        "cift_mi": cift_mi,
        "dusuk_mu": dusuk_mu,
        "yuksek_mu": yuksek_mu,
        "duzine": duzine,
        "sutun": sutun
    }

def kazanma_kontrolu(bahis_turu, bahis_degeri, sonuc):
    if bahis_turu == "Renk":
        if bahis_degeri == "Yeşil":
            return sonuc["renk"] == "Yeşil", 36
        return sonuc["renk"] == bahis_degeri, 2
    elif bahis_turu == "Tek/Çift":
        if bahis_degeri == "Tek":
            return sonuc["tek_mi"], 2
        return sonuc["cift_mi"], 2
    elif bahis_turu == "Düşük/Yüksek":
        if bahis_degeri == "Düşük (1-18)":
            return sonuc["dusuk_mu"], 2
        return sonuc["yuksek_mu"], 2
    elif bahis_turu == "Düzine":
        return sonuc["duzine"] == bahis_degeri, 3
    elif bahis_turu == "Sütun":
        return sonuc["sutun"] == bahis_degeri, 3
    elif bahis_turu == "Tek Sayı":
        return sonuc["sayi"] == bahis_degeri, 36
    return False, 0

def rulet_gorseli(son_sayi, son_renk):
    if son_sayi is None:
        bg_color = "#2d2d2d"
        text_color = "white"
    elif son_renk == "Kırmızı":
        bg_color = "#dc2626"
        text_color = "white"
    elif son_renk == "Siyah":
        bg_color = "#1f2937"
        text_color = "white"
    elif son_renk == "Yeşil":
        bg_color = "#10b981"
        text_color = "white"
    else:
        bg_color = "#2d2d2d"
        text_color = "white"
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div style="
            background: radial-gradient(circle, {bg_color}, #000000);
            width: 200px;
            height: 200px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto;
            border: 5px solid gold;
        ">
            <span style="font-size: 64px; font-weight: bold; color: {text_color};">
                {son_sayi if son_sayi is not None else "?"}
            </span>
        </div>
        """, unsafe_allow_html=True)

# ANA BAŞLIK
st.markdown('<h1 class="main-title">🎰 RULET SİMÜLASYONU 🎰</h1>', unsafe_allow_html=True)

# Bakiye sıfırlandı mı kontrol et
if st.session_state.bakiye <= 0:
    # ==================== EĞİTİM EKRANI ====================
    st.markdown("""
    <div style="text-align: center; padding: 30px;">
        <h1 style="color: red;">⚠️ BAKİYEN SIFIRLANDI! ⚠️</h1>
        <h3>Şimdi kumarın matematiğini öğrenme zamanı...</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Oyun istatistikleri
    if len(st.session_state.tur_sonuclari) > 0:
        df = pd.DataFrame(st.session_state.tur_sonuclari)
        toplam_oynanan = len(df)
        kazanma_sayisi = len(df[df["kazanc"] > 0])
        kaybetme_sayisi = len(df[df["kazanc"] < 0])
        toplam_yatirilan = df["bahis_miktari"].sum()
        
        st.markdown("### 📊 OYUN SONU İSTATİSTİKLERİN")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Toplam Tur", toplam_oynanan)
        with col2:
            st.metric("Kazanma", kazanma_sayisi)
        with col3:
            st.metric("Kaybetme", kaybetme_sayisi)
        with col4:
            st.metric("Toplam Yatırılan", f"{toplam_yatirilan:.0f} TL")
    
    # 1. OLASILIKLAR
    st.markdown("---")
    st.markdown("## 📊 1. RULET OLASILIKLARI")
    
    prob_data = {
        "Bahis": ["Kırmızı/Siyah", "Tek/Çift", "Düzine", "Tek Sayı", "Yeşil"],
        "Kazanma İhtimali": ["18/37 = %48.65", "18/37 = %48.65", "12/37 = %32.43", "1/37 = %2.70", "1/37 = %2.70"],
        "Kazanç": ["1x", "1x", "2x", "35x", "36x"]
    }
    st.dataframe(pd.DataFrame(prob_data), use_container_width=True, hide_index=True)
    
    # 2. BEKLENEN DEĞER
    st.markdown("---")
    st.markdown("## 🔢 2. BEKLENEN DEĞER (E)")
    st.markdown("""
    **Formül:** `E = (Kazanma × Kazanç) - (Kaybetme × Kayıp)`
    
    **Kırmızı için:** `(18/37 × 1) - (19/37 × 1) = -0.027`
    
    > 🚨 **Her 1 TL için BEKLENEN KAYIP = 2.7 kuruş!**
    """)
    
    # 3. HOUSE EDGE
    st.markdown("---")
    st.markdown("## 🏦 3. CASİNO AVANTAJI")
    st.markdown("""
    - **Avrupa Ruleti:** %2.7
    - **Amerikan Ruleti:** %5.26
    
    > Her 100 TL bahisten casino **2.70 TL** garanti kazanır!
    """)
    
    # 4. PSİKOLOJİK TUZAKLAR
    st.markdown("---")
    st.markdown("## 🧠 4. PSİKOLOJİK TUZAKLAR")
    st.markdown("""
    **1. Kumarbaz Yanılgısı:** "Arka arkaya kırmızı geldi, şimdi siyah gelmeli" → YANLIŞ!
    
    **2. Kayıptan Kaçınma:** Kaybettikçe daha çok oynama isteği
    
    **3. Yakın Kaçırma:** "Neredeyse kazanıyordum" hissi sizi kandırır
    """)
    
    # 5. UZUN VADE
    st.markdown("---")
    st.markdown("## 📉 5. UZUN VADEDE KAYBETME RİSKİ")
    
    risk_data = {
        "Tur Sayısı": [10, 50, 100, 500, 1000],
        "Kaybetme Riski": ["%24", "%76", "%92", "%98", "%99.99"]
    }
    st.dataframe(pd.DataFrame(risk_data), use_container_width=True, hide_index=True)
    
    # SONUÇ
    st.markdown("---")
    st.markdown("""
    ## 🎯 MATEMATİK PROJE ÖDEVİ SONUCU
    
    ### Hipotez:
    > "Kumar oyunları matematiksel olarak oyuncunun aleyhinedir"
    
    ### Kanıt:
    1. Beklenen Değer NEGATİF: **E = -0.027**
    2. Casino avantajı (House Edge) her zaman vardır: **%2.7**
    3. Uzun vadede kaybetme olasılığı **%99.99**
    
    ### Sonuç:
    > 🚨 **KISA VADEDE KAZANABİLİRSİN AMA UZUN VADEDE MATEMATİKSEL OLARAK KAYBEDERSİN!**
    """)
    
    # RESET BUTONU
    st.markdown("---")
    if st.button("🔄 YENİDEN DENE", use_container_width=True):
        st.session_state.bakiye = 1000
        st.session_state.baslangic_bakiye = 1000
        st.session_state.tur_sayisi = 0
        st.session_state.bakiye_gecmisi = [1000]
        st.session_state.son_sayi = None
        st.session_state.son_renk = None
        st.session_state.son_kazanc = 0
        st.session_state.tur_sonuclari = []
        st.session_state.toplam_kar = [0]
        st.session_state.bakiye_secildi = False
        st.rerun()
    
    st.stop()  # Burada dur, normal oyunu gösterme

# ==================== NORMAL OYUN EKRANI (Bakiye > 0 ise) ====================
col_rulet, col_bahis, col_grafik = st.columns([1, 1.2, 1.5])

with col_rulet:
    st.markdown('<div class="casino-card">', unsafe_allow_html=True)
    st.subheader("🎡 RULET ÇARKI")
    rulet_gorseli(st.session_state.son_sayi, st.session_state.son_renk)
    if st.session_state.son_sayi is not None:
        st.info(f"📊 **Son Sonuç:** {st.session_state.son_sayi} - {st.session_state.son_renk}")
    st.markdown('</div>', unsafe_allow_html=True)

with col_bahis:
    st.markdown('<div class="casino-card">', unsafe_allow_html=True)
    st.markdown(f'<p class="bakiye-text">💰 BAKİYE: {st.session_state.bakiye} TL 💰</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    bahis_turu = st.selectbox(
        "🎲 Bahis Türü Seç:",
        ["Renk", "Tek/Çift", "Düşük/Yüksek", "Düzine", "Sütun", "Tek Sayı"]
    )
    
    if bahis_turu == "Renk":
        bahis_degeri = st.selectbox("Renk seç:", ["Kırmızı", "Siyah", "Yeşil"])
    elif bahis_turu == "Tek/Çift":
        bahis_degeri = st.selectbox("Seç:", ["Tek", "Çift"])
    elif bahis_turu == "Düşük/Yüksek":
        bahis_degeri = st.selectbox("Aralık seç:", ["Düşük (1-18)", "Yüksek (19-36)"])
    elif bahis_turu == "Düzine":
        bahis_degeri = st.selectbox("Düzine seç:", [1, 2, 3])
    elif bahis_turu == "Sütun":
        bahis_degeri = st.selectbox("Sütun seç:", [1, 2, 3])
    else:
        bahis_degeri = st.number_input("Sayı seç (0-36):", min_value=0, max_value=36, step=1)
    
    bahis_miktari = st.number_input(
        "💰 Bahis Miktarı (TL):",
        min_value=10,
        max_value=st.session_state.bakiye,
        value=min(100, st.session_state.bakiye),
        step=10
    )
    
    oyna = st.button("🎰 ÇARKI ÇEVİR!", type="primary", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_grafik:
    st.markdown('<div class="casino-card">', unsafe_allow_html=True)
    st.subheader("📈 BAKİYE GRAFİĞİ")
    if len(st.session_state.bakiye_gecmisi) > 1:
        fig, ax = plt.subplots(figsize=(8, 4))
        x = range(len(st.session_state.bakiye_gecmisi))
        y = st.session_state.bakiye_gecmisi
        ax.plot(x, y, 'o-', color='gold', linewidth=2, markersize=6)
        ax.fill_between(x, y, alpha=0.3, color='gold')
        ax.set_xlabel('Tur Sayısı')
        ax.set_ylabel('Bakiye (TL)')
        ax.set_title('Bakiyenin Zamanla Değişimi')
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)
    else:
        st.info("Oynamaya başlayınca grafik burada görünecek.")
    st.markdown('</div>', unsafe_allow_html=True)

# OYUN MANTIĞI
if oyna and st.session_state.bakiye >= bahis_miktari:
    st.session_state.tur_sayisi += 1
    tur = st.session_state.tur_sayisi
    
    with st.spinner("🎡 Çark dönüyor..."):
        time.sleep(0.5)
        sonuc = rulet_cevir()
    
    # Bahsi düş
    st.session_state.bakiye -= bahis_miktari
    
    # Kazanç kontrolü
    kazandi_mi, carpan = kazanma_kontrolu(bahis_turu, bahis_degeri, sonuc)
    
    if kazandi_mi:
        odeme = bahis_miktari * carpan
        st.session_state.bakiye += odeme
        net = odeme - bahis_miktari
        st.session_state.son_kazanc = net
        st.success(f"🎉 KAZANDIN! +{net} TL")
    else:
        st.session_state.son_kazanc = -bahis_miktari
        st.error(f"💀 KAYBETTİN! -{bahis_miktari} TL")
    
    # Kaydet
    st.session_state.son_sayi = sonuc["sayi"]
    st.session_state.son_renk = sonuc["renk"]
    st.session_state.bakiye_gecmisi.append(st.session_state.bakiye)
    st.session_state.tur_sonuclari.append({
        "tur": tur,
        "bahis": bahis_miktari,
        "gelen": sonuc["sayi"],
        "kazanc": st.session_state.son_kazanc,
        "bakiye": st.session_state.bakiye
    })
    st.session_state.toplam_kar.append(st.session_state.toplam_kar[-1] + st.session_state.son_kazanc)
    
    st.info(f"🎯 **Sonuç:** {sonuc['sayi']} - {sonuc['renk']}")
    st.rerun()

# ALT BİLGİ
st.markdown("---")
st.markdown("""
<p style="text-align:center; color:gray; font-size:12px;">
🎓 Matematik Proje Ödevi - Kumarın Matematiği | Eğitim Amaçlıdır
</p>
""", unsafe_allow_html=True)
