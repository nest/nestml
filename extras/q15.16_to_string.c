#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

/**
 * @brief Converts a 32-bit Q15.16 fixed-point number to a decimal string.
 *
 * This function extracts the sign, integer, and fractional parts of the Q15.16
 * number without using floating-point arithmetic. It then constructs a string
 * representation.
 *
 * @param q_num The 32-bit Q15.16 fixed-point number.
 * @param buffer A character buffer to store the resulting string.
 * @param buffer_size The size of the buffer.
 */
void q15_16_to_string(int32_t q_num, char *buffer, size_t buffer_size) {
    if (buffer == NULL || buffer_size == 0) {
        return;
    }

    // Determine the sign and work with the absolute value for calculations.
    // The sign bit is the MSB (bit 31)
    int is_negative = (q_num < 0);
    if (is_negative) {
        q_num = -q_num;
    }

    // Extract the integer part by right-shifting by 16 bits.
    // The integer part occupies bits 16 to 30 (15 bits)
    int32_t integer_part = q_num >> 16;

    // Extract the fractional part by masking the lower 16 bits.
    // The fractional part occupies bits 0 to 15 (16 bits)
    int32_t fractional_part = q_num & 0xFFFF;

    // To convert the fractional part to a decimal string without floats, we
    // treat it as a fraction of 2^16 (65536).
    // For example, if the fractional part is 32768, the value is 32768/65536 = 0.5.
    // To get a decimal string with, say, 5 digits, we multiply by 10^5 and
    // then divide by 65536, using a 64-bit integer to avoid overflow.
    // The fractional part will be (fractional_part * 100000) / 65536.
    int64_t decimal_fraction = ((int64_t)fractional_part * 100000 + 32768) >> 16;
    // We add 32768 (0.5 * 65536) for rounding before the bit shift, which is
    // equivalent to division. This is a common fixed-point rounding technique.

    // Start printing the string.
    char *ptr = buffer;
    if (is_negative) {
        *ptr++ = '-';
    }

    // Print the integer part.
    ptr += snprintf(ptr, buffer_size - (ptr - buffer), "%d.", integer_part);

    // Print the fractional part with leading zeros to maintain precision.
    snprintf(ptr, buffer_size - (ptr - buffer), "%05lld", (long long)decimal_fraction);
}

/**
 * @brief Main function to demonstrate the conversion.
 */
int main() {
    // Test cases for various Q15.16 numbers
    // 1. A positive number: 10.5
    //    10 << 16 = 655360
    //    0.5 * 2^16 = 0.5 * 65536 = 32768 = 0x8000
    //    10.5 = (10 << 16) + 32768 = 688128 = 0xA8000
    int32_t q_positive = 688128;

    // 2. A negative number: -2.75
    //    2 << 16 = 131072
    //    0.75 * 2^16 = 0.75 * 65536 = 49152 = 0xC000
    //    -2.75 = - (131072 + 49152) = -180224 = -0x2C000
    int32_t q_negative = -180224;

    // 3. A small number: 0.001
    //    0.001 * 2^16 = 0.001 * 65536 = 65.536 -> round to 66
    int32_t q_small = 66;

    // 4. A large number: 30000.12345
    //    30000 << 16 = 1966080000
    //    0.12345 * 2^16 = 8090.88 -> round to 8091 = 0x1F9B
    //    1966080000 + 8091 = 1966088091 = 0x75231F9B
    int32_t q_large = 1966088091;

    // Buffer to hold the resulting strings
    char result_buffer[50];

    // Convert and print each number
    q15_16_to_string(q_positive, result_buffer, sizeof(result_buffer));
    printf("Q15.16 value 0x%X -> %s\n", q_positive, result_buffer);

    q15_16_to_string(q_negative, result_buffer, sizeof(result_buffer));
    printf("Q15.16 value 0x%X -> %s\n", q_negative, result_buffer);

    q15_16_to_string(q_small, result_buffer, sizeof(result_buffer));
    printf("Q15.16 value 0x%X -> %s\n", q_small, result_buffer);

    q15_16_to_string(q_large, result_buffer, sizeof(result_buffer));
    printf("Q15.16 value 0x%X -> %s\n", q_large, result_buffer);

    return 0;
}
