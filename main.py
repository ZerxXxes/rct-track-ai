from segments import segment

def decode_rle(file_path):
    with open(file_path, 'rb') as file:
        file_content = bytearray(file.read())

    decoded = bytearray()
    i = 0

    while i < len(file_content) - 4:  # Omitting the last four bytes (checksum)
        encode_byte = file_content[i] if file_content[i] < 128 else file_content[i] - 256
        i += 1

        if encode_byte >= 0:
            # Positive value (including 0): copy this many bytes
            for _ in range(encode_byte + 1):
                if i < len(file_content):
                    decoded.append(file_content[i])
                    i += 1
        else:
            # Negative value: copy next byte this many times
            repeat_count = 1 - encode_byte
            if i < len(file_content):
                copy_byte = file_content[i]
                i += 1
                decoded.extend([copy_byte] * repeat_count)

    return decoded

def extract_track_data(decoded_data):
    start_offset = 0xA3  # A3 in hexadecimal is 163 in decimal
    track_data = []
    
    i = start_offset
    while i < len(decoded_data) - 1:  # Ensure there's always a byte to read after the current one
        segment_type = decoded_data[i]
        i += 1  # Move to the qualifier byte

        # Check if it's the end of the track data
        if segment_type == 0xFF:
            print("DEBUG: end of track")
            break

        # Check if there's enough data left for the qualifier byte
        if i >= len(decoded_data):
            break

        qualifier = decoded_data[i]
        i += 1  # Move to the next segment

        # For now, we're ignoring the qualifier
        track_data.append(segment_type)

    return bytes(track_data)


def get_track_name_from_byte(byte_value, type_to_track_name):
    byte_str = hex(byte_value)  # Convert to hex string (e.g., 0x02)
    return type_to_track_name.get(byte_str, "Unknown Track Type")

# Invert the dictionary to map from 'Type' to track name
# Assuming 'segment' is your large nested dictionary
type_to_track_name = {v['Type']: k for k, v in segment.items()}

# Example usage
file_path = 'Contortion.td6'
decoded_data = decode_rle(file_path)
track_data = extract_track_data(decoded_data)

track_names = [get_track_name_from_byte(byte, type_to_track_name) for byte in track_data]
print(track_names)

