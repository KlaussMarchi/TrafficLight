#include "device/index.h"
// AI THINKER ESP32-CAM

Device device;

void setup(){
    device.setup();
}

void loop(){
    device.handle();
}
