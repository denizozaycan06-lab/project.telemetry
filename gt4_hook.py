from pymem import Pymem
import time

try:
    # 1. PCSX2'ye Kanca At
    # (Görev Yöneticisi'nde işlem adı neyse onu yaz: pcsx2.exe veya pcsx2-qt.exe)
    pm = Pymem("pcsx2-qt.exe") 
    print(">> BAĞLANTI BAŞARILI: PCSX2 HACKLENDİ.")
except Exception as e:
    print(f"!! HATA: PCSX2 bulunamadı. Emülatör açık mı? İşlem adı doğru mu? ({e})")
    exit()

# 2. Senin Bulduğun Adres (Bunu değiştir!)
RPM_ADDRESS = 0x24901E34CE4  # <--- BURAYA KENDİ ADRESİNİ YAZ

print(">> VERİ AKIŞI BAŞLATILIYOR (FLOAT MODU)...")

while True:
    try:
        # Adresten 'Float' oku (Ondalıklı Sayı)
        current_rpm = pm.read_float(RPM_ADDRESS)
        
        print(f"RPM: {current_rpm:.2f}")
        
        time.sleep(0.1)
        
    except Exception as e:
        print(f"Okuma Hatası: {e}")