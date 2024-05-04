from aiot_ir_receiver import *
import music
from yolobit import *
button_a.on_pressed = None
button_b.on_pressed = None
button_a.on_pressed_ab = button_b.on_pressed_ab = -1
from mqtt import *
from machine import RTC
import ntptime
import time
from aiot_lcd1602 import LCD1602
from event_manager import *
from machine import Pin, SoftI2C
from aiot_dht20 import DHT20
from aiot_rgbled import RGBLed

aiot_ir_rx = IR_RX(Pin(pin1.pin, Pin.IN)); aiot_ir_rx.start();

# Mô tả hàm này...
def Change():
  global th_C3_B4ng_tin, RT, ADMIN, RH, PASS, STATUS, LUX, aiot_dht20, aiot_lcd1602, aiot_ir_rx, tiny_rgb
  if aiot_ir_rx.get_code() == IR_REMOTE_1:
    music.play(['A3:1'], wait=True)
    ADMIN = str(ADMIN) + '1'
  if aiot_ir_rx.get_code() == IR_REMOTE_2:
    music.play(['B3:1'], wait=True)
    ADMIN = str(ADMIN) + '2'
  if aiot_ir_rx.get_code() == IR_REMOTE_3:
    music.play(['C3:1'], wait=True)
    ADMIN = str(ADMIN) + '3'
  if aiot_ir_rx.get_code() == IR_REMOTE_F:
    STATUS = 0
    PASS = ''
    display.scroll(ADMIN)
  aiot_ir_rx.clear_code()

aiot_lcd1602 = LCD1602()

event_manager.reset()

aiot_dht20 = DHT20(SoftI2C(scl=Pin(22), sda=Pin(21)))

def on_event_timer_callback_a_h_Y_z_q():
  global th_C3_B4ng_tin, RT, RH, ADMIN, STATUS, PASS, LUX
  aiot_dht20.read_dht20()
  RT = aiot_dht20.dht20_temperature()
  RH = aiot_dht20.dht20_humidity()
  LUX = round(translate((pin2.read_analog()), 0, 4095, 0, 100))
  aiot_lcd1602.move_to(0, 0)
  aiot_lcd1602.putstr(RT)
  aiot_lcd1602.move_to(4, 0)
  aiot_lcd1602.putstr('*C')
  aiot_lcd1602.move_to(6, 0)
  aiot_lcd1602.putstr('  ')
  aiot_lcd1602.move_to(8, 0)
  aiot_lcd1602.putstr(RH)
  aiot_lcd1602.move_to(10, 0)
  aiot_lcd1602.putstr('%')
  aiot_lcd1602.move_to(11, 0)
  aiot_lcd1602.putstr('  ')
  aiot_lcd1602.move_to(13, 0)
  aiot_lcd1602.putstr(LUX)
  aiot_lcd1602.move_to(15, 0)
  aiot_lcd1602.putstr('%')
  mqtt.publish('V1', RT)
  mqtt.publish('V2', RH)
  mqtt.publish('V3', LUX)

event_manager.add_timer_event(30000, on_event_timer_callback_a_h_Y_z_q)

def on_event_timer_callback_H_M_C_M_o():
  global th_C3_B4ng_tin, RT, RH, ADMIN, STATUS, PASS, LUX
  aiot_lcd1602.move_to(0, 1)
  aiot_lcd1602.putstr(('%0*d' % (2, RTC().datetime()[2])))
  aiot_lcd1602.move_to(2, 1)
  aiot_lcd1602.putstr('/')
  aiot_lcd1602.move_to(3, 1)
  aiot_lcd1602.putstr(('%0*d' % (2, RTC().datetime()[1])))
  aiot_lcd1602.move_to(5, 1)
  aiot_lcd1602.putstr('/')
  aiot_lcd1602.move_to(6, 1)
  aiot_lcd1602.putstr(('%0*d' % (2, RTC().datetime()[0])))
  aiot_lcd1602.move_to(10, 1)
  aiot_lcd1602.putstr(' ')
  aiot_lcd1602.move_to(11, 1)
  aiot_lcd1602.putstr(('%0*d' % (2, RTC().datetime()[4])))
  aiot_lcd1602.move_to(14, 1)
  aiot_lcd1602.putstr(('%0*d' % (2, RTC().datetime()[5])))

event_manager.add_timer_event(30000, on_event_timer_callback_H_M_C_M_o)

def on_event_timer_callback_Q_i_o_L_W():
  global th_C3_B4ng_tin, RT, RH, ADMIN, STATUS, PASS, LUX
  aiot_lcd1602.move_to(13, 1)
  aiot_lcd1602.putstr(':')
  time.sleep_ms(1000)
  aiot_lcd1602.move_to(13, 1)
  aiot_lcd1602.putstr(' ')
  time.sleep_ms(1000)

event_manager.add_timer_event(2000, on_event_timer_callback_Q_i_o_L_W)

