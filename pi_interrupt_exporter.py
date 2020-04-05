#!/usr/bin/env python3

import argparse
import RPi.GPIO as GPIO
from time import sleep
from prometheus_client import start_http_server, Summary, Counter

parser = argparse.ArgumentParser(description='Prometheus exporter for Raspberry Pi GPIO interrupts')
parser.add_argument('--pins', action='store', type=int, nargs='+', help='GPIO pin number(s)')
#parser.add_argument('--edge_type', action='store', default='BOTH', help='[BOTH|RISING|FALLING], default: BOTH') # FIXME
#parser.add_argument('--pull', action='store', default='DOWN', help='[UP|DOWN], Pull GPIO pin up or down, default: DOWN') # FIXME
parser.add_argument('--polling_interval', action='store', default=0.01, type=float, help='Interrupt detection loop interval, sec (float), default: 0')
parser.add_argument('--metric_name', action='store', default='gpio_interrupt', help='prometheus metric name, default: gpio_interrupt')
parser.add_argument('--metric_description', action='store', default='GPIO interrupt counter', help='prometheus metric description, default: GPIO interrupt counter')
parser.add_argument('--listen', action='store', default='0.0.0.0', help='bind to address, default: 0.0.0.0')
parser.add_argument('--port', action='store', type=int, default=8000, help='bind to port, default: 8000')
parser.add_argument('--debug', action="store_true", help='print all to stdout')
args = parser.parse_args()

if args.debug:
    print(args)

GPIO.setmode(GPIO.BCM)

for channel in args.pins:
    GPIO.setup(channel, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    #GPIO.add_event_detect(channel, GPIO.BOTH)
    #GPIO.add_event_detect(channel, GPIO.RISING)
    GPIO.add_event_detect(channel, GPIO.FALLING)

interrupts = Counter(args.metric_name, args.metric_description, ['pin'])

if __name__ == '__main__':
    start_http_server(args.port, args.listen)
    while True:
        for channel in args.pins:
            if GPIO.event_detected(channel):
                interrupts.labels(pin=channel).inc()
                if args.debug:
                    print('Edge on pin', channel)
        sleep(args.polling_interval)
