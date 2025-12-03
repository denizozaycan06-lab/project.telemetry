import socketio
import eventlet
import random
import math
import time

#  sunucu 
sio = socketio.Server(cors_allowed_origins='*')
app = socketio.WSGIApp(sio)

class E60M5_powertrain:
    def __init__(self):
        self.temp = 40
        self.oil_pressure = 1.5
        self.heating_rate = 0.08
        self.cooling_rate = 0.03
        self.gear = 1
        self.gear_ratios = { 1: 0.012, 2: 0.020, 3: 0.028, 4: 0.036, 5: 0.044, 6: 0.052, 7: 0.060 }
        self.speed = 0
        self.inertia = 0.05
        self.throttle = 0
        self.rpm = 800
        self.max_rpm = 8250
        self.idle_rpm = 750

    
    def set_throttle(self, value):
        self.throttle = max(0, min(100, value)) / 100.0

  
    def update(self):
        current_ratio = self.gear_ratios[self.gear]
        
        if self.speed == 0:
            self.speed = self.rpm * current_ratio

        if self.rpm > 8000 and self.gear < 7:
            self.gear += 1
            new_ratio = self.gear_ratios[self.gear]
            self.rpm = self.speed / new_ratio
        elif self.rpm < 2500 and self.gear > 1:
            self.gear -= 1
            new_ratio = self.gear_ratios[self.gear]
            rev_match_rpm = self.speed / new_ratio
            self.rpm = rev_match_rpm

        target_rpm = self.idle_rpm + (self.throttle * (self.max_rpm - self.idle_rpm))
        vibration = random.randint(-40, 80)
        self.rpm += (target_rpm - self.rpm) * self.inertia + (vibration * 0.1)
        self.speed = self.rpm * self.gear_ratios[self.gear]

        heat_load = (self.rpm / self.max_rpm) ** 2 * 2.0
        cool = (self.temp - 20) * self.cooling_rate
        self.temp += (heat_load - cool) * self.heating_rate
        self.oil_pressure = 1.5 + (self.rpm / 8250) * 5.5 + (random.random() * 0.2)

   
    def get_telemetry(self):
        status_msg = "CRUISING"
        if self.rpm > 8000: status_msg = "UPSHIFTING"
        elif self.throttle > 90: status_msg = "FULL THROTTLE"
        elif self.throttle == 0:
            if self.speed < 5: status_msg = "IDLE"
            elif self.rpm < 2600 and self.gear > 1: status_msg = "DOWNSHIFTING"
            else: status_msg = "COASTING"

        return {
            "gear": f"{self.gear}",
            "status": status_msg,
            "rpm": int(self.rpm),
            "speed": int(self.speed),
            "temp": round(self.temp, 1),
            "oil": round(self.oil_pressure, 1)
        }

car = E60M5_powertrain()


def telemetry_loop():
    print("Motor Başlatıldı - Veri Yayını Aktif...")
    while True:
        wave = math.sin(time.time() * 0.3)
        auto_throttle = 100 if wave > -0.5 else 0
        
        car.set_throttle(auto_throttle)
        car.update()
        
       
        sio.emit('telemetry_data', car.get_telemetry())
        
        
        sio.sleep(0.05) 


@sio.event
def connect(sid, environ):
    print(f'Web Sitesi Bağlandı: {sid}')

@sio.event
def disconnect(sid):
    print(f'Web Sitesi Koptu: {sid}')


if __name__ == '__main__':
    
    sio.start_background_task(telemetry_loop)
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)