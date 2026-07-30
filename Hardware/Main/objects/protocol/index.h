#ifndef PROTOCOL_H
#define PROTOCOL_H

#include <Arduino.h>
#include "esp_camera.h"
#include "../../globals/constants.h"

template <typename Parent> class Protocol{
  private:
    Parent* device;

  public:
    Protocol(Parent* dev): device(dev){}

    void setup(){}

    void handle(){
        if(!check()) return;
        if(!device->camera.update()) return;

        send();
        device->camera.reset();
    }

    bool check(){
        bool requested = false;

        while(Serial.available())
            if(Serial.read() == PROTOCOL_REQUEST)
                requested = true;

        return requested;
    }

    void send(){
        camera_fb_t* frame = device->camera.frame;
        uint32_t size      = frame->len;

        Serial.print(PROTOCOL_HEADER);
        Serial.write((const uint8_t*) &size, sizeof(size));

        for(uint32_t ix = 0; ix < size; ix += PROTOCOL_CHUNK){
            uint32_t n = (size - ix < PROTOCOL_CHUNK) ? size - ix : PROTOCOL_CHUNK;

            Serial.write(frame->buf + ix, n);
            Serial.flush();
            delayMicroseconds(PROTOCOL_GAP);
        }
    }
};

#endif
