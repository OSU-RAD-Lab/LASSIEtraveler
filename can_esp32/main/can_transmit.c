#include "driver/gpio.h"
#include "driver/can.h"
#include <stdio.h>
#include <fcntl.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_err.h"
#include "esp_log.h"
#include "driver/twai.h"
#include <sys/unistd.h>
#include "esp_twai.h"
#include "esp_twai_onchip.h"

/// CODE FROM ESP TWAI GUIDE

twai_node_handle_t node_hdl = NULL;
twai_onchip_node_config_t node_config = {
    .io_cfg.tx = 4,             // TWAI TX GPIO pin
    .io_cfg.rx = 5,             // TWAI RX GPIO pin
    .bit_timing.bitrate = 200000,  // 200 kbps bitrate
    .tx_queue_depth = 5,        // Transmit queue depth set to 5
};
// Create a new TWAI controller driver instance
ESP_ERROR_CHECK(twai_new_node_onchip(&node_config, &node_hdl));
// Start the TWAI controller
ESP_ERROR_CHECK(twai_node_enable(node_hdl));

uint8_t send_buff[8] = {0};
twai_frame_t tx_msg = {
    .header.id = 0x104,       // Message ID
    .dlc = 8,           
    .header.ide = true,         // Use 29-bit extended ID format
    .buffer = send_buff,        // Pointer to data to transmit
    .buffer_len = sizeof(send_buff),  // Length of data to transmit
};
ESP_ERROR_CHECK(twai_node_transmit(node_hdl, &tx_msg, 0));  // Timeout = 0: returns immediately if queue is full
ESP_ERROR_CHECK(twai_node_transmit_wait_all_done(node_hdl, -1));  // Wait for transmission to finish

///// EXAMPLE CODE FROM EVAN /////////

// #define TWAI_TX_GPIO  ((gpio_num_t)CONFIG_CAN_TX_GPIO_NUM)
// #define TWAI_RX_GPIO  ((gpio_num_t)CONFIG_CAN_RX_GPIO_NUM)
// #define MSG_ID       0x104
// #define EXAMPLE_TAG  "TWAI SENDER"

//  // TWAI timing configuration (125 Kbps)
//  static const twai_timing_config_t t_config = TWAI_TIMING_CONFIG_125KBITS();

//  // Filter configuration to accept only messages with MSG_ID
//  static const twai_filter_config_t f_config = {
//      .acceptance_code = (MSG_ID << 21),
//      .acceptance_mask = ~(TWAI_STD_ID_MASK << 21),
//      .single_filter = true
//  };

//  // Use NORMAL mode for communication (not NO_ACK/self-test)
//  static const twai_general_config_t g_config =
//      TWAI_GENERAL_CONFIG_DEFAULT(TWAI_TX_GPIO, TWAI_RX_GPIO, TWAI_MODE_NORMAL);

// void setup() {

// }

// void loop() {
// // try to parse packet
//   int packetSize = CAN.parsePacket();

//   if (packetSize) {
//     // received a packet
//     Serial.print ("Received ");

//     if (CAN.packetExtended()) {
//       Serial.print ("extended ");
//     }

//     if (CAN.packetRtr()) {
//       // Remote transmission request, packet contains no data
//       Serial.print ("RTR ");
//     }

//     Serial.print ("packet with id 0x");
//     Serial.print (CAN.packetId(), HEX);

//     if (CAN.packetRtr()) {
//       Serial.print (" and requested length ");
//       Serial.println (CAN.packetDlc());
//     } else {
//       Serial.print (" and length ");
//       Serial.println (packetSize);

//       // only print packet data for non-RTR packets
//       while (CAN.available()) {
//         Serial.print ((char) CAN.read());
//       }
//       Serial.println();
//     }

//     Serial.println();
//   }
// }

// void app_main(void)
//  {
//      // Install and start the TWAI driver
//      ESP_ERROR_CHECK(twai_driver_install(&g_config, &t_config, &f_config));
//      ESP_ERROR_CHECK(twai_start());
//      ESP_LOGI(EXAMPLE_TAG, "TWAI driver started");

//      // Set STDIN to non-blocking mode so that getchar() does not block forever.
//      int flags = fcntl(STDIN_FILENO, F_GETFL, 0);
//      fcntl(STDIN_FILENO, F_SETFL, flags | O_NONBLOCK);

//      ESP_LOGI(EXAMPLE_TAG, "Enter 0 or 8:");

