https://www.raspberrypirulo.net/entry/cron

*/15 * * * * python /home/gmimaki/tortoise_safe_checker/dht11_publish.py --endpoint a2pibis0kliefa3-ats.iot.ap-northeast-1.amazonaws.com --cert /home/gmimaki/certs/device.pem.crt --key /home/gmimaki/certs/private.pem.key --ca /home/gmimaki/certs/Amazon-root-CA-1.pem --topic tortoise_safe_checker/environment