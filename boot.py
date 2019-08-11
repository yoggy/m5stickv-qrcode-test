# m5stick-qrcode-test.py - QRCode Test for M5StickV
import lcd
import sensor
import time
import audio
from fpioa_manager import fm
from machine import I2C
from Maix import I2S, GPIO

def draw_text(img, str, x, y, s):
    for dx in range(-2,2):
        for dy in range(-2,2):
            img.draw_string(x+dx, y+dy, str, color=(0,0,0), scale=s, mono_space=False)
    img.draw_string(x, y, str, color=(255,255,255), scale=s,mono_space=False)

def play_beep():
    global wav_dev

    print("beep")
    try:
        player = audio.Audio(path = "/flash/beep.wav") # 32bit float, 22.05kHz
        player.volume(50)
        wav_info = player.play_process(wav_dev)
        wav_dev.channel_config(wav_dev.CHANNEL_1, I2S.TRANSMITTER,resolution = I2S.RESOLUTION_16_BIT, align_mode = I2S.STANDARD_MODE)
        wav_dev.set_sample_rate(wav_info[1])
        while True:
            ret = player.play()
            if ret == None:
                break
            elif ret==0:
                break
        player.finish()
    except:
        pass

def init():
    global wav_dev, spk_sd

    lcd.init()
    lcd.rotation(2)

    # for wav
    fm.register(board_info.SPK_SD, fm.fpioa.GPIO0)
    spk_sd=GPIO(GPIO.GPIO0, GPIO.OUT)
    spk_sd.value(1) #Enable the SPK output
    fm.register(board_info.SPK_DIN,fm.fpioa.I2S0_OUT_D1)
    fm.register(board_info.SPK_BCLK,fm.fpioa.I2S0_SCLK)
    fm.register(board_info.SPK_LRCLK,fm.fpioa.I2S0_WS)
    wav_dev = I2S(I2S.DEVICE_0)

    # button
    fm.register(board_info.BUTTON_A, fm.fpioa.GPIO1)
    but_a=GPIO(GPIO.GPIO1, GPIO.IN, GPIO.PULL_UP)

    if but_a.value() == 0:
        sys.exit()

    sensor.reset()
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.VGA)
    sensor.run(1)

def main_loop():
    payload_str = ""
    beep_count = 0
    while(True):

        img = sensor.snapshot()

        qr_codes = img.find_qrcodes()
        if len(qr_codes) > 0:
            if payload_str == "" and beep_count == 0:
                play_beep()
            payload_str = qr_codes[0].payload()
            print("find qrcode...payload=" + payload_str)
            beep_count = 3
        else:
            payload_str = ""
            beep_count = beep_count - 1 if beep_count > 1 else 0


        tmp = img.resize(240, 135)

        draw_text(tmp, "QR Code test...", 5, 5, 3)
        draw_text(tmp, payload_str, 5, 90, 2)

        lcd.display(tmp)

# main
init()
main_loop()
