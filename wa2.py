import streamlit as st
import pandas as pd
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

# Sayfa Ayarları
st.set_page_config(page_title="WhatsApp Bot", page_icon="💬")
st.title("💬 Kişiselleştirilmiş WhatsApp Botu")

# Uyarı ve Bilgilendirme
st.warning("⚠️ Günlük 300 mesaj limitini aşmayın.")
st.info("💡 Mesaj içinde ismin geçmesini istediğiniz yere **{AdSoyad}** yazın. \n\nÖrnek: *Merhaba {AdSoyad}, nasılsınız?*")

# Dosya Yükleme
uploaded_file = st.file_uploader("Excel Dosyası Seç (.xlsx)", type=["xlsx"])

# Mesaj Metni
message_template = st.text_area("Mesaj Taslağı:",
                                placeholder="Merhaba {AdSoyad}, bu bir deneme mesajıdır.",
                                height=150)

# Önizleme (Preview) Bölümü
if uploaded_file and message_template:
    try:
        df_preview = pd.read_excel(uploaded_file, dtype={'Telefon': str, 'AdSoyad': str}).head(1)
        if 'AdSoyad' in df_preview.columns:
            sample_name = df_preview['AdSoyad'].iloc[0]
            preview_msg = message_template.replace("{AdSoyad}", str(sample_name))
            st.subheader("Mesaj Önizleme (İlk Kayıt):")
            st.code(preview_msg)
        else:
            st.error("Excel'de 'AdSoyad' sütunu bulunamadı!")
    except:
        pass

if st.button("GÖNDERİMİ BAŞLAT"):
    if uploaded_file and message_template:
        df = pd.read_excel(uploaded_file, dtype={'Telefon': str, 'AdSoyad': str})

        if 'Telefon' not in df.columns or 'AdSoyad' not in df.columns:
            st.error("Excel'de 'Telefon' veya 'AdSoyad' sütunları eksik!")
        else:
            st.info("Tarayıcı açılıyor... QR kodu taratın.")
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
            driver.get("https://web.whatsapp.com")

            time.sleep(20)  # QR tarama süresi

            progress_bar = st.progress(0)
            status_text = st.empty()

            for index, row in df.iterrows():
                if index >= 300: break

                name = str(row['AdSoyad']).strip()
                phone = str(row['Telefon']).strip()

                # Taslaktaki {AdSoyad} yerini Excel'deki AdSoyadle değiştir
                personalized_message = message_template.replace("{AdSoyad}", name)

                # URL üzerinden gönderim
                url = f"https://web.whatsapp.com/send?phone={phone}&text={personalized_message}"
                driver.get(url)

                time.sleep(15)  # Yükleme beklemesi

                try:
                    actions = webdriver.ActionChains(driver)
                    actions.send_keys(Keys.ENTER)
                    actions.perform()

                    status_text.text(f"Gönderildi: {name} ({phone})")
                    progress_bar.progress((index + 1) / len(df))

                    time.sleep(random.randint(20, 50))
                except:
                    st.error(f"Hata: {name} ({phone})")

            driver.quit()
            st.success("İşlem tamamlandı!")
    else:
        st.error("Dosya ve mesaj şablonu eksik.")