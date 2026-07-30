#ifndef DEVICE_H
#define DEVICE_H

#include <Arduino.h>
#include "../globals/constants.h"
#include "../objects/camera/index.h"
#include "../objects/protocol/index.h"

class Device{
  public:
    Camera<Device> camera;
    Protocol<Device> protocol;

    Device(): camera(this), protocol(this){}

    void setup(){
        Serial.begin(SERIAL_BAUDRATE);
        camera.setup();
        protocol.setup();
        Serial.println("READY");
    }

    void handle(){
        camera.handle();
        protocol.handle();
    }
};

#endif
