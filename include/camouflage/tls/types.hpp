/*=============================================================================
Copyright (c) 2026 Stas Skokov

Distributed under the MIT License (https://opensource.org/licenses/MIT)
=============================================================================*/

#pragma once

#include <cstddef>
#include <cstdint>

namespace camouflage::tls {

#define TLS_MAX_SNI_LEN 68
#define TLS_SESSION_ID_SIZE 32
#define TLS_RANDOM_SIZE 32
#define TLS_MAX_PACKET_SIZE 2048

#define TLS_MAX_RECORDS 5
#define TLS_MAX_ENTRIES 64

// TLS record
typedef struct {
  char sni[TLS_MAX_SNI_LEN];
  std::uint8_t session_id[TLS_SESSION_ID_SIZE];
  std::uint8_t random[TLS_RANDOM_SIZE];
  std::uint8_t handshake_packet[TLS_MAX_PACKET_SIZE];
  std::size_t handshake_packet_size;
} HandshakeRecord;

// group records
typedef struct {
  std::size_t sni_length;
  std::size_t record_count;
  HandshakeRecord records[TLS_MAX_RECORDS];
} HandshakeEntry;

// group of handshake groups
typedef struct {
  std::size_t entry_count;
  HandshakeEntry entries[TLS_MAX_ENTRIES];
} HandshakeData;

}  // namespace camouflage::tls
