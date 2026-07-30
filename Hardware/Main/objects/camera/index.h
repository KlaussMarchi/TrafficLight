#ifndef CAMERA_H
#define CAMERA_H

#include <Arduino.h>
#include "esp_camera.h"
#include "../../globals/constants.h"

template <typename Parent> class Camera{
  private:
    Parent* device;

  public:
    camera_fb_t* frame;

    Camera(Parent* dev): device(dev), frame(NULL){}

    void setup(){
        camera_config_t config = {};
        bool psram = psramFound();

        config.ledc_channel = LEDC_CHANNEL_0;
        config.ledc_timer   = LEDC_TIMER_0;
        config.pin_d0       = CAM_PIN_Y2;
        config.pin_d1       = CAM_PIN_Y3;
        config.pin_d2       = CAM_PIN_Y4;
        config.pin_d3       = CAM_PIN_Y5;
        config.pin_d4       = CAM_PIN_Y6;
        config.pin_d5       = CAM_PIN_Y7;
        config.pin_d6       = CAM_PIN_Y8;
        config.pin_d7       = CAM_PIN_Y9;
        config.pin_xclk     = CAM_PIN_XCLK;
        config.pin_pclk     = CAM_PIN_PCLK;
        config.pin_vsync    = CAM_PIN_VSYNC;
        config.pin_href     = CAM_PIN_HREF;
        config.pin_sccb_sda = CAM_PIN_SIOD;
        config.pin_sccb_scl = CAM_PIN_SIOC;
        config.pin_pwdn     = CAM_PIN_PWDN;
        config.pin_reset    = CAM_PIN_RESET;
        config.xclk_freq_hz = CAM_XCLK_FREQ;
        config.pixel_format = PIXFORMAT_JPEG;
        config.frame_size   = psram ? CAM_FRAME_SIZE : FRAMESIZE_QVGA;
        config.jpeg_quality = psram ? CAM_JPEG_QUALITY : 15;
        config.fb_count     = psram ? CAM_FB_COUNT : 1;
        config.grab_mode    = psram ? CAMERA_GRAB_LATEST : CAMERA_GRAB_WHEN_EMPTY;
        config.fb_location  = psram ? CAMERA_FB_IN_PSRAM : CAMERA_FB_IN_DRAM;

        while(esp_camera_init(&config) != ESP_OK){
            Serial.println("Erro ao inicializar a camera");
            delay(2000);
        }
    }

    void handle(){}

    bool update(){
        frame = esp_camera_fb_get();
        return frame != NULL;
    }

    void reset(){
        if(frame != NULL)
            esp_camera_fb_return(frame);

        frame = NULL;
    }
};

#endif