//      while (1) {
//          int c = getchar();
//          if (c != EOF) {
//              // Ignore newline or carriage return characters
//              if (c == '\n' || c == '\r') {
//                  // Do nothing
//              } else if (c == '0' || c == '8') {
//                  uint8_t data_value = (c == '8') ? 8 : 0;
//                  twai_message_t tx_msg = {
//                      .extd = 0,                // Standard 11-bit identifier
//                      .rtr = 0,                 // Data frame (not a remote frame)
//                      .ss = 0,                  // Not single shot
//                      .self = 0,                // Normal transmission (not self reception)
//                      .identifier = MSG_ID,
//                      .data_length_code = 8,    // Eight data bytes
//                      .data = { data_value }
//                  };

//                  // Transmit the message (wait up to 1000 ms)
//                  ESP_ERROR_CHECK(twai_transmit(&tx_msg, pdMS_TO_TICKS(1000)));
//                  ESP_LOGI(EXAMPLE_TAG, "Message transmitted: %c", c);
//              } else {
//                  ESP_LOGW(EXAMPLE_TAG, "Invalid input. Please enter 0 or 8.");
//              }
//          }
//          // Delay to yield to other tasks and prevent watchdog timeout.
//          vTaskDelay(pdMS_TO_TICKS(100));
//      }

//      // (Unreachable cleanup code)
//      // ESP_ERROR_CHECK(twai_stop());
//      // ESP_ERROR_CHECK(twai_driver_uninstall());

//      esp_err_t motor_feedback_parse(const uint8_t *data, motor_feedback_t *out)
// {
//     if (data == NULL || out == NULL) {
//         return ESP_ERR_INVALID_ARG;
//     }

//     out->position_raw = ((uint16_t)data[0] << 8) | data[1];
//     out->speed_raw = ((uint16_t)data[2] << 8) | data[3];
//     out->current_raw = ((uint16_t)data[4] << 8) | data[5];
//     out->temperature_c = data[6];
//     out->error_code = data[7];

//     out->position_rad = uint_to_float(out->position_raw, POSITION_MIN, POSITION_MAX, 16);
//     out->speed_rad_s = uint_to_float(out->speed_raw, SPEED_MIN, SPEED_MAX, 16);
//     out->current_a = uint_to_float(out->current_raw, CURRENT_MIN, CURRENT_MAX, 16);

//     return ESP_OK;
// }
//  }


///// CODE FOUND ON A WEBSITE

// void app_main()
// {
//     //Initialize configuration structures using macro initializers
//     can_general_config_t g_config = CAN_GENERAL_CONFIG_DEFAULT(U0_TXD, U0_RXD, CAN_MODE_NORMAL);
//     can_timing_config_t t_config = CAN_TIMING_CONFIG_500KBITS();
//     can_filter_config_t f_config = CAN_FILTER_CONFIG_ACCEPT_ALL();

//     //Install CAN driver
//     if (can_driver_install(&g_config, &t_config, &f_config) == ESP_OK) {
//         printf("Driver installed\n");
//     } else {
//         printf("Failed to install driver\n");
//         return;
//     }

//     //Start CAN driver
//     if (can_start() == ESP_OK) {
//         printf("Driver started\n");
//     } else {
//         printf("Failed to start driver\n");
//         return;
//     }

//     //Configure message to transmit
//     can_message_t message;
//     message.identifier = 0xAAAA;
//     message.flags = CAN_MSG_FLAG_EXTD;
//     message.data_length_code = 4;
//     for (int i = 0; i < 4; i++) {
//     message.data[i] = 0;
//     }

//     //Queue message for transmission
//     if (can_transmit(&message, pdMS_TO_TICKS(1000)) == ESP_OK) {
//         printf("Message queued for transmission\n");
//     }   
//     else {
//     printf("Failed to queue message for transmission\n");
//     }

//     //Wait for message to be received
//     can_message_t message;
//     if (can_receive(&message, pdMS_TO_TICKS(10000)) == ESP_OK) {
//         printf("Message received\n");
//     } 
//     else {
//         printf("Failed to receive message\n");
//         return;
//     }
//     }

//     //Process received message
//     if (message.flags & CAN_MSG_FLAG_EXTD) {
//         printf("Message is in Extended Format\n");
//     } 
//     else {
//         printf("Message is in Standard Format\n");
//     }
//     printf("ID is %d\n", message.identifier);

//     if (!(message.flags & CAN_MSG_FLAG_RTR)) {
//         for (int i = 0; i < message.data_length_code; i++) {
//             printf("Data byte %d = %d\n", i, message.data[i]);
//         }
//     }

//     //Stop the CAN driver
//     if (can_stop() == ESP_OK) {
//         printf("Driver stopped\n");
//     } 
//     else {
//         printf("Failed to stop driver\n");
//         return;
//     }
// }