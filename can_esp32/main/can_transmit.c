#include "driver/gpio.h"
#include "driver/can.h"

void app_main()
{
    //Initialize configuration structures using macro initializers
    can_general_config_t g_config = CAN_GENERAL_CONFIG_DEFAULT(U0_TXD, U0_RXD, CAN_MODE_NORMAL);
    can_timing_config_t t_config = CAN_TIMING_CONFIG_500KBITS();
    can_filter_config_t f_config = CAN_FILTER_CONFIG_ACCEPT_ALL();

    //Install CAN driver
    if (can_driver_install(&g_config, &t_config, &f_config) == ESP_OK) {
        printf("Driver installed\n");
    } else {
        printf("Failed to install driver\n");
        return;
    }

    //Start CAN driver
    if (can_start() == ESP_OK) {
        printf("Driver started\n");
    } else {
        printf("Failed to start driver\n");
        return;
    }

    //Configure message to transmit
    can_message_t message;
    message.identifier = 0xAAAA;
    message.flags = CAN_MSG_FLAG_EXTD;
    message.data_length_code = 4;
    for (int i = 0; i < 4; i++) {
    message.data[i] = 0;
    }

    //Queue message for transmission
    if (can_transmit(&message, pdMS_TO_TICKS(1000)) == ESP_OK) {
        printf("Message queued for transmission\n");
    }   
    else {
    printf("Failed to queue message for transmission\n");
    }

    //Wait for message to be received
    can_message_t message;
    if (can_receive(&message, pdMS_TO_TICKS(10000)) == ESP_OK) {
        printf("Message received\n");
    } 
    else {
        printf("Failed to receive message\n");
        return;
    }
    }

    //Process received message
    if (message.flags & CAN_MSG_FLAG_EXTD) {
        printf("Message is in Extended Format\n");
    } 
    else {
        printf("Message is in Standard Format\n");
    }
    printf("ID is %d\n", message.identifier);

    if (!(message.flags & CAN_MSG_FLAG_RTR)) {
        for (int i = 0; i < message.data_length_code; i++) {
            printf("Data byte %d = %d\n", i, message.data[i]);
        }
    }

    //Stop the CAN driver
    if (can_stop() == ESP_OK) {
        printf("Driver stopped\n");
    } 
    else {
        printf("Failed to stop driver\n");
        return;
    }
}