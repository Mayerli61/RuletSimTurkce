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
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    .formul {
        background-color: #0f0f0f;
        padding: 15px;
        border-radius: 10px;
        font-family: monospace;
        font-size: 18px;
        text-align: center;
        border-left: 5px solid gold;
    }
</style>
""", unsafe_allow_html=True)

# ==================== SESSION STATE BAŞLANGIÇ ====================
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
    st.session_state.kazanma_orani_gecmisi = []
    st.session_state.bakiye_secildi = False

# ==================== BAŞLANGIÇ BAKİYESİ SEÇİMİ ====================
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
    elif 25 <= sayi <= 36:
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
            box-shadow: 0 0 20px rgba(255,215,0,0.5);
        ">
            <span style="font-size: 64px; font-weight: bold; color: {text_color}; text-shadow: 2px 2px 4px black;">
                {son_sayi if son_sayi is not None else "?"}
            </span>
        </div>
        """, unsafe_allow_html=True)

# ==================== ANA BAŞLIK ====================
st.markdown('<h1 class="main-title">🎰 RULET SİMÜLASYONU 🎰</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #cccccc;">Matematik Proje Ödevi - Kumarın Matematiği</p>', unsafe_allow_html=True)

# ==================== ANA EKRAN - 3 KOLON ====================
col_rulet, col_bahis, col_grafik = st.columns([1, 1.2, 1.5])

with col_rulet:
    st.markdown('<div class="casino-card">', unsafe_allow_html=True)
    st.subheader("🎡 RULET ÇARKI")
    rulet_gorseli(st.session_state.son_sayi, st.session_state.son_renk)
    if st.session_state.son_sayi is not None:
        st.info(f"📊 **Son Sonuç:** {st.session_state.son_sayi} - {st.session_state.son_renk}")
        if st.session_state.son_kazanc is not None:
            if st.session_state.son_kazanc > 0:
                st.success(f"✨ +{st.session_state.son_kazanc} TL Kazandın!")
            else:
                st.error(f"💔 {st.session_state.son_kazanc} TL Kaybettin!")
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
        max_value=st.session_state.bakiye if st.session_state.bakiye > 0 else 10,
        value=min(100, st.session_state.bakiye) if st.session_state.bakiye > 0 else 10,
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
        ax.axhline(y=st.session_state.bakiye_gecmisi[0], color='gray', linestyle='--', alpha=0.5, label='Başlangıç')
        ax.set_xlabel('Tur Sayısı')
        ax.set_ylabel('Bakiye (TL)')
        ax.set_title('Oynadıkça Bakiyen Nasıl Değişiyor?')
        ax.grid(True, alpha=0.3)
        ax.legend()
        ax.set_facecolor('#1a1a2e')
        st.pyplot(fig)
    else:
        st.info("Oynamaya başlayınca grafik burada görünecek.")
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== OYUN MANTIĞI ====================
if oyna and st.session_state.bakiye >= bahis_miktari and st.session_state.bakiye > 0:
    st.session_state.tur_sayisi += 1
    tur = st.session_state.tur_sayisi
    
    with st.spinner("🎡 Rulet çarkı dönüyor..."):
        time.sleep(0.5)
        sonuc = rulet_cevir()
    
    st.session_state.bakiye -= bahis_miktari
    
    kazandi_mi, carpan = kazanma_kontrolu(bahis_turu, bahis_degeri, sonuc)
    
    if kazandi_mi:
        odeme = bahis_miktari * carpan
        st.session_state.bakiye += odeme
        net = odeme - bahis_miktari
        st.session_state.son_kazanc = net
        kazanc_mesaji = f"🎉 KAZANDIN! +{net} TL"
    else:
        st.session_state.son_kazanc = -bahis_miktari
        kazanc_mesaji = f"💀 KAYBETTİN! -{bahis_miktari} TL"
    
    if len(st.session_state.toplam_kar) == 0:
        st.session_state.toplam_kar.append(st.session_state.son_kazanc)
    else:
        st.session_state.toplam_kar.append(st.session_state.toplam_kar[-1] + st.session_state.son_kazanc)
    
    st.session_state.son_sayi = sonuc["sayi"]
    st.session_state.son_renk = sonuc["renk"]
    st.session_state.bakiye_gecmisi.append(st.session_state.bakiye)
    st.session_state.tur_sonuclari.append({
        "tur": tur,
        "bahis_turu": bahis_turu,
        "bahis_degeri": bahis_degeri,
        "bahis_miktari": bahis_miktari,
        "gelen_sayi": sonuc["sayi"],
        "gelen_renk": sonuc["renk"],
        "kazanc": st.session_state.son_kazanc,
        "bakiye": st.session_state.bakiye
    })
    
    if kazanc_mesaji.startswith("🎉"):
        st.success(kazanc_mesaji)
    else:
        st.error(kazanc_mesaji)
    st.info(f"🎯 **Rulet Sonucu:** {sonuc['sayi']} - {sonuc['renk']}")
    st.rerun()

