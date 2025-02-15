import socket

#                                1  1  1  1  1  1
#  0  1  2  3  4  5  6  7  8  9  0  1  2  3  4  5
# +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
# |                      ID                       |
# +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
# |QR|   Opcode  |AA|TC|RD|RA| Z|AD|CD|   RCODE   |
# +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
# |                QDCOUNT/ZOCOUNT                |
# +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
# |                ANCOUNT/PRCOUNT                |
# +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
# |                NSCOUNT/UPCOUNT                |
# +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
# |                    ARCOUNT                    |


def build_question(question):
    question_bytes = b""
    for parts in question:
        length = len(parts)
        question_bytes += bytes([length])

        for char in parts:
            question_bytes += ord(char).to_bytes(1, byteorder="big")
    question_bytes += (16).to_bytes(2, byteorder="big")  # Adding TXT Record type
    question_bytes += (1).to_bytes(2, byteorder="big")  # Adding Class IN
    return question_bytes


def rec_to_bytes():
    rec_bytes = b"\xc0\x0c\x00\x10\x00\x01"
    rec_bytes += int("300").to_bytes(4, byteorder="big")  # TTL
    rec_bytes += bytes([0]) + bytes([4])  # RDLENGTH'

    answer = "234.123.10.1"  # Replace it with ChatGPT response
    for part in answer.split("."):
        rec_bytes += bytes([int(part)])
    print(rec_bytes)

    return rec_bytes


def generate_flags(data):
    byte_1 = bytes(data[:1])
    QR = "1"

    OPCODE = ""
    for byte in range(1, 5):
        OPCODE += str(ord(byte_1) & (1 << byte))

    AA = "1"
    TC = "0"
    RD = "0"
    RA = "0"
    Z = "000"
    RCODE = "0000"
    return int(QR + OPCODE + AA + TC + RD, 2).to_bytes(byteorder="big") + int(
        RA + Z + RCODE, 2
    ).to_bytes(byteorder="big")


def get_question_domain_type(data):
    domain = ""
    format_error = 0
    state = 0  # 1 = parsing for text labels, 0 = update length of next text to parse
    expected_length = 0
    domain_string = ""
    domain_parts = []
    question_type = None
    x = 0  # count to see if we reach end of subtext to parse
    y = 0  # count number of bytes
    try:
        for byte in data:
            if state == 1:
                if byte != 0:  # domain name not ended so add chars
                    domain_string += chr(byte)
                x += 1
                if x == expected_length:
                    domain_parts.append(domain_string)
                    domain_string = ""
                    state = 0  # ensure that next loop captures the byte length of the next label
                if byte == 0:  # Check if we have reached the end of the question domain
                    domain_parts.append(domain_string)
                    break
            else:
                state = 1
                expected_length = byte
                x = 0
            y += 1
        question_type = data[
            y + 1 : y + 3
        ]  # after the domain the next 2 bytes are question type
        domain = ".".join(domain_parts)
    except IndexError:
        format_error = 1
    finally:
        return domain, question_type


def build_answer(data):
    # Transaction ID
    TransactionID = data[:2]

    # Generate flags
    Flags = generate_flags(data[2:4])

    # Qusetion count
    QDCOUNT = b"\x00\x01"

    # Answer count
    ANCOUNT = b"\x00\x01"

    # NAmeserver count
    NSCOUNT = (0).to_bytes(2, byteorder="big")

    # Additional count
    ADCOUNT = (0).to_bytes(2, byteorder="big")

    # Final header
    dns_header = TransactionID + Flags + QDCOUNT + ANCOUNT + NSCOUNT + ADCOUNT

    domain, type = get_question_domain_type(data[12:])

    dns_question = build_question(domain.split("."))

    # DNS body
    dns_body = b""
    dns_body += rec_to_bytes()
    return dns_header + dns_question + dns_body


def main():
    udp_ip = "127.0.0.1"
    udp_port = 9000

    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((udp_ip, udp_port))
    print("Listening on port 9000...")
    while True:
        try:
            data, addr = udp_socket.recvfrom(1024)  # buffer size is 1024 bytes
            response = build_answer(data=data)
            udp_socket.sendto(response, addr)
        except Exception as ex:
            print(ex)


if __name__ == "__main__":
    main()
