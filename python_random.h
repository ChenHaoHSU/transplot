// A faithful reimplementation of CPython's `random` module (the Mersenne
// Twister core plus `random.seed(int)`, `getrandbits`, and the
// `_randbelow_with_getrandbits` used by `random.randint`).
//
// This exists so the C++ port produces byte-identical colors to base_plot.py,
// which seeds `random.seed(0)` and draws `random.randint(0, 255)` for the extra
// SDC-group colors. It matches CPython 3.11's algorithm exactly.

#ifndef TRANSPLOT_PYTHON_RANDOM_H_
#define TRANSPLOT_PYTHON_RANDOM_H_

#include <cstdint>

namespace transplot {

class PythonRandom {
 public:
  PythonRandom() { Seed(0); }

  // Equivalent to `random.seed(n)` for a non-negative integer `n`. Only the
  // seed values transplot uses (currently 0) are needed; the key array is built
  // from the 32-bit words of `n` exactly as CPython's random_seed does.
  void Seed(uint64_t n);

  // Equivalent to CPython's genrand_uint32(): a full 32-bit MT output word.
  uint32_t NextUint32();

  // Equivalent to `random.getrandbits(k)` for 1 <= k <= 32.
  uint32_t GetRandBits(int k);

  // Equivalent to `random._randbelow_with_getrandbits(n)` for n > 0.
  uint32_t RandBelow(uint32_t n);

  // Equivalent to `random.randint(a, b)` (inclusive on both ends).
  int RandInt(int a, int b);

 private:
  static constexpr int kN = 624;
  static constexpr int kM = 397;
  static constexpr uint32_t kMatrixA = 0x9908b0dfUL;
  static constexpr uint32_t kUpperMask = 0x80000000UL;
  static constexpr uint32_t kLowerMask = 0x7fffffffUL;

  void InitGenrand(uint32_t s);
  void InitByArray(const uint32_t* init_key, int key_length);

  uint32_t mt_[kN];
  int mti_ = kN + 1;
};

}  // namespace transplot

#endif  // TRANSPLOT_PYTHON_RANDOM_H_