# ==================== İSTATİSTİKLER BÖLÜMÜ ====================
if st.session_state.bakiye > 0:
    st.markdown("---")
    st.markdown("## 🔬 OYUN İSTATİSTİKLERİN")
    
    col_stat1, col_stat2 = st.columns(2)
    
    with col_stat1:
        st.markdown('<div class="casino-card">', unsafe_allow_html=True)
        st.subheader("📊 OYUN İSTATİSTİKLERİN")
        if len(st.session_state.tur_sonuclari) > 0:
            df = pd.DataFrame(st.session_state.tur_sonuclari)
            
            toplam_oynanan = len(df)
            toplam_kayip = df[df["kazanc"] < 0]["kazanc"].sum() if len(df[df["kazanc"] < 0]) > 0 else 0
            toplam_kazanc = df[df["kazanc"] > 0]["kazanc"].sum() if len(df[df["kazanc"] > 0]) > 0 else 0
            kazanma_sayisi = len(df[df["kazanc"] > 0])
            kaybetme_sayisi = len(df[df["kazanc"] < 0])
            kazanma_orani = (kazanma_sayisi / toplam_oynanan) * 100 if toplam_oynanan > 0 else 0
            
            metric_col1, metric_col2, metric_col3 = st.columns(3)
            with metric_col1:
                st.metric("Toplam Oynanan Tur", toplam_oynanan)
                st.metric("Kazanma Oranı", f"%{kazanma_orani:.1f}")
            with metric_col2:
                st.metric("Toplam Kazanç", f"+{toplam_kazanc:.0f} TL" if toplam_kazanc > 0 else f"{toplam_kazanc:.0f} TL")
                st.metric("Kazanma Sayısı", kazanma_sayisi)
            with metric_col3:
                st.metric("Toplam Kayıp", f"{toplam_kayip:.0f} TL")
                st.metric("Kaybetme Sayısı", kaybetme_sayisi)
            
            st.metric("📈 Net Kar/Zarar", f"{st.session_state.bakiye - st.session_state.baslangic_bakiye:.0f} TL", 
                      delta=f"{((st.session_state.bakiye - st.session_state.baslangic_bakiye) / st.session_state.baslangic_bakiye * 100):.1f}%")
            
            st.markdown("**📋 Son 10 Oyun:**")
            st.dataframe(df.tail(10)[["tur", "bahis_turu", "bahis_miktari", "gelen_sayi", "kazanc", "bakiye"]], 
                         use_container_width=True)
        else:
            st.info("Henüz oyun oynamadınız. Çarkı çevirerek başlayın!")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_stat2:
        st.markdown('<div class="casino-card">', unsafe_allow_html=True)
        st.subheader("📉 KÜMÜLATİF KAR/ZARAR GRAFİĞİ")
        if len(st.session_state.toplam_kar) > 1:
            fig_kar, ax_kar = plt.subplots(figsize=(8, 4))
            x_kar = range(len(st.session_state.toplam_kar))
            y_kar = st.session_state.toplam_kar
            
            colors = ['green' if val >= 0 else 'red' for val in y_kar]
            ax_kar.bar(x_kar, y_kar, color=colors, alpha=0.7, width=0.8)
            ax_kar.axhline(y=0, color='gray', linestyle='-', linewidth=1)
            ax_kar.plot(x_kar, y_kar, 'b-o', linewidth=1.5, markersize=4, alpha=0.5)
            
            ax_kar.set_xlabel('Tur Sayısı')
            ax_kar.set_ylabel('Kümülatif Kar/Zarar (TL)')
            ax_kar.set_title('Oynadıkça Toplam Kar/Zarar Durumun')
            ax_kar.grid(True, alpha=0.3)
            
            ax_kar.fill_between(x_kar, y_kar, 0, where=(np.array(y_kar) >= 0), 
                                color='green', alpha=0.2, label='Kâr Bölgesi')
            ax_kar.fill_between(x_kar, y_kar, 0, where=(np.array(y_kar) <= 0), 
                                color='red', alpha=0.2, label='Zarar Bölgesi')
            ax_kar.legend(loc='upper left')
            
            st.pyplot(fig_kar)
            
            toplam_kar_zarar = st.session_state.toplam_kar[-1] if st.session_state.toplam_kar else 0
            if toplam_kar_zarar > 0:
                st.success(f"🎉 **Toplam Kârınız:** +{toplam_kar_zarar:.0f} TL")
            elif toplam_kar_zarar < 0:
                st.error(f"💸 **Toplam Zararınız:** {toplam_kar_zarar:.0f} TL")
            else:
                st.info("📊 **Toplam Kar/Zarar:** 0 TL (Başabaş)")
        else:
            st.info("Oynamaya başlayınca kar/zarar grafiği burada görünecek.")
        st.markdown('</div>', unsafe_allow_html=True)

