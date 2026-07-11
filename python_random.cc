#include "python_random.h"

#include <cstdint>

namespace transplot {

void PythonRandom::InitGenrand(uint32_t s) {
  mt_[0] = s;
  for (mti_ = 1; mti_ < kN; mti_++) {
    mt_[mti_] =
        (1812433253UL * (mt_[mti_ - 1] ^ (mt_[mti_ - 1] >> 30)) + mti_);
  }
}

void PythonRandom::InitByArray(const uint32_t* init_key, int key_length) {
  InitGenrand(19650218UL);
  int i = 1;
  int j = 0;
  int k = (kN > key_length ? kN : key_length);
  for (; k; k--) {
    mt_[i] = (mt_[i] ^ ((mt_[i - 1] ^ (mt_[i - 1] >> 30)) * 1664525UL)) +
             init_key[j] + j;
    i++;
    j++;
    if (i >= kN) {
      mt_[0] = mt_[kN - 1];
      i = 1;
    }
    if (j >= key_length) j = 0;
  }
  for (k = kN - 1; k; k--) {
    mt_[i] = (mt_[i] ^ ((mt_[i - 1] ^ (mt_[i - 1] >> 30)) * 1566083941UL)) - i;
    i++;
    if (i >= kN) {
      mt_[0] = mt_[kN - 1];
      i = 1;
    }
  }
  mt_[0] = 0x80000000UL;  // MSB is 1, assuring a non-zero initial array.
}

void PythonRandom::Seed(uint64_t n) {
  // CPython builds the key array from the 32-bit little-endian words of abs(n).
  // A zero seed yields a single-element key {0} (keyused == 1).
  uint32_t key[2];
  int key_length = 0;
  if (n == 0) {
    key[0] = 0;
    key_length = 1;
  } else {
    while (n > 0 && key_length < 2) {
      key[key_length++] = static_cast<uint32_t>(n & 0xffffffffUL);
      n >>= 32;
    }
  }
  InitByArray(key, key_length);
}

uint32_t PythonRandom::NextUint32() {
  static const uint32_t mag01[2] = {0x0UL, kMatrixA};
  uint32_t y;

  if (mti_ >= kN) {  // Generate kN words at a time.
    int kk;
    if (mti_ == kN + 1) InitGenrand(5489UL);  // Never reached (always seeded).

    for (kk = 0; kk < kN - kM; kk++) {
      y = (mt_[kk] & kUpperMask) | (mt_[kk + 1] & kLowerMask);
      mt_[kk] = mt_[kk + kM] ^ (y >> 1) ^ mag01[y & 0x1UL];
    }
    for (; kk < kN - 1; kk++) {
      y = (mt_[kk] & kUpperMask) | (mt_[kk + 1] & kLowerMask);
      mt_[kk] = mt_[kk + (kM - kN)] ^ (y >> 1) ^ mag01[y & 0x1UL];
    }
    y = (mt_[kN - 1] & kUpperMask) | (mt_[0] & kLowerMask);
    mt_[kN - 1] = mt_[kM - 1] ^ (y >> 1) ^ mag01[y & 0x1UL];

    mti_ = 0;
  }

  y = mt_[mti_++];
  y ^= (y >> 11);
  y ^= (y << 7) & 0x9d2c5680UL;
  y ^= (y << 15) & 0xefc60000UL;
  y ^= (y >> 18);
  return y;
}

uint32_t PythonRandom::GetRandBits(int k) {
  // For 1 <= k <= 32, CPython returns the top k bits of one MT word.
  return NextUint32() >> (32 - k);
}

uint32_t PythonRandom::RandBelow(uint32_t n) {
  if (n == 0) return 0;
  // k = n.bit_length()
  int k = 0;
  for (uint32_t v = n; v; v >>= 1) k++;
  uint32_t r = GetRandBits(k);
  while (r >= n) r = GetRandBits(k);
  return r;
}

int PythonRandom::RandInt(int a, int b) {
  return a + static_cast<int>(RandBelow(static_cast<uint32_t>(b - a + 1)));
}

}  // namespace transplot
