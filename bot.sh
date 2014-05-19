#!/bin/bash

# bot working directory
cd /home/gbot/ggbot/src

# load virtualenv
source /home/gbot/ggbot/env/bin/activate


if [ -f "twistd.pid" ]; then
    TWISTD_PID=$(cat twistd.pid)
fi

case $1 in
    profile)
        if kill -0 $TWISTD_PID &> /dev/null; then
            echo "bot is already runnin"
        else
            echo "starting bot in profile mode..."
            twistd -n -y development.py -l tmp/twistd.log --profile=stats_obj --profiler=cProfile --savestats
        fi
    ;;
    devel)
        if kill -0 $TWISTD_PID &> /dev/null; then
            echo "bot is already runnin"
        else
            echo "starting bot in devel mode..."
            python development.py
        fi
    ;;
    start)
        if kill -0 $TWISTD_PID &> /dev/null; then
            echo "bot is already runnin"
        else
            echo "starting bot..."
            twistd -y development.py -l tmp/twistd.log
            echo "starting bot... done"
        fi
    ;;
    stop)
        if kill -0 $TWISTD_PID &> /dev/null; then
            echo "stopping bot..."
            kill $TWISTD_PID
            while kill -0 $TWISTD_PID &> /dev/null; do sleep 1; done
            echo "stopping bot... done"
        else
            echo "bot aint runnin"
        fi
    ;;
    restart)
        echo "restarting bot..."
        if kill -0 $TWISTD_PID &> /dev/null; then
            kill $TWISTD_PID
            while kill -0 $TWISTD_PID &> /dev/null; do sleep 1; done
        fi
        twistd -y development.py -l tmp/twistd.log
        echo "restarting bot... done"
    ;;
    status)
        if kill -0 $TWISTD_PID &> /dev/null; then
            echo "bot seems to be up and runnin (pid :$TWISTD_PID)"
        else
            echo "bot seems to be down"
        fi
    ;;
    *)
        echo "available commands => devel, profile, start, stop, restart, status"
    ;;
esac
