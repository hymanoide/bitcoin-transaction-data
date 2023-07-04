"""
Each transaction has the following structure:

- Version (4 bytes)
- Input Count (Variable)
- Inputs:
    - Transaction ID (32 bytes)
    - VOUT (4 bytes)
    - ScriptSig Size (Variable)
    - ScriptSig
    - Sequence (4 bytes)
- Output Count (Variable)
- Outputs:
    - Value (8 bytes)
    - ScriptPubKey Size (Variable)
    - ScriptPubKey
- Locktime (4 bytes)

*Tasks* 1) Serialization Function: Write a function named serialize_transaction that takes a transaction object and
serializes it into a hexadecimal string. The transaction object can be represented using your preferred data
structure (e.g., a dictionary).

2) Deserialization Function: Write a function named deserialize_transaction that takes a hexadecimal string (
serialized transaction) as an argument and returns a transaction object. Additionally, during the deserialization
process, you must calculate the Transaction ID by computing the SHA-256 hash of the entire serialized transaction
data and add it as an additional field in the returned transaction object. The Transaction ID is the SHA-256 hash of
the serialized transaction data.

Serialized txn example:
01000000017967a5185e907a25225574544c31f7b059c1a191d65b53dcc1554d339c4f9efc010000006a47304402206a2eb16b7b92051d0fa38c133e67684ed064effada1d7f925c842da401d4f22702201f196b10e6e4b4a9fff948e5c5d71ec5da53e90529c8dbd122bff2b1d21dc8a90121039b7bcd0824b9a9164f7ba098408e63e5b7e3cf90835cceb19868f54f8961a825ffffffff014baf2100000000001976a914db4d1141d0048b1ed15839d0b7a4c488cd368b0e88ac00000000

More info:
- https://learnmeabitcoin.com/technical/transaction-data
- https://learnmeabitcoin.com/technical/varint
"""


# We could refactor this code as a class with following functions as methods inside.

def serialize_transaction(deserialized_string):
    serialized = int_to_hex(deserialized_string['version'], 8)
    serialized += format(deserialized_string['inputs_count'], '02x')

    for input_data in deserialized_string['inputs']:
        serialized += input_data['TXID']
        serialized += input_data['VOUT']
        serialized += int_to_hex(input_data['ScriptSig_Size'] // 2, 2)  # Divide by 2 needed.
        serialized += input_data['ScriptSig']
        serialized += input_data['Sequence']

    serialized += int_to_hex(deserialized_string['output_count'], 2)

    for output_data in deserialized_string['outputs']:
        serialized += output_data['Value']
        serialized += int_to_hex(output_data['ScriptPubKey_Size'], 2)  # TODO: Why here we don't need to divide by 2 ?
        serialized += output_data['ScriptPubKey']

    serialized += deserialized_string['locktime']

    return serialized


def deserialize_transaction(serialized_string):
    diccionario = {}

    size = 0
    diccionario['version'] = hex_to_int(serialized_string[size: size + 8])  # 4 bytes
    size += 8
    diccionario['inputs_count'] = hex_to_int(serialized_string[size: size + 2])  # 1 byte
    size += 2
    diccionario['inputs'] = []
    # Size 10
    for i in range(diccionario['inputs_count']):
        script_size = hex_to_int(serialized_string[size + 72: size + 74]) * 2  # 1 byte
        inputs = {
            'TXID': serialized_string[size: size + 64],  # 32 bytes
            'VOUT': serialized_string[size + 64: size + 72],  # 4 bytes
            'ScriptSig_Size': script_size,  # 1 byte
            'ScriptSig': serialized_string[size + 74:size + 74 + script_size],  # bytes from size variable
            'Sequence': serialized_string[size + 74 + script_size:size + 74 + script_size + 8],
            # 4 bytes with size from previous unlocking code
        }
        diccionario['inputs'].append(inputs)
        size += 74 + script_size + 8

    diccionario['output_count'] = hex_to_int(serialized_string[size: size + 2])

    diccionario['outputs'] = []

    for i in range(diccionario['output_count']):
        script_size = hex_to_int(serialized_string[size + 18:size + 20]) * 2  # 1 byte
        outputs = {
            'Value': serialized_string[size + 2:size + 2 + 16],
            'ScriptPubKey_Size': hex_to_int(serialized_string[size + 18:size + 20]),
            'ScriptPubKey': serialized_string[size + 20:size + 20 + script_size]
        }
        diccionario['outputs'].append(outputs)
        size += 20 + script_size

    diccionario['locktime'] = (serialized_string[size:size + 8])

    return diccionario


"""
 Helper functions: Convert Hex to Int
"""


def hex_to_int(hex_string: str) -> int:
    # Convert the hex string to bytes
    bytes_representation = bytes.fromhex(hex_string)

    # Convert the bytes to an integer in little endian format
    return int.from_bytes(bytes_representation, byteorder='little')


def int_to_hex(integer, field_length) -> str:
    # Convert the integer to bytes in little endian format
    bytes_representation = integer.to_bytes((integer.bit_length() + 7) // 8, byteorder='little')

    # Convert the bytes to a hexadecimal string with the specified field length
    hex_representation = bytes_representation.hex().ljust(field_length, '0')

    return hex_representation


if __name__ == '__main__':
    string_original = '01000000017967a5185e907a25225574544c31f7b059c1a191d65b53dcc1554d339c4f9efc010000006a47304402206a2eb16b7b92051d0fa38c133e67684ed064effada1d7f925c842da401d4f22702201f196b10e6e4b4a9fff948e5c5d71ec5da53e90529c8dbd122bff2b1d21dc8a90121039b7bcd0824b9a9164f7ba098408e63e5b7e3cf90835cceb19868f54f8961a825ffffffff014baf2100000000001976a914db4d1141d0048b1ed15839d0b7a4c488cd368b0e88ac00000000'

    deserialized = deserialize_transaction(string_original)
    serialized = serialize_transaction(deserialized)

    print("Deserialized: \n", deserialized)
    print("Original: \n", string_original)
    print("Serialized: \n", serialized)
    print("Matches?: \n", string_original == serialized)
