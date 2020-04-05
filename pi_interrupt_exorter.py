#!/usr/bin/env python3

import argparse
import RPi.GPIO as GPIO
import time
from prometheus_client import start_http_server, Summary, Counter

parser = argparse.ArgumentParser(description='Prometheus exporter for Raspberry Pi GPIO interrupts')
parser.add_argument('--pin', action='store', type=int, help='GPIO pin number')
#parser.add_argument('--edge_type', action='store', default='BOTH', help='[BOTH|RISING|FALLING], default: BOTH') # FIXME
#parser.add_argument('--pull', action='store', default='DOWN', help='[UP|DOWN], Pull GPIO pin up or down, default: DOWN') # FIXME
parser.add_argument('--polling_interval', action='store', default=0.01, type=float, help='Pin polling interval, sec, float, default: 0.01')
parser.add_argument('--listen', action='store', default='0.0.0.0', help='bind to address, default: 0.0.0.0')
parser.add_argument('--metric_name', action='store', default='gpio_interrupt', help='prometheus metric name, default: gpio_interrupt')
parser.add_argument('--metric_description', action='store', default='GPIO interrupt counter', help='prometheus metric description, default: GPIO interrupt counter')
parser.add_argument('--port', action='store', type=int, default=8000, help='bind to port, default: 8000')
parser.add_argument('--debug', action="store_true", help='print all to stdout')
args = parser.parse_args()

if args.debug:
    print(args)

GPIO.setmode(GPIO.BCM)
GPIO.setup(args.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')

# TODO pin number in labels
interrupts = Counter(args.metric_name, args.metric_description)

@REQUEST_TIME.time()
def catch_interrupt():
    if GPIO.input(args.pin):
        if args.debug:
            print('Click!')
        interrupts.inc()
    else:
        if args.debug:
            print('nope')
        pass

if __name__ == '__main__':
    start_http_server(args.port, args.listen)
    while True:
        catch_interrupt()
        time.sleep(args.polling_interval)
