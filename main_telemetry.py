import socketio
import eventlet
from pymem import Pymem
import time

#SUNUCU
sio = socketio.Server(cors_allowed_origins='*')
app = socketio.WSGIApp(sio)

#Memory Hook
try:
   
    pm = Pymem("pcsx2-qt.exe") 
    print(">> BAĞLANTI BAŞARILI: M3 GTR TELEMETRİSİ AKTİF.")
except Exception as e:
    print(f"!! HATA: Emülatör bulunamadı. ({e})")
    exit()


# ADRESLER
# NOT: 0x koymayı unutma, bunlar Hexadecimal adreslerdir.

RPM_ADDR   = 0x24901E34CE4  # Motor Devri (Float)
SPEED_ADDR = 0x24901E34D00  # Hız (m/s) (Float)
GEAR_ADDR  = 0x24881E34BD4  # Vites (Byte) - Ekran görüntüsünden aldım



def telemetry_loop():
    print(">> YAYIN BAŞLADI: VERİ AKIŞI (60Hz)...")
    
    while True:
        try:
           
            rpm_val = pm.read_float(RPM_ADDR)
            speed_ms = pm.read_float(SPEED_ADDR)
            gear_val = pm.read_bytes(GEAR_ADDR, 1) 
            
         
            gear_int = int.from_bytes(gear_val, "little")

         
            speed_kmh = speed_ms * 3.6 
            
            gear_str = str(gear_int)
            if gear_int == -1: gear_str = "R"
            elif gear_int == 0: gear_str = "N" 

           
            data = {
                "rpm": int(rpm_val),
                "speed": int(speed_kmh),
                "gear": gear_str, 
                "temp": 90,     # Sabit (Yağ sıcaklığı)
                "oil": 4.5,     # Sabit (Basınç)
                "status": "LIVE - TRACK MODE"
            }
            
            
            sio.emit('telemetry_data', data)
            
           
            sio.sleep(0.016) 
            
        except Exception as e:
            print(f"Okuma Hatası: {e}")
            sio.sleep(1)

if __name__ == '__main__':
    sio.start_background_task(telemetry_loop)
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)