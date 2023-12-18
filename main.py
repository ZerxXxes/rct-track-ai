from segments import segment
from pprint import pprint

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

def interpolate_positions(start, end):
    positions = []
    step = 1 if end >= start else -1
    for pos in range(start, end + step, step):
        positions.append(pos)
    return positions

def calculate_segment_positions(track_names, segment_dict):
    position = [0, 0, 0]  # [x, y, z]
    direction = 'DIR_STRAIGHT'  # Initial direction
    positions = [tuple(position)]  # Store initial position

    for name in track_names:
        segment_info = segment_dict.get(name, {})
        forward_delta = int(segment_info.get('ForwardDelta', 0))
        sideways_delta = int(segment_info.get('SidewaysDelta', 0))
        elevation_delta = int(segment_info.get('ElevationDelta', 0))

        # Handle forward movement
        if direction in ['DIR_STRAIGHT', 'DIR_90_DEG_LEFT', 'DIR_90_DEG_RIGHT']:
            new_x_positions = interpolate_positions(position[0], position[0] + forward_delta)
            for x in new_x_positions[1:]:  # Skip the first position as it's already included
                positions.append((x, position[1], position[2]))
            position[0] += forward_delta

        # Handle sideways movement
        if direction == 'DIR_90_DEG_LEFT':
            new_y_positions = interpolate_positions(position[1], position[1] + sideways_delta)
            for y in new_y_positions[1:]:
                positions.append((position[0], y, position[2]))
            position[1] += sideways_delta
        elif direction == 'DIR_90_DEG_RIGHT':
            new_y_positions = interpolate_positions(position[1], position[1] - sideways_delta)
            for y in new_y_positions[1:]:
                positions.append((position[0], y, position[2]))
            position[1] -= sideways_delta

        # Handle elevation
        new_z_positions = interpolate_positions(position[2], position[2] + elevation_delta)
        for z in new_z_positions[1:]:
            positions.append((position[0], position[1], z))
        position[2] += elevation_delta

        # Update direction for the next segment
        direction = segment_info.get('DirectionDelta', direction)

    return positions

# Invert the dictionary to map from 'Type' to track name
# Assuming 'segment' is your large nested dictionary
type_to_track_name = {v['Type']: k for k, v in segment.items()}

# Example usage
file_path = 'markustest3.td6'
decoded_data = decode_rle(file_path)
track_data = extract_track_data(decoded_data)

track_names = [get_track_name_from_byte(byte, type_to_track_name) for byte in track_data]
positions = calculate_segment_positions(track_names, segment)
pprint(track_names)
pprint(positions)
