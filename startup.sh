#!/bin/bash
#
# 
# 
#

# Get function from functions library
# Start SmartPlanter
start() {
  pm2 kill
        ### Starte Datareader ####
	pm2 start server.py --name Dashboard --interpreter python3 && pm2 start datareader.py --name Datareader --interpreter python3 && pm2 start timelaps.py --name Timelapse  --interpreter python3

        echo "Smartplanter wurde gestartet"
}

# Restart SmartPlanter
stop() {
        pm2 kill
        ### Now, delete the lock file ###
        echo "Smartplanter wurde gestoppt"
}
restart() {
        pm2 restart Dashboard Datareader
        ### Now, delete the lock file ###
        echo "Smartplanter wurde gestoppt"
}

### main logic ###
case "$1" in
  start)
        start
        ;;
  stop)
        stop
        ;;
  status)
        status FOO
        ;;
  restart|reload|condrestart)
        restart
        ;;
  *)
        echo $"Benutzung: $0 {start|stop|restart|reload|status}"
        exit 1
esac

exit 0
