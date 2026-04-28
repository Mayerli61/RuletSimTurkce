import streamlit as st
import random
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import time

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
    .kaybet {
        color: red;
        font-weight: bold;
    }
    .kazan {
        color: limegreen;
        font-weight: bold;
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
st.markdown('<p style="text-align: center; color: #cccccc;">Oynadıkça kazanmak sandığın kadar kolay değil...</p>', unsafe_allow_html=True)

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
    # Bakiye gösterimi
    st.markdown(f'<p class="bakiye-text">💰 BAKİYE: {st.session_state.bakiye} TL 💰</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Bahis seçenekleri
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
    else:  # Tek Sayı
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
        if st.session_state.bakiye < 1000:
            ax.set_facecolor('#330000')
        else:
            ax.set_facecolor('#1a1a2e')
        st.pyplot(fig)
    else:
        st.info("Oynamaya başlayınca grafik burada görünecek.")
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== OYUN MANTIĞI (GERÇEK RULET KURALLARI) ====================
if oyna and st.session_state.bakiye >= bahis_miktari and st.session_state.bakiye > 0:
    st.session_state.tur_sayisi += 1
    tur = st.session_state.tur_sayisi
    
    with st.spinner("🎡 Rulet çarkı dönüyor..."):
        time.sleep(0.5)
        sonuc = rulet_cevir()
    
    # Önce bahis düşülür
    st.session_state.bakiye -= bahis_miktari
    
    # Kazanç kontrolü
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
    
    # Kümülatif kar/zarar hesapla
    if len(st.session_state.toplam_kar) == 0:
        st.session_state.toplam_kar.append(st.session_state.son_kazanc)
    else:
        st.session_state.toplam_kar.append(st.session_state.toplam_kar[-1] + st.session_state.son_kazanc)
    
    # Sonuçları kaydet
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
    
    # Sonuç gösterimi
    if kazanc_mesaji.startswith("🎉"):
        st.success(kazanc_mesaji)
    else:
        st.error(kazanc_mesaji)
    st.info(f"🎯 **Rulet Sonucu:** {sonuc['sayi']} - {sonuc['renk']}")
    st.rerun()

# ==================== İSTATİSTİKLER BÖLÜMÜ ====================
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

# ==================== EĞİTİM BÖLÜMÜ ====================
st.markdown("---")
st.markdown("""
# 🎓 Neden Kumar Oynamamalıyız?

Kumar oyunları kısa süreli heyecan verebilir. Ancak matematiksel olarak sistem uzun vadede oyuncunun kaybetmesi üzerine kuruludur.

## 📉 Matematiksel Gerçek

Avrupa ruletinde:
- 18 kırmızı
- 18 siyah
- 1 yeşil sayı vardır.

Bu nedenle:
- Kırmızı gelme ihtimali %50 değildir.
- Casino her zaman küçük bir avantaja sahiptir.

Bu küçük fark uzun vadede büyük kayıplara dönüşür.

## 🧠 Psikolojik Etkiler

Kumar:
- "Bir sonraki elde kazanacağım" hissi oluşturur,
- Kaybedilen parayı geri kazanma isteği doğurur,
- Zamanla kontrol kaybına neden olabilir.

## ⚠️ Gerçek Hayatta Casinolar

- Kısa süreli kazançlara izin verebilir,
- Fakat uzun vadede avantaj her zaman sistemdedir.

Bu yüzden sürekli kazanan oyuncu sistemi gerçekçi değildir.

## ✅ Bu Projenin Amacı

Bu simülasyon:
- Kumarın matematiğini göstermek,
- Uzun vadede neden kaybettirdiğini anlatmak,
- Bilinç oluşturmak için hazırlanmıştır.
""")

# ==================== RESET SİSTEMİ ====================
if st.session_state.bakiye <= 0:
    st.error("⚠️ Bakiyen sıfırlandı!")
    if st.button("🔄 Oyunu Sıfırla"):
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
        st.rerun()

# ==================== ALT BİLGİ ====================
st.markdown("---")
st.markdown("""
<p style="text-align:center; color:gray; font-size:12px;">
🎰 Bu proje eğitim amaçlı hazırlanmıştır.
</p>
""", unsafe_allow_html=True)
