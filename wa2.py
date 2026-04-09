import streamlit as st
import pandas as pd
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

# Sayfa tasarımı
st.set_page_config(page_title="WhatsApp Bot", page_icon="💬")
st.title("💬 WhatsApp Toplu Mesaj Gönderici")

# Uyarı bölümü
st.warning("⚠️ DİKKAT: Günlük 300 mesaj limitini aşmayın. Hesabınızın banlanma riski vardır.")

# Kullanıcı Girişleri
uploaded_file = st.file_uploader("Numara listesini seçin (Excel)", type=["xlsx"])
message_text = st.text_area("Mesajınızı yazın:", placeholder="Merhaba, bu bir test mesajıdır...")

if st.button("Gönderimi Başlat"):
    if uploaded_file and message_text:
        df = pd.read_excel(uploaded_file, dtype={'Telefon': str})

        if 'Telefon' not in df.columns:
            st.error("Excel dosyasında 'Telefon' sütunu bulunamadı!")
        else:
            st.info("Tarayıcı hazırlanıyor... Lütfen açılan pencerede QR kodu taratın.")

            # Selenium Ayarları
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
            driver.get("https://web.whatsapp.com")

            # QR Kod için bekleme
            st.write("QR kodu tarattıktan sonra işlem başlayacaktır.")
            time.sleep(20)  # Kullanıcıya taratması için süre tanıyoruz

            status_text = st.empty()
            progress_bar = st.progress(0)

            for index, row in df.iterrows():
                if index >= 300:  # Günlük Limit
                    st.warning("300 mesaj limitine ulaşıldı.")
                    break

                phone = str(row['Telefon']).strip()
                url = f"https://web.whatsapp.com/send?phone={phone}&text={message_text}"
                driver.get(url)

                time.sleep(15)  # Sayfanın yüklenmesi için

                try:
                    actions = webdriver.ActionChains(driver)
                    actions.send_keys(Keys.ENTER)
                    actions.perform()

                    status_text.text(f"Gönderiliyor: {phone} ({index + 1}/{len(df)})")
                    progress_bar.progress((index + 1) / len(df))

                    # Ban riskine karşı rastgele bekleme
                    time.sleep(random.randint(20, 50))
                except Exception as e:
                    st.error(f"Hata oluştu: {phone}")

            driver.quit()
            st.success("İşlem başarıyla tamamlandı!")
    else:
        st.error("Lütfen dosya yükleyin ve mesaj yazın.")