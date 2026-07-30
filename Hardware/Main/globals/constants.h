#ifndef CONSTANTS_H
#define CONSTANTS_H

#define SERIAL_BAUDRATE    921600

#define PROTOCOL_HEADER    "IMG"
#define PROTOCOL_REQUEST   'F'
#define PROTOCOL_CHUNK     2048
#define PROTOCOL_GAP       500

#define CAM_XCLK_FREQ      20000000
#define CAM_FRAME_SIZE     FRAMESIZE_VGA
#define CAM_JPEG_QUALITY   12
#define CAM_FB_COUNT       2

#define CAM_PIN_PWDN       32
#define CAM_PIN_RESET      -1
#define CAM_PIN_XCLK       0
#define CAM_PIN_SIOD       26
#define CAM_PIN_SIOC       27
#define CAM_PIN_Y9         35
#define CAM_PIN_Y8         34
#define CAM_PIN_Y7         39
#define CAM_PIN_Y6         36
#define CAM_PIN_Y5         21
#define CAM_PIN_Y4         19
#define CAM_PIN_Y3         18
#define CAM_PIN_Y2         5
#define CAM_PIN_VSYNC      25
#define CAM_PIN_HREF       23
#define CAM_PIN_PCLK       22

#endif
