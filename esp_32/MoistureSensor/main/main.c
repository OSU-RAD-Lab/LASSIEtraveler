#include <stdio.h>
#include "driver/adc.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

void app_main(void)
{
    // Configure ADC1
    adc1_config_width(ADC_WIDTH_BIT_12);                 // 0–4095
    adc1_config_channel_atten(ADC1_CHANNEL_0, ADC_ATTEN_DB_11); // ~0–3.3V

    while (1) {
        int adc_raw = adc1_get_raw(ADC1_CHANNEL_0);

        printf("ADC: %d", adc_raw);

        vTaskDelay(pdMS_TO_TICKS(25));
    }
}
