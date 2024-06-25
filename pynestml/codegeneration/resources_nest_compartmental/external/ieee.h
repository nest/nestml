/*
MIT License

Copyright (c) 2018 simonpf

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/

#ifndef FASTEXP_IEEE_H
#define FASTEXP_IEEE_H

namespace fastexp
{
    template<typename Real, size_t degree, size_t i = 0> struct PolynomialFit;
    template<typename Real> struct Info;

    template<typename Real, size_t degree>

    struct IEEE {
        static uint64_t FloatToBinaryIntegerRepresentation(double f){
            // Step 1: Extract the raw binary representation of the float
            // This step is highly dependent on the system architecture and usually involves bit-level operations.
            constexpr uint64_t uint64max = std::numeric_limits<uint64_t>::max();

            uint64_t raw_bits;
            std::memcpy(&raw_bits, &f, sizeof(f));

            // Step 2: Extract the sign, exponent, and significand
            uint64_t sign = (raw_bits >> 63) & 0x1;
            uint64_t exponent = (raw_bits >> 52) & 0x7FF;   // 11 bits for exponent
            uint64_t significand = raw_bits & 0xFFFFFFFFFFFFF;    // 52 bits for significand

            // Step 3: Calculate the actual exponent by subtracting the bias
            uint64_t bias = 1023;                           // Bias for 64-bit float
            uint64_t actual_exponent = exponent - bias;

            // Step 4: Normalize the significand (implicit leading 1 for normalized numbers)
            significand = significand | 0x10000000000000;         // Add the implicit 1 (23rd bit)

            uint64_t integer_part;

            // Step 5: Calculate the integer part of the float
            if(actual_exponent > 52){
                // Shift significand left if the exponent is larger than the number of significand bits
                integer_part = significand << (actual_exponent - 52);
            }
            else{
                // Shift significand right if the exponent is smaller or equal to the number of significand bits
                integer_part = significand >> (52 - actual_exponent);
            }
            if(sign){
                integer_part = uint64max - integer_part + 1;
            }

            return integer_part;
        }

        static Real evaluate(Real x) {
            using unsigned_t = typename Info<Real>::unsigned_t;
            constexpr unsigned_t shift = static_cast<unsigned_t>(1) << Info<Real>::shift;

            x *= Info<Real>::log2e;
            Real xi = floor(x);
            Real xf = x - xi;

            Real k = PolynomialFit<Real, degree, 0>::evaluate(xf) + 1.0;
            unsigned_t e = reinterpret_cast<const unsigned_t &>(k);
            unsigned_t ut = FloatToBinaryIntegerRepresentation(xi);//static_cast<unsigned_t>(xi);

            unsigned_t sut = shift * ut;
            unsigned_t eTmp = sut+e;
            return reinterpret_cast<Real &>(eTmp);
        }
    };


    ////////////////////////////////////////////////////////////////////////////////
    // Polynomial coefficients for error function fit.
    ////////////////////////////////////////////////////////////////////////////////


    template<> struct Info<float> {
        using unsigned_t = uint32_t;
        static constexpr uint32_t shift = 23;
        static constexpr float  log2e = 1.442695040;
    };

    template<> struct Info<double> {
        using unsigned_t = uint64_t;
        static constexpr uint64_t shift = 52;
        static constexpr double log2e = 1.442695040;
    };

    template<typename Real, size_t degree>
        struct Data;

    template<typename Real>
    struct Data<Real, 1> {
        static constexpr Real coefficients[2] = {-0.05288671,
                                                 0.99232129};
    };
    template<typename Real> constexpr Real Data<Real, 1>::coefficients[2];

    template<typename Real>
    struct Data<Real, 2> {
        static constexpr Real coefficients[3] = {0.00365539,
                                                 0.64960693,
                                                 0.34271434};
    };
    template<typename Real> constexpr Real Data<Real, 2>::coefficients[3];

    template<typename Real>
    struct Data<Real, 3> {
        static constexpr Real coefficients[4] = {-1.77187919e-04,
                                                6.96787180e-01,
                                                2.24169036e-01,
                                                7.90302044e-02};
    };
    template<typename Real> constexpr Real Data<Real, 3>::coefficients[4];

    template<typename Real>
    struct Data<Real, 4> {
        static constexpr Real coefficients[5] = { 6.58721338e-06,
                                                  6.92937406e-01,
                                                  2.41696769e-01,
                                                  5.16742848e-02,
                                                  1.36779598e-02};
    };
    template<typename Real> constexpr Real Data<Real, 4>::coefficients[5];

    template<typename Real>
        struct Data<Real, 5> {
        static constexpr Real coefficients[6] = {6.58721338e-06,
                                                 6.92937406e-01,
                                                 2.41696769e-01,
                                                 5.16742848e-02,
                                                 1.36779598e-02};
    };
    template<typename Real> constexpr Real Data<Real, 5>::coefficients[6];

    template<typename Real>
        struct Data<Real, 6> {
        static constexpr Real coefficients[7] = {-1.97880719e-07,
                                                 6.93156327e-01,
                                                 2.40133447e-01,
                                                 5.58740717e-02,
                                                 8.94160147e-03,
                                                 1.89454334e-03};
    };
    template<typename Real> constexpr Real Data<Real, 6>::coefficients[7];

    template<typename Real>
        struct Data<Real, 7> {
        static constexpr Real coefficients[8] = {4.97074799e-09,
                                                 6.93146861e-01,
                                                 2.40230956e-01,
                                                 5.54792541e-02,
                                                 9.68583180e-03,
                                                 1.23835751e-03,
                                                 2.18728611e-04};
    };
    template<typename Real> constexpr Real Data<Real, 7>::coefficients[8];

    template<typename Real>
        struct Data<Real, 8> {
        static constexpr Real coefficients[9] = {-1.06974751e-10,
                                                    6.93147190e-01,
                                                    2.40226337e-01,
                                                    5.55053726e-02,
                                                    9.61338873e-03,
                                                    1.34310382e-03,
                                                    1.42959529e-04,
                                                    2.16483090e-05};
    };
    template<typename Real> constexpr Real Data<Real, 8>::coefficients[9];

    template<typename Real>
        struct Data<Real, 9> {
        static constexpr Real coefficients[10] = {2.00811867e-12,
                                                    6.93147180e-01,
                                                    2.40226512e-01,
                                                    5.55040573e-02,
                                                    9.61838113e-03,
                                                    1.33265219e-03,
                                                    1.55193275e-04,
                                                    1.41484217e-05,
                                                    1.87497191e-06};
    };
    template<typename Real> Real constexpr Data<Real, 9>::coefficients[10];

    template<typename Real, size_t degree, size_t i>
        struct PolynomialFit {
            inline static Real evaluate(Real x) {
                Real p = PolynomialFit<Real, degree, i + 1>::evaluate(x) * x;
                p += Data<Real, degree>::coefficients[i];
                return p;
            }
        };

    template<typename Real, size_t degree>
        struct PolynomialFit<Real, degree, degree> {
        inline static Real evaluate(Real x) {
            return Data<Real, degree>::coefficients[degree];
        }
    };

    template<typename Real>
        struct PolynomialFit<Real, 0, 0> {
        inline static Real evaluate(Real x) {
            return x;
        }
    };

}      // fastexp
#endif // FASTEXP_IEEE_H