tiny_rgb = RGBLed(pin0.pin, 4)

def on_mqtt_message_receive_callback__V10_(th_C3_B4ng_tin):
  global RT, RH, ADMIN, STATUS, PASS, LUX
  if th_C3_B4ng_tin == '1':
    tiny_rgb.show(0, hex_to_rgb('#ff0000'))
  else:
    tiny_rgb.show(0, hex_to_rgb('#000000'))

def on_mqtt_message_receive_callback__V11_(th_C3_B4ng_tin):
  global RT, RH, ADMIN, STATUS, PASS, LUX
  tiny_rgb.show(0, hex_to_rgb(th_C3_B4ng_tin))

def on_mqtt_message_receive_callback__V12_(th_C3_B4ng_tin):
  global RT, RH, ADMIN, STATUS, PASS, LUX
  pin10.write_analog(round(translate((int(th_C3_B4ng_tin)), 0, 100, 0, 1023)))

def on_mqtt_message_receive_callback__V14_(th_C3_B4ng_tin):
  global RT, RH, ADMIN, STATUS, PASS, LUX
  if th_C3_B4ng_tin == 'A':
    pin4.servo_write(90)
    display.scroll('TUAN')
    time.sleep_ms(2000)
    pin4.servo_write(0)
  if th_C3_B4ng_tin == 'B':
    pin4.servo_write(90)
    display.scroll('NHUNG')
    time.sleep_ms(2000)
    pin4.servo_write(0)
  if th_C3_B4ng_tin == 'Z':
    display.clear()

# Mô tả hàm này...
def _C4_90_C4_83ng_K_C3_AD_K_C3_AAnh():
  global th_C3_B4ng_tin, RT, ADMIN, RH, PASS, STATUS, LUX, aiot_dht20, aiot_lcd1602, aiot_ir_rx, tiny_rgb
  mqtt.on_receive_message('V10', on_mqtt_message_receive_callback__V10_)
  mqtt.on_receive_message('V11', on_mqtt_message_receive_callback__V11_)
  mqtt.on_receive_message('V12', on_mqtt_message_receive_callback__V12_)
  mqtt.on_receive_message('V14', on_mqtt_message_receive_callback__V14_)

# Mô tả hàm này...
def Check():
  global th_C3_B4ng_tin, RT, ADMIN, RH, PASS, STATUS, LUX, aiot_dht20, aiot_lcd1602, aiot_ir_rx, tiny_rgb
  if aiot_ir_rx.get_code() == IR_REMOTE_1:
    music.play(['A3:1'], wait=True)
    PASS = str(PASS) + '1'
  if aiot_ir_rx.get_code() == IR_REMOTE_2:
    music.play(['B3:1'], wait=True)
    PASS = str(PASS) + '2'
  if aiot_ir_rx.get_code() == IR_REMOTE_3:
    music.play(['C3:1'], wait=True)
    PASS = str(PASS) + '3'
  if aiot_ir_rx.get_code() == IR_REMOTE_F:
    if PASS == str(ADMIN) + str(ADMIN):
      ADMIN = ''
      STATUS = 1
      PASS = ''
    else:
      if PASS == ADMIN:
        display.show(Image.YES)
        pin4.servo_write(90)
        time.sleep_ms(2000)
        pin4.servo_write(0)
      else:
        display.show(Image.NO)
        pin4.servo_write(0)
      PASS = ''
      time.sleep_ms(2000)
      display.clear()
  aiot_ir_rx.clear_code()

def on_event_timer_callback_M_y_D_J_W():
  global th_C3_B4ng_tin, RT, RH, ADMIN, STATUS, PASS, LUX
  if STATUS == 0:
    Check()
  else:
    Change()

event_manager.add_timer_event(100, on_event_timer_callback_M_y_D_J_W)

def on_event_timer_callback_k_U_d_I_F():
  global th_C3_B4ng_tin, RT, RH, ADMIN, STATUS, PASS, LUX
  if pin3.read_digital()==1:
    display.set_all('#ff0000')
  else:
    display.set_all('#000000')

event_manager.add_timer_event(100, on_event_timer_callback_k_U_d_I_F)

if True:
  display.scroll('AIoT')
  mqtt.connect_wifi('Chi Huong', 'nlhtnlat')
  mqtt.connect_broker(server='mqtt.ohstem.vn', port=1883, username='1852837', password='')
  ntptime.settime()
  (year, month, mday, week_of_year, hour, minute, second, milisecond) = RTC().datetime()
  RTC().init((year, month, mday, week_of_year, hour+7, minute, second, milisecond))
  aiot_lcd1602.clear()
  PASS = ''
  ADMIN = '123'
  STATUS = 0
  _C4_90_C4_83ng_K_C3_AD_K_C3_AAnh()
  display.scroll('OK')

while True:
  event_manager.run()
  mqtt.check_message()
  time.sleep_ms(1000)
