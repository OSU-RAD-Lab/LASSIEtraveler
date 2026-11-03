#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/adc.h"
#include "esp_system.h"

// ------------------------------------------------------------
// YOUR CALIBRATION TABLE
// Replace these with your actual ADC readings for each moisture level.
// ------------------------------------------------------------
// static const float moisture_percent[] = {0, 2.5, 5, 10, 15, 20, 30, 100};
//static const int   adc_values[]       = {3100, 3000, 2900, 2700, 2500, 2300, 2000, 1200};
//static const int   NUM_POINTS = sizeof(moisture_percent) / sizeof(moisture_percent[0]);

// ------------------------------------------------------------
// Linear interpolation function
// ------------------------------------------------------------
/*float interpolate_moisture(int adc_raw)
{
    // If below lowest calibration point
    if (adc_raw <= adc_values[NUM_POINTS - 1]) {
        return moisture_percent[NUM_POINTS - 1];
    }

    // If above highest calibration point
    if (adc_raw >= adc_values[0]) {
        return moisture_percent[0];
    }

    // Find bracketing points
    for (int i = 0; i < NUM_POINTS - 1; i++) {
        int adc_high = adc_values[i];
        int adc_low  = adc_values[i + 1];

        if (adc_raw <= adc_high && adc_raw >= adc_low) {
            float m_high = moisture_percent[i];
            float m_low  = moisture_percent[i + 1];

            // Linear interpolation:
            // moisture = m_low + (adc_raw - adc_low)*(m_high - m_low)/(adc_high - adc_low)
            float moisture = m_low +
                ( (float)(adc_raw - adc_low) * (m_high - m_low) ) /
                (float)(adc_high - adc_low);

            return moisture;
        }
    }

    return 0; // fallback
}*/

void app_main(void)
{
    // Configure ADC1
    adc1_config_width(ADC_WIDTH_BIT_12);                 // 0–4095
    adc1_config_channel_atten(ADC1_CHANNEL_0, ADC_ATTEN_DB_11); // ~0–3.3V

    while (1) {
        int adc_raw = adc1_get_raw(ADC1_CHANNEL_0);

        //float moisture = interpolate_moisture(adc_raw);

        //printf("ADC: %d   Moisture: %.2f%%\n", adc_raw, moisture);
        printf("ADC: %d, adc_raw,);

        vTaskDelay(pdMS_TO_TICKS(25));
    }
}