# ==================== BAKİYE SIFIRLANINCA EĞİTİM EKRANI (SADECE BURADA GÖSTER) ====================
if st.session_state.bakiye <= 0:
    # Tüm ana içeriği temizle ve sadece eğitim ekranını göster
    st.empty()
    
    st.markdown("""
    <div style="text-align: center; padding: 50px;">
        <h1 style="color: red; font-size: 48px;">⚠️ BAKİYEN SIFIRLANDI! ⚠️</h1>
        <p style="font-size: 24px;">Şimdi kumarın matematiğini öğrenme zamanı...</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Oyun istatistikleri
    if len(st.session_state.tur_sonuclari) > 0:
        df = pd.DataFrame(st.session_state.tur_sonuclari)
        toplam_oynanan = len(df)
        kazanma_sayisi = len(df[df["kazanc"] > 0])
        kaybetme_sayisi = len(df[df["kazanc"] < 0])
        toplam_yatirilan = df["bahis_miktari"].sum()
        toplam_kayip = df[df["kazanc"] < 0]["kazanc"].sum() if len(df[df["kazanc"] < 0]) > 0 else 0
        toplam_kazanc = df[df["kazanc"] > 0]["kazanc"].sum() if len(df[df["kazanc"] > 0]) > 0 else 0
        
        st.markdown("## 📊 OYUN SONU İSTATİSTİKLERİN")
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Toplam Tur", toplam_oynanan)
        with col2:
            st.metric("Kazanma Sayısı", kazanma_sayisi)
        with col3:
            st.metric("Kaybetme Sayısı", kaybetme_sayisi)
        with col4:
            st.metric("Toplam Yatırılan", f"{toplam_yatirilan:.0f} TL")
        with col5:
            net_sonuc = st.session_state.bakiye - st.session_state.baslangic_bakiye
            st.metric("Net Sonuç", f"{net_sonuc:.0f} TL", delta=f"{net_sonuc:.0f} TL")
        
        kazanma_orani = (kazanma_sayisi / toplam_oynanan * 100) if toplam_oynanan > 0 else 0
        st.warning(f"🎯 **Senin Kazanma Oranın:** %{kazanma_orani:.1f} | **Rulet Teorik Oranı:** %48.65")
    
    # ==================== MATEMATİK EĞİTİM BÖLÜMÜ ====================
    st.markdown("---")
    st.markdown("# 🎓 KUMARIN MATEMATİĞİ (Proje Konusu)")
    
    # 1. BÖLÜM: OLASILIKLAR
    st.markdown('<div class="egitim-card">', unsafe_allow_html=True)
    st.markdown("## 📊 1. KAZANMA OLASILIKLARI")
    
    col_prob1, col_prob2 = st.columns(2)
    
    with col_prob1:
        prob_data = {
            "Bahis Türü": ["Kırmızı/Siyah", "Tek/Çift", "Düşük/Yüksek", "Düzine", "Sütun", "Tek Sayı", "Yeşil"],
            "Kazanma İhtimali": ["18/37 = %48.65", "18/37 = %48.65", "18/37 = %48.65", "12/37 = %32.43", "12/37 = %32.43", "1/37 = %2.70", "1/37 = %2.70"],
            "Kazanç Çarpanı": ["1x", "1x", "1x", "2x", "2x", "35x", "36x"]
        }
        prob_df = pd.DataFrame(prob_data)
        st.dataframe(prob_df, use_container_width=True, hide_index=True)
    
    with col_prob2:
        fig_prob, ax_prob = plt.subplots(figsize=(8, 5))
        bahisler = ["Kırmızı", "Düzine", "Tek Sayı"]
        olasiliklar = [48.65, 32.43, 2.70]
        renkler = ['red', 'orange', 'green']
        ax_prob.bar(bahisler, olasiliklar, color=renkler, alpha=0.7)
        ax_prob.set_ylabel('Kazanma Olasılığı (%)')
        ax_prob.set_title('Farklı Bahis Türlerinde Kazanma İhtimali')
        ax_prob.set_ylim(0, 60)
        for i, v in enumerate(olasiliklar):
            ax_prob.text(i, v + 1, f"%{v}", ha='center', fontweight='bold')
        ax_prob.grid(True, alpha=0.3)
        st.pyplot(fig_prob)
    
    st.markdown("""
    > 📌 **Not:** Toplam 37 sayı vardır (0-36). Yeşil 0 sayısı casinonun avantajını oluşturur.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 2. BÖLÜM: BEKLENEN DEĞER
    st.markdown('<div class="egitim-card">', unsafe_allow_html=True)
    st.markdown("## 🔢 2. BEKLENEN DEĞER (EXPECTED VALUE)")
    
    col_ev1, col_ev2 = st.columns(2)
    
    with col_ev1:
        st.markdown("""
        ### Formül:
        `E = (Kazanma Olasılığı × Kazanç) - (Kaybetme Olasılığı × Kayıp)`
        
        ### Kırmızı bahsi için hesap:
        - Kazanma: `18/37 = 0.4865` × `(+1)` = **+0.4865**
        - Kaybetme: `19/37 = 0.5135` × `(-1)` = **-0.5135**
        
        ### SONUÇ:
        > `E = 0.4865 - 0.5135 = **-0.027**`
        
        **Yani her 1 TL bahis için BEKLENEN KAYIP = 2.7 kuruş!**
        """)
    
    with col_ev2:
        fig_ev, ax_ev = plt.subplots(figsize=(8, 4))
        bahisler = [10, 50, 100, 500, 1000]
        beklenen_kayip = [b * 0.027 for b in bahisler]
        ax_ev.bar(range(len(bahisler)), beklenen_kayip, color='red', alpha=0.7, edgecolor='darkred')
        ax_ev.set_xticks(range(len(bahisler)))
        ax_ev.set_xticklabels([f"{b} TL" for b in bahisler])
        ax_ev.set_ylabel('Beklenen Kayıp (TL)')
        ax_ev.set_xlabel('Yatırılan Bahis')
        ax_ev.set_title('BEKLENEN KAYIP GRAFİĞİ')
        ax_ev.grid(True, alpha=0.3)
        for i, v in enumerate(beklenen_kayip):
            ax_ev.text(i, v + 0.5, f"{v:.2f} TL", ha='center', fontweight='bold')
        st.pyplot(fig_ev)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 3. BÖLÜM: HOUSE EDGE
    st.markdown('<div class="egitim-card">', unsafe_allow_html=True)
    st.markdown("## 🏦 3. CASİNO AVANTAJI (HOUSE EDGE)")
    
    col_he1, col_he2 = st.columns(2)
    
    with col_he1:
        st.markdown("""
        ### House Edge = Casino'nun Garantili Kazancı
        
        **Avrupa Ruleti:** `1/37 = %2.7`
        
        **Amerikan Ruleti:** `2/38 = %5.26` (Çift sıfırlı)
        
        #### Ne Anlama Geliyor?
        - Her 100 TL bahis yapıldığında **casino 2.70 TL kazanır**
        - Her 1.000.000 TL'lik bahiste **casino 27.000 TL kazanır**
        - Bu para **OYUNCULARIN KAYBETTİĞİ PARADIR!**
        """)
    
    with col_he2:
        fig_he, ax_he = plt.subplots(figsize=(8, 5))
        labels = ['Oyuncu Kaybı', 'Casino Kazancı']
        sizes = [97.3, 2.7]
        colors = ['#ff4444', '#44ff44']
        explode = (0, 0.1)
        ax_he.pie(sizes, explode=explode, labels=labels, colors=colors,
                autopct='%1.1f%%', shadow=True, startangle=90)
        ax_he.set_title('100 TL Bahiste PARA DAĞILIMI')
        st.pyplot(fig_he)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 4. BÖLÜM: PSİKOLOJİK TUZAKLAR
    st.markdown('<div class="egitim-card">', unsafe_allow_html=True)
    st.markdown("## 🧠 4. NEDEN KAYBEDERİZ? (Psikolojik Faktörler)")
    
    col_psy1, col_psy2 = st.columns(2)
    
    with col_psy1:
        st.markdown("""
        ### 1. **Kumarbaz Yanılgısı (Gambler's Fallacy)**
        > "Arka arkaya 5 kırmızı geldi, şimdi mutlaka siyah gelmeli!"
        
        **GERÇEK:** Her çeviriş BAĞIMSIZDIR! Olasılık her zaman %48.65.
        
        ### 2. **Kayıptan Kaçınma (Loss Aversion)**
        > "Kaybettiğim parayı geri kazanana kadar bırakmayacağım!"
        
        **GERÇEK:** Kaybetme acısı, kazanma sevincinden **2 KAT DAHA GÜÇLÜDÜR**.
        """)
    
    with col_psy2:
        st.markdown("""
        ### 3. **Yakın Kaçırma Etkisi (Near Miss Effect)**
        > "Bir sayı farkla kaçırdım, neredeyse kazanıyordum!"
        
        **GERÇEK:** Beyniniz "neredeyse kazandım" hissini gerçek kazanç gibi algılar.
        
        ### 4. **Batık Maliyet (Sunk Cost Fallacy)**
        > "Şimdiye kadar çok para verdim, çekilirsem hepsi boşa gidecek!"
        
        **GERÇEK:** Geçmiş kayıplarınızı geri kazanma şansınız YOKTUR!
        """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 5. BÖLÜM: UZUN VADELİ KAYIP
    st.markdown('<div class="egitim-card">', unsafe_allow_html=True)
    st.markdown("## 📉 5. UZUN VADEDE NE OLUR?")
    
    col_long1, col_long2 = st.columns(2)
    
    with col_long1:
        st.markdown("""
        ### Büyük Sayılar Kanunu
        Ne kadar çok oynarsan, gerçek olasılıklara o kadar yaklaşırsın.
        
        | Tur Sayısı | Kaybetme Riski |
        |------------|----------------|
        | 10 Tur | **%24** |
        | 50 Tur | **%76** |
        | 100 Tur | **%92** |
        | 500 Tur | **%98** |
        | 1000 Tur | **%99.99** |
        
        > ⚠️ **SONUÇ:** Uzun vadede KAYBETMEK MATEMATİKSEL ZORUNLULUKTUR!
        """)
    
    with col_long2:
        fig_long, ax_long = plt.subplots(figsize=(8, 4))
        n_values =
